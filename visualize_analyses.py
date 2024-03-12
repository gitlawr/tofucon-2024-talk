from pymongo import MongoClient
import matplotlib.pyplot as plt
import numpy as np
import re


def camel_case_split(identifier):
    """
    Split a camel case string into a human-readable format.
    """
    matches = re.finditer(
        ".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", identifier
    )
    return " ".join([m.group(0) for m in matches])


# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["terraform"]
collection = db["open_issue_analyses"]

# Count each domain
domain_counts = collection.aggregate(
    [
        {"$unwind": "$domains"},
        {"$group": {"_id": "$domains", "count": {"$sum": 1}}},
        {
            "$sort": {"count": 1}
        },  # Sort by count in ascending order for visual consistency
    ]
)

domain_dict = {}
total_issues = collection.count_documents({})
for domain in domain_counts:
    domain_dict[domain["_id"]] = domain["count"]

# Calculate the ratio of each domain to the total volume of issues and convert to percentage
domain_ratios = {
    domain: (count / total_issues) * 100 for domain, count in domain_dict.items()
}

# Sorting the domain_ratios dictionary by its values (ratios) for plotting
sorted_domains = sorted(domain_ratios.items(), key=lambda x: x[1])

# Plotting
fig, ax = plt.subplots(figsize=(10, 8))  # Adjusted figure size for better visibility
domains = [
    camel_case_split(item[0]) for item in sorted_domains
]  # Convert domain names to human-readable format
ratios = [item[1] for item in sorted_domains]

# Generate a color map
colors = plt.cm.viridis(np.linspace(0, 1, len(domains)))

ax.barh(domains, ratios, color=colors)
plt.xlabel("Percentage of Open Issues")
plt.ylabel("Domains")
plt.title("Percentage of Open Issues by Domain")
plt.tight_layout()  # Automatically adjust subplot parameters to give specified padding

# Increase font size for y-axis labels for better readability
plt.yticks(fontsize=10)  # Adjust font size as needed

# Add the data value on each bar
for index, value in enumerate(ratios):
    plt.text(value, index, f"{value:.2f}%", va="center")

# Adjust x-axis to extend up to 60
plt.xlim(0, 60)

plt.show()
