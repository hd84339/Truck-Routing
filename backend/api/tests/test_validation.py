import json
import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
from django.test import RequestFactory
from api import views

class ApiValidationTests(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
    def test_invalid_interval(self):
        payload = {
            "origin": "Chicago, IL",
            "destination": "Denver, CO",
            "departure": datetime.now(timezone.utc).isoformat(),
            "load_lb": 35000,
            "interval_mi": 99 # invalid interval
        }
        req = self.factory.post('/api/plan', data=json.dumps(payload), content_type='application/json')
        res = views.plan(req)
        self.assertEqual(res.status_code, 400)
        
    def test_past_departure(self):
        payload = {
            "origin": "Chicago, IL",
            "destination": "Denver, CO",
            "departure": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(), # past
            "load_lb": 35000,
            "interval_mi": 25
        }
        req = self.factory.post('/api/plan', data=json.dumps(payload), content_type='application/json')
        res = views.plan(req)
        self.assertEqual(res.status_code, 400)

if __name__ == "__main__":
    unittest.main()
