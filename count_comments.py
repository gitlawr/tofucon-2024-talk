from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["terraform"]
collection = db["issues"]

pipeline = [
    {"$group": {"_id": None, "totalComments": {"$sum": {"$size": "$comments"}}}}
]

result = list(collection.aggregate(pipeline))

if result:
    print("Total comments:", result[0]["totalComments"])
else:
    print("No data found")

# Total comments: 19782
