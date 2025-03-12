# ntpcl

An NTP server for Chile using server's timezone.

## Why

To synchronize an NTP desk clock, ideally it gets GMT time from an NTP server, you configure the timezone and daylight saving time (DST) in your clock, and that's it.

However, in Chile you [never know](https://github.com/eggert/tz/blob/1913dd77b52a84ef73a98c27677ea14c1ce80a0f/southamerica#L1344-L1356) when the next DST will be. It's cumbersome to set the correct offset in every clock every year, it should come from the server in the NTP response instead.

## How

Configure your NTP clocks with:
- your server IP as its NTP server
- Timezone **GMT+3**, no DST. With 6 or 7 hours of difference with GMT−3 and GMT−4, in case of misconfiguration the time will be wrong enough for you to notice.
