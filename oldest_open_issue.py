from pymongo import MongoClient

# Connect to MongoDB - Adjust the connection string as needed
client = MongoClient("mongodb://localhost:27017/")

# Access the 'terraform' database
db = client.terraform

# Access the 'issues' collection
issues_collection = db.issues

# Find the oldest enhancement issue that's still open
oldest_open_issue = issues_collection.find_one(
    {"state": "open"},  # Query to find open issues
    sort=[("created_at", 1)],  # Sort by creation date in ascending order
)

if oldest_open_issue:
    print("Oldest open issue:")
    print(f"Title: {oldest_open_issue['title']}")
    print(f"Created At: {oldest_open_issue['created_at']}")
    print(f"URL: {oldest_open_issue['html_url']}")
else:
    print("No open issues found.")


# Oldest open enhancement issue:
# Title: Support provisioning using `docker exec`
# Created At: 2016-01-15T03:23:23Z
# URL: https://github.com/hashicorp/terraform/issues/4686
