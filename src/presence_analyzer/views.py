# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import abort, render_template
from jinja2 import TemplateNotFound

from presence_analyzer.main import app
from presence_analyzer.utils import jsonify, get_data, mean, \
    group_by_weekday, start_end_group_by_weekday, mean_start_end_by_weekday

import logging
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.route('/', defaults={'template_name': 'presence_weekday'})
@app.route('/<string:template_name>', methods=['GET'])
def render_page(template_name):
    """
    Render templates by template_name.
    """
    try:
        return render_template(template_name + '.html')
    except TemplateNotFound:
        abort(404)


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [
        {'user_id': i, 'name': 'User {0}'.format(str(i))}
        for i in data.keys()
    ]


@app.route('/api/v1/mean_time_weekday/',
           defaults={'user_id': 0},
           methods=['GET'])
@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    return result


@app.route('/api/v1/presence_weekday/',
           defaults={'user_id': 0},
           methods=['GET'])
@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end_per_weekday/',
           defaults={'user_id': 0},
           methods=['GET'])
@app.route('/api/v1/presence_start_end_per_weekday/<int:user_id>',
           methods=['GET'])
@jsonify
def presence_start_end_per_weekday_view(user_id):
    """
    Returns list of mean presence start and end time of given user
    grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = start_end_group_by_weekday(data[user_id])
    mean_start_end = mean_start_end_by_weekday(weekdays)
    result = [
        (calendar.day_abbr[weekday], start_end[0], start_end[1])
        for weekday, start_end in enumerate(mean_start_end)
    ]
    return result
