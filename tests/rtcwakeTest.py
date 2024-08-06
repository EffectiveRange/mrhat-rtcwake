import unittest
from unittest import TestCase
from unittest.mock import MagicMock

from context_logger import setup_logging

from rtcwake import RtcWake
import datetime


class RtcWakeTest(TestCase):

    @classmethod
    def setUpClass(cls):
        setup_logging("mrhat-rtcwake-python", "DEBUG", warn_on_overwrite=False)

    def setUp(self):
        print()

    def test_hwclock_timestamp_parsing(self):
        # # Given
        dt = "2024-08-04 00:43:13.520949+02:00"
        rtc = RtcWake()

        # # When
        res = rtc.parse_hwclock_ts(dt)

        # # Then
        self.assertEqual(res.year, 2024)
        self.assertEqual(res.month, 8)
        self.assertEqual(res.day, 4)
        self.assertEqual(res.hour, 0)
        self.assertEqual(res.minute, 43)
        self.assertEqual(res.second, 13)
        self.assertEqual(res.microsecond, 520949)
        self.assertIsNotNone(res.tzinfo)
        assert res.tzinfo is not None  # for mypy
        self.assertEqual(res.tzinfo.utcoffset(None), datetime.timedelta(hours=2))

    def test_hwclock_timestamp_parsing_error(self):
        # # Given
        dt = "2024-08-04 00:43:13.520949"
        rtc = RtcWake()

        # # When/Tthen
        self.assertRaises(ValueError, lambda: rtc.parse_hwclock_ts(dt))

    def test_wake_time_validation_too_soon_1(self):
        now = datetime.datetime(2024, 5, 21, 8, 12, 23)
        wake = datetime.datetime(2024, 5, 21, 8, 13, 59)
        wake_ok = datetime.datetime(2024, 5, 21, 8, 14, 00)
        rtc = RtcWake()
        self.assertEqual(RtcWake.too_soon_msg, rtc.validate_alarm(now, wake))
        self.assertIsNone(rtc.validate_alarm(now, wake_ok))

    def test_wake_time_validation_too_late_1(self):
        now = datetime.datetime(2024, 5, 21, 8, 12, 23)
        wake = datetime.datetime(2024, 6, 21, 8, 12, 23)
        wake2 = datetime.datetime(2024, 6, 21, 8, 12, 00)
        wake3 = datetime.datetime(2024, 6, 22, 8, 12, 23)
        wake4 = datetime.datetime(2024, 7, 1, 8, 11, 23)
        wake_ok = datetime.datetime(2024, 6, 21, 8, 11, 59)
        rtc = RtcWake()
        self.assertEqual(
            RtcWake.too_late_msg,
            rtc.validate_alarm(now, wake),
        )
        self.assertEqual(
            RtcWake.too_late_msg,
            rtc.validate_alarm(now, wake2),
        )
        self.assertEqual(
            RtcWake.too_late_msg,
            rtc.validate_alarm(now, wake3),
        )
        self.assertEqual(
            RtcWake.too_late_msg,
            rtc.validate_alarm(now, wake4),
        )
        self.assertIsNone(rtc.validate_alarm(now, wake_ok))

    def test_wake_time_validation_too_late_2(self):
        now = datetime.datetime(2024, 12, 21, 8, 12, 23)
        wake = datetime.datetime(2025, 1, 21, 8, 12, 23)
        wake2 = datetime.datetime(2025, 1, 21, 8, 12, 00)
        wake3 = datetime.datetime(2025, 2, 1, 8, 11, 59)
        wake_ok = datetime.datetime(2025, 1, 21, 8, 11, 59)
        rtc = RtcWake()
        self.assertEqual(
            RtcWake.too_late_msg,
            rtc.validate_alarm(now, wake),
        )
        self.assertEqual(
            RtcWake.too_late_msg,
            rtc.validate_alarm(now, wake2),
        )
        self.assertEqual(
            RtcWake.too_late_msg,
            rtc.validate_alarm(now, wake3),
        )
        self.assertIsNone(rtc.validate_alarm(now, wake_ok))


if __name__ == "__main__":
    unittest.main()
