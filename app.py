#!/usr/bin/env python3
"""
Recommendation Engine - REST API
Flask API exposing collaborative and content-based recommendation.
Author: Gabriel Demetrios Lafis
"""

from flask import Flask, request, jsonify
from engine import CollaborativeFilter, ContentBasedFilter, HybridRecommender

app = Flask(__name__)

# Initialize engines
hybrid = HybridRecommender(cf_weight=0.6)

# Pre-load demo data
_demo_items = {
    "item_1": {"action": 0.9, "comedy": 0.2, "drama": 0.1, "scifi": 0.7},
    "item_2": {"action": 0.1, "comedy": 0.8, "drama": 0.3, "scifi": 0.1},
    "item_3": {"action": 0.7, "comedy": 0.1, "drama": 0.6, "scifi": 0.5},
    "item_4": {"action": 0.2, "comedy": 0.9, "drama": 0.1, "scifi": 0.0},
    "item_5": {"action": 0.8, "comedy": 0.3, "drama": 0.5, "scifi": 0.8},
}
for _id, _feat in _demo_items.items():
    hybrid.add_item(_id, _feat)

_demo_ratings = [
    ("user_1", "item_1", 5.0), ("user_1", "item_3", 4.0),
    ("user_2", "item_2", 5.0), ("user_2", "item_4", 4.5),
    ("user_3", "item_1", 4.0), ("user_3", "item_2", 3.0),
    ("user_3", "item_3", 5.0),
]
for _u, _i, _r in _demo_ratings:
    hybrid.add_rating(_u, _i, _r)


@app.route("/")
def index():
    return jsonify({
        "name": "Recommendation Engine API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/ratings": "Add a user rating",
            "POST /api/items": "Add an item with features",
            "GET /api/recommend/<user_id>": "Get recommendations for a user",
            "GET /api/similar/<item_id>": "Find similar items",
            "GET /api/stats": "Engine statistics",
        },
    })


@app.route("/api/ratings", methods=["POST"])
def add_rating():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    item_id = data.get("item_id")
    rating = data.get("rating")

    if not all([user_id, item_id, rating is not None]):
        return jsonify({"error": "user_id, item_id, and rating are required"}), 400

    hybrid.add_rating(str(user_id), str(item_id), float(rating))
    return jsonify({"message": "Rating added", "user_id": user_id, "item_id": item_id})


@app.route("/api/items", methods=["POST"])
def add_item():
    data = request.get_json() or {}
    item_id = data.get("item_id")
    features = data.get("features")

    if not item_id or not features:
        return jsonify({"error": "item_id and features are required"}), 400

    hybrid.add_item(str(item_id), features)
    return jsonify({"message": "Item added", "item_id": item_id})


@app.route("/api/recommend/<user_id>")
def recommend(user_id):
    k = request.args.get("k", 10, type=int)
    recs = hybrid.recommend(user_id, k=k)
    return jsonify({
        "user_id": user_id,
        "recommendations": [{"item_id": item, "score": score} for item, score in recs],
    })


@app.route("/api/similar/<item_id>")
def similar_items(item_id):
    k = request.args.get("k", 5, type=int)
    items = hybrid.content_based.find_similar_items(item_id, k=k)
    return jsonify({
        "item_id": item_id,
        "similar_items": [{"item_id": i, "similarity": s} for i, s in items],
    })


@app.route("/api/stats")
def stats():
    return jsonify(hybrid.get_stats())


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
