#!/usr/bin/env python3
"""
Recommendation Engine
Collaborative filtering and content-based recommendation system.
Author: Gabriel Demetrios Lafis
"""

import math
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple


class CollaborativeFilter:
    """User-based and item-based collaborative filtering recommendation engine."""

    def __init__(self):
        self.user_ratings: Dict[str, Dict[str, float]] = {}
        self.item_users: Dict[str, Set[str]] = defaultdict(set)

    def add_rating(self, user_id: str, item_id: str, rating: float) -> None:
        """Add or update a user rating for an item."""
        rating = max(0.0, min(5.0, rating))
        if user_id not in self.user_ratings:
            self.user_ratings[user_id] = {}
        self.user_ratings[user_id][item_id] = rating
        self.item_users[item_id].add(user_id)

    def add_ratings_bulk(self, ratings: List[Tuple[str, str, float]]) -> int:
        """Add multiple ratings at once. Returns count of ratings added."""
        for user_id, item_id, rating in ratings:
            self.add_rating(user_id, item_id, rating)
        return len(ratings)

    def _cosine_similarity(self, user_a: str, user_b: str) -> float:
        """Compute cosine similarity between two users."""
        if user_a not in self.user_ratings or user_b not in self.user_ratings:
            return 0.0

        ratings_a = self.user_ratings[user_a]
        ratings_b = self.user_ratings[user_b]
        common_items = set(ratings_a.keys()) & set(ratings_b.keys())

        if not common_items:
            return 0.0

        dot_product = sum(ratings_a[item] * ratings_b[item] for item in common_items)
        norm_a = math.sqrt(sum(r ** 2 for r in ratings_a.values()))
        norm_b = math.sqrt(sum(r ** 2 for r in ratings_b.values()))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def _pearson_correlation(self, user_a: str, user_b: str) -> float:
        """Compute Pearson correlation between two users."""
        if user_a not in self.user_ratings or user_b not in self.user_ratings:
            return 0.0

        ratings_a = self.user_ratings[user_a]
        ratings_b = self.user_ratings[user_b]
        common_items = set(ratings_a.keys()) & set(ratings_b.keys())

        n = len(common_items)
        if n < 2:
            return 0.0

        sum_a = sum(ratings_a[item] for item in common_items)
        sum_b = sum(ratings_b[item] for item in common_items)
        sum_a2 = sum(ratings_a[item] ** 2 for item in common_items)
        sum_b2 = sum(ratings_b[item] ** 2 for item in common_items)
        sum_ab = sum(ratings_a[item] * ratings_b[item] for item in common_items)

        numerator = n * sum_ab - sum_a * sum_b
        denominator = math.sqrt(
            (n * sum_a2 - sum_a ** 2) * (n * sum_b2 - sum_b ** 2)
        )

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def find_similar_users(
        self, user_id: str, k: int = 5, method: str = "cosine"
    ) -> List[Tuple[str, float]]:
        """Find the k most similar users."""
        if user_id not in self.user_ratings:
            return []

        similarity_fn = (
            self._cosine_similarity if method == "cosine" else self._pearson_correlation
        )
        similarities = []

        for other_user in self.user_ratings:
            if other_user != user_id:
                sim = similarity_fn(user_id, other_user)
                if sim > 0:
                    similarities.append((other_user, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]

    def recommend_items(
        self,
        user_id: str,
        k: int = 10,
        n_neighbors: int = 5,
        method: str = "cosine",
    ) -> List[Tuple[str, float]]:
        """Recommend items for a user based on similar users' preferences."""
        if user_id not in self.user_ratings:
            return []

        similar_users = self.find_similar_users(user_id, n_neighbors, method)
        if not similar_users:
            return []

        user_items = set(self.user_ratings[user_id].keys())
        scores: Dict[str, float] = defaultdict(float)
        sim_sums: Dict[str, float] = defaultdict(float)

        for neighbor, similarity in similar_users:
            for item, rating in self.user_ratings[neighbor].items():
                if item not in user_items:
                    scores[item] += similarity * rating
                    sim_sums[item] += similarity

        recommendations = []
        for item in scores:
            if sim_sums[item] > 0:
                predicted_score = scores[item] / sim_sums[item]
                recommendations.append((item, round(predicted_score, 3)))

        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:k]

    def get_stats(self) -> Dict:
        """Return engine statistics."""
        total_ratings = sum(len(r) for r in self.user_ratings.values())
        return {
            "total_users": len(self.user_ratings),
            "total_items": len(self.item_users),
            "total_ratings": total_ratings,
            "avg_ratings_per_user": (
                round(total_ratings / len(self.user_ratings), 2)
                if self.user_ratings
                else 0
            ),
        }


class ContentBasedFilter:
    """Content-based recommendation using item feature vectors."""

    def __init__(self):
        self.item_features: Dict[str, Dict[str, float]] = {}
        self.user_profiles: Dict[str, Dict[str, float]] = {}
        self.user_ratings: Dict[str, Dict[str, float]] = {}

    def add_item(self, item_id: str, features: Dict[str, float]) -> None:
        """Register an item with its feature vector."""
        norm = math.sqrt(sum(v ** 2 for v in features.values()))
        if norm > 0:
            self.item_features[item_id] = {k: v / norm for k, v in features.items()}
        else:
            self.item_features[item_id] = features

    def add_user_rating(self, user_id: str, item_id: str, rating: float) -> None:
        """Record a user rating and update the user profile."""
        if user_id not in self.user_ratings:
            self.user_ratings[user_id] = {}
        self.user_ratings[user_id][item_id] = rating
        self._update_user_profile(user_id)

    def _update_user_profile(self, user_id: str) -> None:
        """Recompute user profile as weighted average of rated item features."""
        profile: Dict[str, float] = defaultdict(float)
        total_weight = 0.0

        for item_id, rating in self.user_ratings[user_id].items():
            if item_id in self.item_features:
                weight = rating
                total_weight += weight
                for feature, value in self.item_features[item_id].items():
                    profile[feature] += value * weight

        if total_weight > 0:
            self.user_profiles[user_id] = {
                k: v / total_weight for k, v in profile.items()
            }

    def _cosine_similarity(
        self, vec_a: Dict[str, float], vec_b: Dict[str, float]
    ) -> float:
        """Compute cosine similarity between two feature vectors."""
        common_keys = set(vec_a.keys()) & set(vec_b.keys())
        if not common_keys:
            return 0.0

        dot = sum(vec_a[k] * vec_b[k] for k in common_keys)
        norm_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
        norm_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def recommend_items(
        self, user_id: str, k: int = 10
    ) -> List[Tuple[str, float]]:
        """Recommend items based on user profile similarity to item features."""
        if user_id not in self.user_profiles:
            return []

        user_profile = self.user_profiles[user_id]
        rated_items = set(self.user_ratings.get(user_id, {}).keys())
        scores = []

        for item_id, features in self.item_features.items():
            if item_id not in rated_items:
                sim = self._cosine_similarity(user_profile, features)
                if sim > 0:
                    scores.append((item_id, round(sim, 3)))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k]

    def find_similar_items(
        self, item_id: str, k: int = 5
    ) -> List[Tuple[str, float]]:
        """Find items most similar to a given item."""
        if item_id not in self.item_features:
            return []

        target_features = self.item_features[item_id]
        similarities = []

        for other_id, features in self.item_features.items():
            if other_id != item_id:
                sim = self._cosine_similarity(target_features, features)
                if sim > 0:
                    similarities.append((other_id, round(sim, 3)))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]

    def get_stats(self) -> Dict:
        """Return engine statistics."""
        return {
            "total_items": len(self.item_features),
            "total_users": len(self.user_profiles),
            "total_ratings": sum(len(r) for r in self.user_ratings.values()),
        }


class HybridRecommender:
    """Hybrid recommender combining collaborative and content-based filtering."""

    def __init__(self, cf_weight: float = 0.5):
        self.collaborative = CollaborativeFilter()
        self.content_based = ContentBasedFilter()
        self.cf_weight = cf_weight
        self.cb_weight = 1.0 - cf_weight

    def add_item(self, item_id: str, features: Dict[str, float]) -> None:
        """Add item features for content-based filtering."""
        self.content_based.add_item(item_id, features)

    def add_rating(self, user_id: str, item_id: str, rating: float) -> None:
        """Add a rating for both collaborative and content-based engines."""
        self.collaborative.add_rating(user_id, item_id, rating)
        self.content_based.add_user_rating(user_id, item_id, rating)

    def recommend(
        self, user_id: str, k: int = 10
    ) -> List[Tuple[str, float]]:
        """Generate hybrid recommendations."""
        cf_recs = dict(self.collaborative.recommend_items(user_id, k=k * 2))
        cb_recs = dict(self.content_based.recommend_items(user_id, k=k * 2))

        all_items = set(cf_recs.keys()) | set(cb_recs.keys())
        hybrid_scores = []

        for item in all_items:
            cf_score = cf_recs.get(item, 0.0)
            cb_score = cb_recs.get(item, 0.0)
            combined = self.cf_weight * cf_score + self.cb_weight * cb_score
            hybrid_scores.append((item, round(combined, 3)))

        hybrid_scores.sort(key=lambda x: x[1], reverse=True)
        return hybrid_scores[:k]

    def get_stats(self) -> Dict:
        """Return combined statistics."""
        return {
            "collaborative": self.collaborative.get_stats(),
            "content_based": self.content_based.get_stats(),
            "cf_weight": self.cf_weight,
            "cb_weight": self.cb_weight,
        }


# --- Demo ---
def demo():
    """Demonstrate the recommendation engine."""
    engine = HybridRecommender(cf_weight=0.6)

    # Add items with features
    items = {
        "movie_1": {"action": 0.9, "comedy": 0.2, "drama": 0.1},
        "movie_2": {"action": 0.1, "comedy": 0.8, "drama": 0.3},
        "movie_3": {"action": 0.7, "comedy": 0.1, "drama": 0.6},
        "movie_4": {"action": 0.2, "comedy": 0.9, "drama": 0.1},
        "movie_5": {"action": 0.8, "comedy": 0.3, "drama": 0.5},
        "movie_6": {"action": 0.1, "comedy": 0.2, "drama": 0.9},
    }
    for item_id, features in items.items():
        engine.add_item(item_id, features)

    # Add user ratings
    ratings = [
        ("user_1", "movie_1", 5.0), ("user_1", "movie_3", 4.0),
        ("user_1", "movie_5", 4.5),
        ("user_2", "movie_2", 5.0), ("user_2", "movie_4", 4.5),
        ("user_2", "movie_6", 3.0),
        ("user_3", "movie_1", 4.0), ("user_3", "movie_2", 3.0),
        ("user_3", "movie_3", 5.0), ("user_3", "movie_5", 4.0),
    ]
    for user_id, item_id, rating in ratings:
        engine.add_rating(user_id, item_id, rating)

    # Get recommendations
    print("Recommendations for user_1:")
    for item, score in engine.recommend("user_1"):
        print(f"  {item}: {score}")

    print("\nEngine stats:", engine.get_stats())


if __name__ == "__main__":
    demo()
