from pymongo import MongoClient
from textblob import TextBlob
import matplotlib.pyplot as plt

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.terraform
issues_collection = db.issues

# Fetch open issues
open_issues = issues_collection.find({"state": "open"})

# Initialize counters and lists for sentiment categories
positive_count = 0
negative_count = 0
neutral_count = 0
negative_issues = []  # List to store issue numbers of negative issues

for issue in open_issues:
    # Initial sentiment score for the issue based on title and body
    title_blob = TextBlob(issue["title"])
    body_blob = TextBlob(issue["body"])
    sentiment_score = title_blob.sentiment.polarity + body_blob.sentiment.polarity

    # Analyze sentiment for comments
    for comment in issue["comments"]:
        comment_blob = TextBlob(comment["body"])
        sentiment_score += comment_blob.sentiment.polarity

    # Average sentiment score for the issue
    elements_count = len(issue["comments"]) + 2  # +2 for the title and body
    average_sentiment = sentiment_score / elements_count

    # Categorize the issue based on the average sentiment
    if average_sentiment > 0:
        positive_count += 1
    elif average_sentiment < 0:
        negative_count += 1
        negative_issues.append(
            issue["number"]
        )  # Add issue number to the negative_issues list
    else:
        neutral_count += 1

# Plotting the results
labels = ["Positive", "Negative", "Neutral"]
sizes = [positive_count, negative_count, neutral_count]
colors = ["lightgreen", "lightcoral", "lightgrey"]
explode = (0.1, 0.1, 0.1)  # explode all slices for better visibility

plt.pie(
    sizes,
    explode=explode,
    labels=labels,
    colors=colors,
    autopct="%1.1f%%",
    shadow=True,
    startangle=140,
)
plt.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.title("Sentiment Analysis of Open Issues")
plt.show()

# Output the list of issue numbers for negative issues
print("Issue Numbers of Negative Issues:", negative_issues)

# Issue Numbers of Negative Issues: [10912, 10454, 8811, 8014, 7414, 7190, 5667, 16829, 16698, 16651, 16494, 16459, 16222, 15761, 15434, 15373, 15103, 14804, 14050, 19679, 19488, 19444, 18852, 18769, 18741, 18383, 18325, 18070, 18001, 17774, 17724, 17505, 17067, 23735, 23580, 23552, 23512, 23388, 23368, 23361, 23331, 23239, 23167, 22969, 22955, 22785, 22739, 22661, 22648, 22633, 22595, 22549, 22479, 22393, 22204, 22093, 21777, 21617, 21512, 21430, 21231, 21163, 21086, 20744, 20658, 20344, 20114, 20059, 20006, 27369, 27291, 27126, 27043, 26864, 26823, 26781, 26496, 26438, 26408, 26261, 26164, 25776, 25754, 25704, 25697, 25575, 25538, 25488, 25390, 25382, 25316, 25118, 25051, 25039, 24991, 24981, 24961, 24936, 24905, 24812, 24692, 24663, 24658, 24645, 24573, 24391, 24324, 24222, 24217, 24059, 24006, 23960, 23846, 30143, 30079, 29806, 29724, 29679, 29345, 29019, 29007, 28991, 28970, 28938, 28898, 28879, 28614, 28451, 28218, 28077, 28003, 27984, 27953, 27875, 27811, 27802, 27778, 27618, 27558, 27532, 27459, 32439, 32384, 32319, 32148, 32013, 32012, 31968, 31888, 31836, 31833, 31645, 31439, 31414, 31363, 31309, 31305, 31072, 30633, 30524, 34461, 34424, 34379, 34327, 34242, 34211, 34203, 34146, 34010, 33908, 33712, 33651, 33449, 33277, 33216, 33137, 33105, 33067, 32748, 32593, 32505, 34760, 34757, 34711, 34710, 34627, 34612]
