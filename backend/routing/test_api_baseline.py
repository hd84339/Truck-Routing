import json
import unittest
from unittest.mock import patch
from datetime import datetime, timezone, timedelta
import os
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        TRUCK_TIME_FACTOR=1.1,
        ROOT_URLCONF='',
        DEBUG=True
    )
django.setup()

from django.test import RequestFactory
from routing import views

class ApiBaselineTests(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.mock_origin = {"lat": 41.8781, "lng": -87.6298, "name": "Chicago, IL"}
        self.mock_dest = {"lat": 39.7392, "lng": -104.9903, "name": "Denver, CO"}
        self.mock_route = {
            "distance_mi": 1000.0,
            "duration_h": 15.0,
            "geometry": [(41.8, -87.6), (39.7, -104.9)]
        }

    @patch('weather.services.fetch_weather')
    @patch('routing.services.get_routes')
    @patch('routing.services.geocode')
    def test_plan_success(self, mock_geocode, mock_get_routes, mock_fetch_weather):
        mock_geocode.side_effect = [self.mock_origin, self.mock_dest]
        mock_get_routes.return_value = [self.mock_route]
        
        def dummy_weather(points):
            now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
            return [{
                "start": now,
                "wind": [10.0] * 50,
                "rain": [0.0] * 50,
                "snow": [0.0] * 50
            } for _ in points]
        mock_fetch_weather.side_effect = dummy_weather

        payload = {
            "origin": "Chicago, IL",
            "destination": "Denver, CO",
            "departure": datetime.now(timezone.utc).isoformat(),
            "load_lb": 35000,
            "interval_mi": 25
        }
        
        req = self.factory.post('/api/plan', data=json.dumps(payload), content_type='application/json')
        res = views.plan(req)
        
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        
        self.assertIn('origin', data)
        self.assertIn('destination', data)
        self.assertIn('routes', data)
        self.assertIn('recommended', data)
        self.assertIn('explanation', data)
        
        self.assertEqual(data['origin']['name'], "Chicago, IL")
        self.assertEqual(data['destination']['name'], "Denver, CO")
        self.assertEqual(len(data['routes']), 1)
        
        route = data['routes'][0]
        self.assertIn('id', route)
        self.assertIn('summary', route)
        self.assertIn('geometry', route)
        self.assertIn('checkpoints', route)

if __name__ == '__main__':
    unittest.main()
