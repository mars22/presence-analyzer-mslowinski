# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
from __future__ import unicode_literals

import os.path
import json
import datetime
import time
import unittest
from functools import partial

from presence_analyzer import main, views, utils


class PresenceAnalyzerTestCase(unittest.TestCase):
    """
    Base class for Presence Analyzer tests.
    """
    def setUp(self):
        """
        Before each test, set up a environment.
        """
        runtime_data = partial(os.path.join, 'runtime', 'data')
        main.app.config.update({
            'DATA_CSV': runtime_data('test_data.csv'),
            'USERS_XML': runtime_data('test_users.xml'),
        })


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerViewsTestCase(PresenceAnalyzerTestCase):
    """
    Views tests.
    """
    def setUp(self):
        """
        Before each test, set up a environment.
        """
        super(PresenceAnalyzerViewsTestCase, self).setUp()
        self.client = main.app.test_client()

    def endpoint_should_return_404(self, url):
        """
        Asserts that endpoint return 404.
        """
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def endpoint_return_json_data(self, url):
        """
        Asserts that endpoint returns json data then deserialize and return it.
        """
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        return json.loads(resp.data)

    def test_render_page(self):
        """
        Test render page by template name.
        """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'text/html; charset=utf-8')

        self.endpoint_should_return_404("/not_existing")

    def test_api_users(self):
        """
        Test users listing.
        """
        data = self.endpoint_return_json_data('/api/v1/users')
        self.assertEqual(len(data), 3)
        self.assertDictEqual(
            data[0],
            {
                'user_id': 10,
                'name': 'Maciej Z.',
                'avatar_url': 'https://intranet.stxnext.pl:443'
                              '/api/images/users/10',
            }
        )

    def test_api_start_end(self):
        """
        Test mean start and end presence of user per day.
        """
        data = self.endpoint_return_json_data(
            '/api/v1/presence_start_end_per_weekday/11')
        self.assertEqual(
            data,
            [
                ['Mon', '09:12:14', '15:54:17'],
                ['Tue', '09:19:50', '13:55:54'],
                ['Wed', '09:13:26', '16:15:27'],
                ['Thu', '09:53:22', '16:16:26'],
                ['Fri', '13:16:56', '15:04:02'],
                ['Sat', '00:00:00', '00:00:00'],
                ['Sun', '00:00:00', '00:00:00'],
            ]
        )
        self.endpoint_should_return_404(
            '/api/v1/presence_start_end_per_weekday/1')

    def test_api_mean_time_weekday(self):
        """
        Test mean presence time of given user grouped by weekday.
        """
        data = self.endpoint_return_json_data('/api/v1/mean_time_weekday/11')
        self.assertEqual(
            data,
            [
                ['Mon', 24123.0],
                ['Tue', 16564.0],
                ['Wed', 25321.0],
                ['Thu', 22984.0],
                ['Fri', 6426.0],
                ['Sat', 0],
                ['Sun', 0],
            ]
        )
        self.endpoint_should_return_404('/api/v1/mean_time_weekday/1')

    def test_api_presence_weekday(self):
        """
        Test total presence time of given user grouped by weekday.
        """
        data = self.endpoint_return_json_data('/api/v1/presence_weekday/11')
        self.assertEqual(
            data,
            [
                ['Weekday', 'Presence (s)'],
                ['Mon', 24123],
                ['Tue', 16564],
                ['Wed', 25321],
                ['Thu', 45968],
                ['Fri', 6426],
                ['Sat', 0],
                ['Sun', 0],
            ]
        )
        self.endpoint_should_return_404('/api/v1/presence_weekday/1')


class PresenceAnalyzerUtilsTestCase(PresenceAnalyzerTestCase):
    """
    Utility functions tests.
    """
    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_get_users(self):
        """
        Test parsing of Users XML file.
        """
        data = utils.get_users()
        self.assertItemsEqual(data.keys(), [10, 11, 141])
        self.assertDictEqual(
            data[10],
            {
                'avatar_url': 'https://intranet.stxnext.pl:443'
                              '/api/images/users/10',
                'name': 'Maciej Z.',
            }
        )

    def test_start_end_grouped_by_weekday(self):
        """
        Test grouped start end presence by weekday.
        """
        data = utils.get_data()
        grouped_by_weekday = utils.start_end_group_by_weekday(data[11])
        self.assertDictEqual(
            grouped_by_weekday,
            {
                0: {'start': [33134], 'end': [57257]},
                1: {'start': [33590], 'end': [50154]},
                2: {'start': [33206], 'end': [58527]},
                3: {'start': [37116, 34088], 'end': [60085, 57087]},
                4: {'start': [47816], 'end': [54242]},
                5: {'start': [], 'end': []},
                6: {'start': [], 'end': []},
            }
        )

    def test_mean_start_end_grouped_by_weekday(self):
        """
        Test mean start/end presence by workday.
        """
        data = utils.get_data()
        grouped_by_weekday = utils.start_end_group_by_weekday(data[11])
        mean_start_end_by_day = utils.mean_start_end_by_weekday(
            grouped_by_weekday)
        self.assertEqual(
            mean_start_end_by_day,
            [
                ['09:12:14', '15:54:17'],
                ['09:19:50', '13:55:54'],
                ['09:13:26', '16:15:27'],
                ['09:53:22', '16:16:26'],
                ['13:16:56', '15:04:02'],
                ['00:00:00', '00:00:00'],
                ['00:00:00', '00:00:00'],
            ]
        )

    def test_group_by_weekday(self):
        """
        Test grouping presence entries by weekday.
        """
        data = utils.get_data()
        grouped_by_weekday = utils.group_by_weekday(data[11])
        self.assertEqual(
            grouped_by_weekday,
            [
                [24123],
                [16564],
                [25321],
                [22969, 22999],
                [6426],
                [],
                [],
            ]
        )

    def test_seconds_since_midnight(self):
        """
        Test calculating amount of seconds from midnight.
        """
        self.assertEqual(
            utils.seconds_since_midnight(datetime.time(0, 0, 3)),
            3
        )
        self.assertEqual(
            utils.seconds_since_midnight(datetime.time(1, 1, 1)),
            3661
        )

    def test_interval(self):
        """
        Test calculating interval between datetime.time objects.
        """
        self.assertEqual(
            utils.interval(
                datetime.time(0, 0, 3),
                datetime.time(0, 0, 5)
            ),
            2
        )
        self.assertEqual(
            utils.interval(
                datetime.time(0, 0, 5),
                datetime.time(0, 0, 3)
            ),
            -2
        )

    def test_cache(self):
        """
        Test cache decorator.
        """
        @utils.cache(1000)
        def stub():
            stub.was_called = True
            return 200

        self.assertEqual(stub(), 200)
        self.assertTrue(stub.was_called)
        stub.was_called = False
        self.assertEqual(stub(), 200)
        self.assertFalse(stub.was_called)

    def test_cache_timeout(self):
        """
        Test cache decorator timeout.
        """
        @utils.cache(2)
        def stub():
            """Stub method."""
            return 200 + stub.i

        stub.i = 1
        self.assertEqual(stub(), 201)
        time.sleep(3)
        stub.i = 2
        self.assertEqual(stub(), 202)
        stub.i = 3
        self.assertEqual(stub(), 202)

    def test_cache_diffrent_functions(self):
        """
        Test cache decorator can cache results of diffrent functions.
        """
        @utils.cache(2)
        def stub1():
            """Stub method."""
            return 200

        @utils.cache(2)
        def stub2():
            """Stub method."""
            return [1, 2]

        self.assertEqual(stub1(), 200)
        self.assertEqual(stub2(), [1, 2])
        time.sleep(4)
        self.assertEqual(stub1(), 200)
        self.assertEqual(stub2(), [1, 2])


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
