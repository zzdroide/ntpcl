# ntpcl

An NTP server for Chile using server's timezone.

## Why

To synchronize an NTP desk clock, ideally it gets GMT time from an NTP server, you configure the timezone and daylight saving time (DST) in your clock, and that's it.

However, in Chile you [never know](https://github.com/eggert/tz/blob/1913dd77b52a84ef73a98c27677ea14c1ce80a0f/southamerica#L1344-L1356) when the next DST will be. It's cumbersome to set the correct offset in every clock every year, it should come from the server in the NTP response instead.

## How

Configure your NTP clocks with:

- your server IP as its NTP server
  > If it can't be configured, you'll have to hijack it. My [CH899](https://www.hr-clockparts.com/clock-movement/wifi-clock-movement.html) clock queries `time.pool.aliyun.com` and `cn.ntp.org.cn`, so in my router I set the DNS to resolve those domains to my server IP.

- Timezone **GMT+3**, no DST. With 6 or 7 hours of difference with GMT−3 and GMT−4, in case of misconfiguration the time will be wrong enough for you to notice.
  > Misconfiguration especially if the DNS hijacking is removed.

- Query time at 00:01, so on DST changes it jumps back to 23:01 or forward to 01:01.
  > CH899's interface only allows you to choose presets like 22:00, but with inspect element I changed it to 00:01 and it works fine.

## Running

Clone this repo in your server and start the container with docker compose.
