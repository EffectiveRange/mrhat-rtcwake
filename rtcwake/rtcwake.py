# SPDX-FileCopyrightText: 2024 Ferenc Nandor Janky <ferenj@effective-range.com>
# SPDX-FileCopyrightText: 2024 Attila Gombos <attila.gombos@effective-range.com>
# SPDX-License-Identifier: MIT

import argparse
import os
import subprocess
import sys
from typing import Optional, Any

from datetime import datetime, timedelta, time, timezone
from tzlocal import get_localzone
from context_logger import get_logger


log = get_logger("mrhat-rtcwake")


class RtcWake(object):
    too_soon_msg = "Minimum supported sleep time is 2 minutes!"
    too_late_msg = "Maximum supported sleep time is around 1 month"

    def __init__(self, args: Optional[argparse.Namespace] = None, *argv):
        self.args = vars(args or argparse.Namespace())
        self.rtc = self.args.get("device", "rtc0")
        self.adjfile = self.args.get("adjfile", "/etc/adjtime")
        self.argv = argv

    def parse_hwclock_ts(self, dt: str) -> datetime:
        try:
            return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S.%f%z")
        except ValueError as e:
            log.error(f"Invalid hwclock timestamp format:{dt}")
            raise e

    def parse_hwclock(self) -> datetime:
        try:
            res = subprocess.check_output(
                [
                    "hwclock",
                    "-r",
                    "--rtc",
                    f"/dev/{self.rtc}",
                    "--adjfile",
                    self.adjfile,
                ],
                stderr=subprocess.STDOUT,
            )
            return self.parse_hwclock_ts(res.decode().strip())

        except subprocess.CalledProcessError as e:
            log.error(f"Failed to read hwclock {self.rtc}: {e.output.decode().strip()}")
            raise e

    def read_wakealarm(self) -> datetime:
        tzinfo = self.get_rtc_tzinfo()
        with open(f"/sys/class/rtc/{self.rtc}/wakealarm") as f:
            ts = f.readline()
            return datetime.fromtimestamp(int(ts), tzinfo)

    def get_rtc_tzinfo(self):
        with open(self.adjfile) as f:
            lines = f.readlines()
        tz = lines[2].strip()
        if tz not in ("UTC", "LOCAL"):
            log.error(f"Failed to get RTC timezone info from {self.adjfile}")
            raise ValueError()

        return timezone.utc if tz == "UTC" else get_localzone()

    def cancel_alarm(self):
        with open(f"/sys/class/rtc/{self.rtc}/wakealarm", "w") as f:
            f.write("0")

    def validate_alarm(self, now: datetime, wakealarm: datetime) -> Optional[str]:
        two_minutes = timedelta(minutes=2)
        minute_to_sec = 60
        one_year_months = 12
        max_days_in_month = timedelta(days=31)
        if (wakealarm - now) < two_minutes and (
            (wakealarm.minute - now.minute) * minute_to_sec
        ) < two_minutes.total_seconds():
            return RtcWake.too_soon_msg
        if (
            (wakealarm - now) > max_days_in_month
            or (wakealarm.month % one_year_months > (now.month + 1) % one_year_months)
            or (
                wakealarm.month % one_year_months == (now.month + 1) % one_year_months
                and (
                    wakealarm.day,
                    wakealarm.hour,
                    wakealarm.minute,
                )
                >= (now.day, now.hour, now.minute)
            )
        ):
            return RtcWake.too_late_msg
        return None

    def exec(self):
        try:
            tz = self.get_rtc_tzinfo()
            now = self.parse_hwclock().astimezone(tz)
            res = subprocess.check_output(
                ["rtcwake", *self.argv, "--mode", "no"], stderr=subprocess.STDOUT
            )
            wakealarm = self.read_wakealarm().astimezone(tz)
            log.info(f"current time:{now}")
            log.info(f"wakealarm time:{wakealarm}")
            msg = self.validate_alarm(now, wakealarm)
            if msg is not None:
                log.error(msg)
                self.cancel_alarm()
                raise ValueError(msg)
            log.info(f"halting system")
            os.system("poweroff --halt")

        except subprocess.CalledProcessError as e:
            log.error(f"Failed to read hwclock: {e.output.decode().strip()}")
            raise e
