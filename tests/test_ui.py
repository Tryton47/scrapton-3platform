"""
Unit tests for UI analytics and session helpers.
"""
import unittest
import pandas as pd
from ui.analytics import prepare_chart_dataframe, get_metric_summary
from ui.session_helper import get_session_status

class TestUIHelpers(unittest.TestCase):

    def test_session_status_keys(self):
        status = get_session_status()
        self.assertIn("instagram", status)
        self.assertIn("tiktok", status)
        self.assertIn("twitter", status)

    def test_metric_summary_calculation(self):
        df = pd.DataFrame([
            {"metrics_likes": 100, "metrics_comments": 20, "metrics_views": 1000},
            {"metrics_likes": 250, "metrics_comments": 30, "metrics_views": 2500},
        ])
        summary = get_metric_summary(df)
        self.assertEqual(summary["total_likes"], 350)
        self.assertEqual(summary["total_comments"], 50)
        self.assertEqual(summary["total_views"], 3500)

    def test_prepare_chart_dataframe(self):
        df = pd.DataFrame([
            {"id": "111", "metrics_likes": 50, "metrics_views": 500},
            {"id": "222", "metrics_likes": 80, "metrics_views": 800},
        ])
        chart_df = prepare_chart_dataframe(df)
        self.assertIsNotNone(chart_df)
        self.assertEqual(len(chart_df), 2)
        self.assertIn("metrics_likes", chart_df.columns)

if __name__ == "__main__":
    unittest.main()
