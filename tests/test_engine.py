"""Tests for Recommendation Engine. Author: Gabriel Demetrios Lafis"""
import unittest
from engine import CollaborativeFilter, ContentBasedFilter, HybridRecommender


class TestCollaborativeFilter(unittest.TestCase):
    def setUp(self):
        self.cf = CollaborativeFilter()
        self.cf.add_rating("u1", "i1", 5.0)
        self.cf.add_rating("u1", "i2", 3.0)
        self.cf.add_rating("u2", "i1", 4.0)
        self.cf.add_rating("u2", "i3", 5.0)
        self.cf.add_rating("u3", "i1", 5.0)
        self.cf.add_rating("u3", "i2", 4.0)
        self.cf.add_rating("u3", "i3", 3.0)

    def test_add_rating(self):
        self.assertEqual(self.cf.user_ratings["u1"]["i1"], 5.0)

    def test_rating_clamped(self):
        self.cf.add_rating("u1", "i4", 10.0)
        self.assertEqual(self.cf.user_ratings["u1"]["i4"], 5.0)

    def test_find_similar_users(self):
        similar = self.cf.find_similar_users("u1", k=2)
        self.assertGreater(len(similar), 0)
        self.assertIsInstance(similar[0][1], float)

    def test_recommend_items(self):
        recs = self.cf.recommend_items("u1", k=5)
        item_ids = [r[0] for r in recs]
        self.assertIn("i3", item_ids)

    def test_recommend_unknown_user(self):
        recs = self.cf.recommend_items("unknown", k=5)
        self.assertEqual(recs, [])

    def test_stats(self):
        stats = self.cf.get_stats()
        self.assertEqual(stats["total_users"], 3)


class TestContentBasedFilter(unittest.TestCase):
    def setUp(self):
        self.cb = ContentBasedFilter()
        self.cb.add_item("i1", {"a": 0.9, "b": 0.1})
        self.cb.add_item("i2", {"a": 0.1, "b": 0.9})
        self.cb.add_item("i3", {"a": 0.8, "b": 0.2})
        self.cb.add_user_rating("u1", "i1", 5.0)

    def test_recommend(self):
        recs = self.cb.recommend_items("u1", k=5)
        self.assertGreater(len(recs), 0)

    def test_similar_items(self):
        similar = self.cb.find_similar_items("i1", k=2)
        self.assertEqual(similar[0][0], "i3")


class TestHybridRecommender(unittest.TestCase):
    def setUp(self):
        self.hr = HybridRecommender(cf_weight=0.5)
        self.hr.add_item("i1", {"x": 1.0})
        self.hr.add_item("i2", {"y": 1.0})
        self.hr.add_item("i3", {"x": 0.8, "y": 0.2})
        self.hr.add_rating("u1", "i1", 5.0)
        self.hr.add_rating("u2", "i1", 4.0)
        self.hr.add_rating("u2", "i2", 5.0)

    def test_recommend(self):
        recs = self.hr.recommend("u1", k=5)
        self.assertIsInstance(recs, list)

    def test_stats(self):
        stats = self.hr.get_stats()
        self.assertIn("collaborative", stats)
        self.assertIn("content_based", stats)


if __name__ == "__main__":
    unittest.main()
