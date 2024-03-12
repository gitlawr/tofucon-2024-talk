from pymongo import MongoClient

# Establish a connection to the MongoDB instance
client = MongoClient("mongodb://localhost:27017/")

# Select the 'terraform' database and the 'issues' collection
db = client["terraform"]
issues_collection = db["issues"]

# Query to find the open issue with the most "+1" reactions
query = {"state": "open"}
projection = {"title": 1, "html_url": 1, "reactions.+1": 1, "created_at": 1}
most_positive_issue = issues_collection.find_one(
    query, projection, sort=[("reactions.+1", -1)]
)

# Check if we found an issue and print the result
if most_positive_issue:
    print(f"Issue Title: {most_positive_issue['title']}")
    print(f"HTML URL: {most_positive_issue['html_url']}")
    print(f"+1 Reactions: {most_positive_issue['reactions']['+1']}")
    print(f"Created At: {most_positive_issue['created_at']}")
else:
    print("No open issues with '+1' reactions found.")


# Issue Title: Using variables in terraform backend config block
# HTML URL: https://github.com/hashicorp/terraform/issues/13022
# +1 Reactions: 1035
# Created At: 2017-03-23T20:06:56Z
