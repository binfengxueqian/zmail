import datetime
import os

import pytest

from zmail.exceptions import InvalidArguments
from zmail.helpers import (convert_date_to_datetime, get_abs_path,
                           get_intersection, make_iterable, match_conditions)
from zmail.structures import CaseInsensitiveDict


def test_convert_date_to_datetime():
    now = datetime.datetime.now()
    now_year = now.year
    now_month = now.month
    now_day = now.day

    assert now is convert_date_to_datetime(now)

    with pytest.raises(InvalidArguments):
        convert_date_to_datetime('test-with-invalidArgs')

    datetime_as_str = ''
    res_datetime = convert_date_to_datetime(datetime_as_str)
    assert res_datetime.year == now_year
    assert res_datetime.month == now_month
    assert res_datetime.day == now_day

    for datetime_as_str in ('1000', '1000-'):
        res_datetime = convert_date_to_datetime(datetime_as_str)
        assert res_datetime.year == 1000
        assert res_datetime.month == now_month
        assert res_datetime.day == now_day
        assert res_datetime.hour == 0
        assert res_datetime.minute == 0
        assert res_datetime.second == 0

    for datetime_as_str in ('1000-05', '1000-5', '1000-05-', '1000-5-'):
        res_datetime = convert_date_to_datetime(datetime_as_str)
        assert res_datetime.year == 1000
        assert res_datetime.month == 5
        assert res_datetime.day == now_day
        assert res_datetime.hour == 0
        assert res_datetime.minute == 0
        assert res_datetime.second == 0

    for datetime_as_str in ('1000-10-01', '1000-10-1'):
        res_datetime = convert_date_to_datetime(datetime_as_str)
        assert res_datetime.year == 1000
        assert res_datetime.month == 10
        assert res_datetime.day == 1
        assert res_datetime.hour == 0
        assert res_datetime.minute == 0
        assert res_datetime.second == 0

    for datetime_as_str in ('1000-10-01 03', '1000-10-01 3:'):
        res_datetime = convert_date_to_datetime(datetime_as_str)
        assert res_datetime.year == 1000
        assert res_datetime.month == 10
        assert res_datetime.day == 1
        assert res_datetime.hour == 3
        assert res_datetime.minute == 0
        assert res_datetime.second == 0

    for datetime_as_str in ('1000-10-01 04:05', '1000-10-01 4:5:'):
        res_datetime = convert_date_to_datetime(datetime_as_str)
        assert res_datetime.year == 1000
        assert res_datetime.month == 10
        assert res_datetime.day == 1
        assert res_datetime.hour == 4
        assert res_datetime.minute == 5
        assert res_datetime.second == 0

    for datetime_as_str in ('1000-10-01 02:03:04', '1000-10-01 2:3:4',
                            '1000-10-01 02:03:04', '1000-10-01 2:3:4 '):
        res_datetime = convert_date_to_datetime(datetime_as_str)
        assert res_datetime.year == 1000
        assert res_datetime.month == 10
        assert res_datetime.day == 1
        assert res_datetime.hour == 2
        assert res_datetime.minute == 3
        assert res_datetime.second == 4


def test_match_conditions():
    mock_mail_headers = CaseInsensitiveDict({
        'subject': 'zmail',
        'from': 'zmail_test@gmail.com',
        'date': datetime.datetime(year=2000, month=1, day=15)
    })

    headers_without_date = mock_mail_headers.copy()
    headers_without_date['date'] = None

    headers_without_subject = mock_mail_headers.copy()
    headers_without_subject['subject'] = None

    headers_without_from = mock_mail_headers.copy()
    headers_without_from['from'] = None

    assert match_conditions(mock_mail_headers)
    assert match_conditions(mock_mail_headers, subject='zmail')
    assert match_conditions(mock_mail_headers, sender='zmail')
    assert match_conditions(mock_mail_headers, subject='zmail', sender='zmail')

    assert match_conditions(mock_mail_headers, subject='123') is False
    assert match_conditions(mock_mail_headers, subject='123', sender='zmail') is False

    with pytest.raises(InvalidArguments):
        match_conditions(mock_mail_headers, subject='zmail', start_time=1)
        match_conditions(mock_mail_headers, subject='zmail', end_time=1)

    assert match_conditions(mock_mail_headers, end_time=datetime.datetime.now())
    assert match_conditions(mock_mail_headers, end_time='2018-1-1')
    assert match_conditions(mock_mail_headers, start_time=datetime.datetime.now()) is False
    assert match_conditions(mock_mail_headers, start_time='2018-1-1') is False

    assert match_conditions(mock_mail_headers, start_time=datetime.datetime(2000, 1, 1),
                            end_time=datetime.datetime.now())
    assert match_conditions(mock_mail_headers, start_time='2000-1-1', end_time='2018-1-1')

    assert match_conditions(headers_without_date, start_time=datetime.datetime.now()) is False
    assert match_conditions(headers_without_date, end_time=datetime.datetime.now()) is False
    assert match_conditions(headers_without_date, start_time=datetime.datetime(2000, 1, 1),
                            end_time=datetime.datetime.now()) is False

    assert match_conditions(headers_without_subject, subject='test') is False

    assert match_conditions(headers_without_from, sender='test') is False


def test_get_intersection():
    assert get_intersection((1, 5), (1, 5)) == [1, 2, 3, 4, 5]
    assert get_intersection((1, 5), (None, None)) == [1, 2, 3, 4, 5]

    assert get_intersection((1, 5), (2, 3)) == [2, 3]
    assert get_intersection((1, 5), (3, None)) == [3, 4, 5]
    assert get_intersection((1, 5), (None, 3)) == [1, 2, 3]

    assert get_intersection((1, 5), (-3, None)) == [1, 2, 3, 4, 5]
    assert get_intersection((1, 5), (None, 10)) == [1, 2, 3, 4, 5]

    assert get_intersection((0, 0), (1, 2)) == []
    assert get_intersection((0, 0), (None, None)) == [0]
    assert get_intersection((1, 0), (1, 2)) == []


def test_make_iterable():
    assert make_iterable('') == ('',)
    assert make_iterable(1) == (1,)

    assert make_iterable(list()) == list()
    assert make_iterable(tuple()) == tuple()

    assert make_iterable([1, 2, 3]) == [1, 2, 3]
    assert make_iterable((1, 2, 3)) == (1, 2, 3)


def test_get_abs_path():
    here = os.path.abspath(os.path.dirname(__file__))
    assert os.path.exists(get_abs_path(os.path.join(here, 'test_helpers.py')))
