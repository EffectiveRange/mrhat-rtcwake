# mrhat-rtcwake

A wrapper for `rtcwake` utility to be used on the [Effective Range MrHat Raspberry Pi extension Hat](https://effective-range.com/hardware/mrhat/), featuring an Epson RX8130CE RTC module.

## Help

```bash
usage: mrhat-rtcwake [-h] [-v] [-d DEVICE] [-A ADJFILE] (--date DATE | -t TIME | -s SECONDS)

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose messages (default: False)
  -d DEVICE, --device DEVICE
                        select rtc device (rtc0|rtc1|...) (default: rtc0)
  -A ADJFILE, --adjfile ADJFILE
                        specifies the path to the adjust file (default: /etc/adjtime)
  --date DATE           date time of timestamp to wake (default: None)
  -t TIME, --time TIME  set the wakeup time to the absolute time in time_t (default: None)
  -s SECONDS, --seconds SECONDS
                        seconds to sleep (must be greater or equal to 120, will be rounded to the nearest minute) (default: None)
```

## Examples
```bash
sudo rtcwake --date +1h  # go to sleep for 1 hour
sudo rtcwake --date "2024-08-12 8:00"  # go to sleep  until the specified date and time
sudo rtcwake --seconds 210  # go to sleep for 210 seconds (truncated to minute boundary)
sudo mrhat-rtcwake -t 1722903023 # go to sleep untile the specified time using seconds since epoch
```
All arguments are forwarded to the underlying `rtcwake` utility, for detailed time specification see [man entry for rtcwake](https://man7.org/linux/man-pages/man8/rtcwake.8.html)


## Operation

The EPSON RX8130CE RTC supports alarm interrupts on a minute granularity, and also the fact that shutdown and boot up are non-zero time operations a 2 minutes minimum sleep time has been selected and is enforced by this wrapper. If less than 2 minutes specified with either time spec mode, then the program returns an error.

Also the RTC has a maximum alarm window of a calendar month. This constraint is also enforced by this wrapper, if a longer sleep period is requested, then the program returns an error.

Otherwise if a valid time-point is specified, then the RTC alarm is armed, and the wrapper will invoke `poweroff --halt` which halts the system using the `sytemctl` utility on the normal Raspbian OS iamge. There's an extreme low power (XLP) PIC-18-Q20 family MCU onboard, that reacts to the RTC interrupt with our [default Firmware](https://github.com/EffectiveRange/fw-mrhat), and executes the wake-from-halt procedure - which is pulling the SCL line low - that in turn boots up the Raspberry Pi.

