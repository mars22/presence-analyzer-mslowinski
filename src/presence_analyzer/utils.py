# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""
from __future__ import unicode_literals

import csv
from json import dumps
from functools import wraps
from datetime import datetime, timedelta
from lxml.etree import parse
from collections import deque
from threading import Lock
from flask import Response

from presence_analyzer.main import app

import logging
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        """
        This docstring will be overridden by @wraps decorator.
        """
        return Response(
            dumps(function(*args, **kwargs)),
            mimetype='application/json'
        )
    return inner


def cache(cache_time):
    """
    Cache result of func for period of cache_time (in s).
    """
    def decorator(func):
        fn_name = func.__name__

        cache = {}
        cache.setdefault(fn_name, {
            'memo': deque(maxlen=1),
            'valid': deque(maxlen=1),
        })
        lock = Lock()

        @wraps(func)
        def wraper():
            now = datetime.now()
            valid_to = now + timedelta(0, cache_time)
            with lock:
                if not cache[fn_name]['memo'] or \
                   now > cache[fn_name]['valid'][0]:
                    cache[fn_name]['valid'].append(valid_to)
                    cache[fn_name]['memo'].append(func())
                return cache[fn_name]['memo'][0]
        return wraper
    return decorator


@cache(600)
def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=str(','))
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}

    return data


def _get_server_url(element):
    """
    Extract server url from xml element.
    """
    protocol = element.find('protocol').text
    host = element.find('host').text
    port = element.find('port').text
    return '{0}://{1}:{2}'.format(protocol, host, port)


def get_users():
    """
    Extracts users data from XML file.

    It creates structure like this:
    data = {
        'user_id': {
            'name': 'User Name',
            'avatar_url': 'http://.....'
        }
    }
    """
    data = {}
    xml = parse(app.config['USERS_XML'])
    root = xml.getroot()
    server_info = root.find('server')
    users = root.find('users')
    server_url = _get_server_url(server_info)
    for i, user_elem in enumerate(users):
        try:
            user_id = int(user_elem.attrib['id'])
            name = user_elem.find('name').text
            avatar = user_elem.find('avatar').text
            avatar_url = '{0}{1}'.format(server_url, avatar)
        except (KeyError, AttributeError):
            log.debug('Problem with line %d: ', i, exc_info=True)

        data[user_id] = {
            'name': unicode(name),
            'avatar_url': unicode(avatar_url),
        }

    return data


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = [[], [], [], [], [], [], []]  # one list for every day in week
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def start_end_group_by_weekday(items):
    """
    Groups presence entries by weekday. Each weekday contains to dict with
    to key start, end.
    Start key contains a list of starts for given day.
    End key contains a list of starts for given day.
    """
    result = {i: {'start': [], 'end': []} for i in range(7)}
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        curr = result[date.weekday()]
        curr['start'].append(seconds_since_midnight(start))
        curr['end'].append(seconds_since_midnight(end))
    return result


def str_to_time(str_time):
    """
    Convert string rep. of time to time.
    """
    import time
    return time.strftime('%H:%M:%S', time.gmtime(str_time))


def mean_start_end_by_weekday(grouped):
    """
    Calculate mean start/end time by day.
    """
    result = [
        [
            str_to_time(mean(item['start'])),
            str_to_time(mean(item['end'])),
        ]
        for item in grouped.values()
    ]
    return result


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0
