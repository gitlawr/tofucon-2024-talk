from pymongo import MongoClient
from datetime import datetime
import json

client = MongoClient("mongodb://localhost:27017/")
db = client.terraform
issues_collection = db.issues
issue_analyses_collection = (
    db.open_issue_analyses
)  # Collection for saving issue analyses


def generate_open_issue_prompts():
    open_issues = issues_collection.find({"state": "open"})

    prompts = []  # List to store prompts and issue numbers
    for issue in open_issues:
        prompt = {"text": "", "number": issue["number"], "title": issue["title"]}
        prompt_text = ""
        prompt_text += f"Issue Title: {issue['title']}\n"
        prompt_text += f"Created At: {datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')}\n"
        prompt_text += f"Creator: {issue['user']['login']}\n"
        prompt_text += "Body:\n" + issue["body"] + "\n"
        prompt_text += "Comments:\n"
        if issue.get("comments"):
            for comment in issue["comments"]:
                if comment["user"]["login"] == "ghost":
                    continue
                prompt_text += "---\n"
                prompt_text += f"Creator: {comment['user']['login']}\n"
                prompt_text += f"Created At: {datetime.strptime(comment['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')}\n"
                prompt_text += f"Body: {comment['body']}\n"
            prompt_text += "---"
        else:
            prompt_text += "---\nNo comments available.\n---"
        prompt["text"] = prompt_text
        prompts.append(prompt)
    return prompts


# Call the function and store its return value
open_issue_prompts = generate_open_issue_prompts()

# For demonstration, printing the first prompt from the list
if open_issue_prompts:
    print(open_issue_prompts[0])
else:
    print("No open issues found.")


from openai import OpenAI

SYSTEM_PROMPT = """
You are an assistant help to analyze open enhancement issues of the Terraform GitHub repository.
Given the issue title, creator, creation date, body, and comments, summary the domains of the issue, and do sentiment analysis.
Output a valid JSON in the following format:
Example Output:

{
    "domains": ["example_domain"],
    "sentiment": "positive"
}

End of example output.

"sentiment" should be any of "positive", "neutral" or "negative".
"domains" should be a list of the following:
ConfigurationLanguageAndSyntax: Issues related to the syntax of the Terraform configuration language (HCL), including requests for new features, syntax simplifications, and improvements in error message clarity.
StateManagement: Concerns about handling the state file, enhancing state locking and state storage mechanisms, and providing better tools for state migration.
ModulesAndResources: Improvements to the Terraform module system, management of resource dependencies, and ease of module reuse and sharing.
ProvidersAndPlatformSupport: Expanding and enhancing support for different cloud providers and services, improving coverage of existing provider resources, and adding new providers.
PerformanceAndScalability: Focused on increasing the efficiency of Terraform operations, reducing performance bottlenecks in large-scale deployments, and improving support for concurrent operations.
UIUX: Improvements to Terraform's command-line interface (CLI) and graphical interfaces (GUI), including user interactions, visualization tools, and error handling enhancements.
SecurityAndCompliance: Enhancements to the security of infrastructure managed by Terraform, increased support for security best practices, and integration of compliance checks and reporting.
IntegrationAndToolchain: Improvements in integrating Terraform with other development and operations tools (such as version control systems, CI/CD pipelines, and monitoring tools).
DocumentationAndTutorial: Enhancing the availability and accuracy of official documentation, providing more tutorials and examples, and expanding community knowledge bases and learning resources.
"""


def analyse_issue(prompt):
    client = OpenAI()

    try:
        response = client.chat.completions.create(
            model="gpt-4-0125-preview",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        result = response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")

    return result


# Example usage
open_issue_prompts = (
    generate_open_issue_prompts()
)  # Assuming this function is defined and returns prompts


for prompt in open_issue_prompts:
    analysis_result = analyse_issue(prompt["text"])
    analysis_data = json.loads(analysis_result)

    document = {
        "number": prompt["number"],
        "title": prompt["title"],
        **analysis_data,
    }

    issue_analyses_collection.insert_one(document)

    print(f"Analysis of issue {prompt['number']} saved to the database.")
    print(document)
