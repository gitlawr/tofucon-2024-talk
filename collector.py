import requests
from pymongo import MongoClient
import os

# GitHub token and MongoDB URI loaded from environment variables for security
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def fetch_issue_urls(repo_owner, repo_name):
    query = f"label:enhancement,proposal+-label:duplicate,documentation+repo:{repo_owner}/{repo_name}+is:issue"
    non_range_url = f"https://api.github.com/search/issues?per_page=100&q={query}"

    issue_urls = []
    for year in range(2016, 2025):
        url = non_range_url + f"+created:{year}-01-01..{year}-12-31"
        while url:
            response = requests.get(url, headers=headers)
            if response.status_code == 403:
                print(f"Rate limit hit. Request URL: {url}")
                break
            elif response.status_code != 200:
                raise Exception(
                    f"GitHub API request failed with status code {response.status_code}"
                )
            data = response.json()
            issue_urls.extend([issue["html_url"] for issue in data["items"]])

            # Pagination handling
            url = None
            if "next" in response.links:
                url = response.links["next"]["url"]
    return issue_urls


def fetch_all_pages(url):
    all_data = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 403:
            print(f"Rate limit hit. Request URL: {url}")
            return all_data
        elif response.status_code != 200:
            raise Exception(
                f"GitHub API request failed with status code {response.status_code}"
            )
        all_data.extend(response.json())

        url = None
        if "next" in response.links:
            url = response.links["next"]["url"]
    return all_data


def fetch_issue_data_and_comments(issue_url):
    issue_response = requests.get(issue_url, headers=headers)
    if issue_response.status_code == 403:
        print(f"Rate limit hit. Request URL: {issue_url}")
        return None
    elif issue_response.status_code != 200:
        raise Exception(
            f"GitHub API request failed with status code {issue_response.status_code}"
        )
    issue_data = issue_response.json()

    comments_url = issue_data.get("comments_url", "")
    comments_data = fetch_all_pages(comments_url)

    document = issue_data
    document["comments"] = comments_data

    return document


def insert_into_mongodb(document, db_name="terraform", collection_name="issues"):
    client = MongoClient(MONGODB_URI)
    db = client[db_name]
    collection = db[collection_name]
    collection.insert_one(document)


def get_urls_from_mongodb(db_name="terraform", collection_name="issue_urls"):
    client = MongoClient(MONGODB_URI)
    db = client[db_name]
    collection = db[collection_name]
    document = collection.find_one()
    client.close()

    return document["urls"] if document and "urls" in document else []


def main(repo_owner, repo_name):
    issue_urls = get_urls_from_mongodb()
    if not issue_urls:
        issue_urls = fetch_issue_urls(repo_owner, repo_name)
        insert_into_mongodb({"urls": issue_urls}, collection_name="issue_urls")

    for issue_url in issue_urls:
        issue_data = fetch_issue_data_and_comments(
            issue_url.replace("https://github.com", "https://api.github.com/repos")
        )
        if issue_data:
            insert_into_mongodb(issue_data)
            print(f"Issue {issue_data['id']} inserted into MongoDB.")


if __name__ == "__main__":
    repo_owner = "hashicorp"
    repo_name = "terraform"
    main(repo_owner, repo_name)
