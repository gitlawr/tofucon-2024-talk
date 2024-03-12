import requests
from pymongo import MongoClient
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}


client = MongoClient("mongodb://localhost:27017/")
db = client["terraform"]
issues_collection = db["issues"]

closed_issues = issues_collection.find({"state": "closed"})

cont = True
for issue in closed_issues:
    issue_number = issue["number"]
    if issue_number == 27581:
        cont = False
    if cont:
        continue
    url = (
        f"https://api.github.com/repos/hashicorp/terraform/issues/{issue_number}/events"
    )
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(
            f"failed to request GitHub API, status code：{response.status_code}, issue number：{issue_number}"
        )
        continue

    events = response.json()

    close_reason = "completed"  # default
    for event in events:
        if event["event"] == "closed" and "state_reason" in event:
            close_reason = (
                event["state_reason"]
                if event["state_reason"] is not None
                else "completed"
            )
            break

    issues_collection.update_one(
        {"_id": issue["_id"]}, {"$set": {"close_reason": close_reason}}
    )
    print(f"updated issue {issue_number} with close reason: {close_reason}")

print("All issues updated.")
