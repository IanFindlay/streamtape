#!/usr/bin/env/ python3

"""Unittests for twitch_recorder.py."""

import datetime as dt
import unittest

import streamtape as st


class TestStrtimeDatetime(unittest.TestCase):
    """Test for strtime_datetime function."""

    def test_later_hour_yields_same_day_date_and_correct_time(self):
        """Start time later than current time sets start date to today."""
        now = dt.datetime.now()
        start_time = st.strtime_datetime('{}:00'.format(now.hour + 1))
        self.assertEqual(now.day, start_time.day)

    def test_earlier_hour_yields_next_day_date_and_correct_time(self):
        """Start time earlier than current time sets start date to tommorow."""
        now = dt.datetime.now()
        start_time = st.strtime_datetime('{}:00'.format(now.hour - 1))
        self.assertEqual(now.day + 1, start_time.day)

    def test_start_time_same_hour_as_current_but_earlier_yields_next_day(self):
        """Edge case where start time is just under 24 hours away."""
        now = dt.datetime.now()
        start_time = st.strtime_datetime('{}:{}'.format(now.hour,
                                                        now.minute - 1))
        self.assertEqual(now.day + 1, start_time.day)


if __name__ == '__main__':
    unittest.main()
