from pymongo import MongoClient
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Establish a connection to the MongoDB database
client = MongoClient("mongodb://localhost:27017/")
db = client["terraform"]
collection = db["issues"]


# Function to generate monthly range
def month_range(start_year, start_month, end_year, end_month):
    start_date = datetime(start_year, start_month, 1)
    end_date = datetime(end_year, end_month, 1)

    while start_date <= end_date:
        yield start_date
        start_date += timedelta(days=31)
        start_date = start_date.replace(day=1)


# Prepare to store the statistics
opened_issues = {}
closed_issues = {}
remaining_open_issues = {}

cumulative_opened = 0
cumulative_closed = 0

for date in month_range(2015, 12, 2024, 2):
    next_month = date + timedelta(days=31)
    next_month = next_month.replace(day=1)
    # MongoDB query to count issues opened each month
    opened_count = collection.count_documents(
        {
            "created_at": {
                "$gte": date.strftime("%Y-%m-%dT00:00:00Z"),
                "$lt": next_month.strftime("%Y-%m-%dT00:00:00Z"),
            }
        }
    )
    cumulative_opened += opened_count
    opened_issues[date.strftime("%Y-%m")] = opened_count

    # MongoDB query to count issues closed each month
    closed_count = collection.count_documents(
        {
            "closed_at": {
                "$gte": date.strftime("%Y-%m-%dT00:00:00Z"),
                "$lt": next_month.strftime("%Y-%m-%dT00:00:00Z"),
            }
        }
    )
    cumulative_closed += closed_count
    closed_issues[date.strftime("%Y-%m")] = closed_count

    # Calculate the remaining open issues
    remaining_open_issues[date.strftime("%Y-%m")] = (
        cumulative_opened - cumulative_closed
    )

# Plotting
plt.figure(figsize=(15, 7))
plt.plot(
    list(opened_issues.keys()),
    list(opened_issues.values()),
    label="Issues Opened",
    marker="o",
)
plt.plot(
    list(closed_issues.keys()),
    list(closed_issues.values()),
    label="Issues Closed",
    marker="o",
)
plt.plot(
    list(remaining_open_issues.keys()),
    list(remaining_open_issues.values()),
    label="Cumulative Remaining Open Issues",
    marker="o",
    linestyle="--",  # Dashed line for cumulative remaining open issues
)

plt.title("Terraform GitHub Enhancement Issues Opened and Closed (2015-2024)")
plt.xlabel("Month")
plt.ylabel("Number of Issues")
plt.xticks(rotation=90)  # Rotate labels to improve readability
plt.legend()
plt.grid(True)
plt.tight_layout()  # Adjust layout to make room for the rotated x-axis labels
plt.show()
