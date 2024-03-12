from pymongo import MongoClient
import matplotlib.pyplot as plt

# Establish a connection to the MongoDB database
client = MongoClient("mongodb://localhost:27017/")
db = client["terraform"]
collection = db["issues"]

# Prepare to store the statistics
years = range(2015, 2025)
opened_issues = {}
closed_issues = {}

for year in years:
    # MongoDB query to count issues opened each year
    opened_count = collection.count_documents(
        {
            "created_at": {
                "$gte": f"{year}-01-01T00:00:00Z",
                "$lt": f"{year+1}-01-01T00:00:00Z",
            }
        }
    )
    opened_issues[year] = opened_count

    # MongoDB query to count issues closed each year
    closed_count = collection.count_documents(
        {
            "closed_at": {
                "$gte": f"{year}-01-01T00:00:00Z",
                "$lt": f"{year+1}-01-01T00:00:00Z",
            }
        }
    )
    closed_issues[year] = closed_count

# Plotting
plt.figure(figsize=(10, 5))
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

plt.title("Terraform GitHub Enhancement Issues Opened and Closed (2015-2024)")
plt.xlabel("Year")
plt.ylabel("Number of Issues")
plt.xticks(list(years))
plt.legend()
plt.grid(True)
plt.show()
