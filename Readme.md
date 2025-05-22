# ntpcl

An NTP server for Chile using server's tzdata.

## Why

To synchronize an NTP desk clock, ideally it gets UTC time from an NTP server, you configure the timezone and daylight saving time (DST) in your clock, and that's it.

However, in Chile you [never know](https://github.com/eggert/tz/blob/1913dd77b52a84ef73a98c27677ea14c1ce80a0f/southamerica#L1344-L1356) when the next DST will be. It's cumbersome to set the correct offset in every clock every year, it should come from the server in the NTP response instead.

> Especially because [CH899](https://www.hr-clockparts.com/clock-movement/wifi-clock-movement.html) wifi clock's hotspot has weak signal and I have to go underground to configure it because I just can't connect to it in my apartment.

## How

This NTP server provides, instead of UTC time, the time with an offset already included.

Configure your NTP clocks with:

- your server IP as its NTP server

  > If it can't be configured, you'll have to hijack it. CH899 clock queries `time.pool.aliyun.com` and `cn.ntp.org.cn`, so in my router I set the DNS to resolve those domains to my server IP.

- Timezone **GMT+3**, no DST. With 6 or 7 hours of difference with GMT−3 and GMT−4, in case of misconfiguration the time will be wrong enough for you to notice.

  > Misconfiguration for example if the DNS hijacking stops working.

- Query time at 00:01, so on DST changes it jumps back to 23:01 or forward to 01:01.

  > Unfortunately CH899 can query only as late as 22:00 or as early as 9:00. Using 9:00 would show wrong time in the morning, using 22:00 would show wrong time almost all day.
  >
  > Hack: set `CH899` to `true` in clock config (see below) and set the CH899 clock to query at 22:00. This program will make an exception for them and advance DST changes, so time will be wrong for only 2 hours before midnight.

Optionally, create `config.json` from `config.example.json`. `clocks` keys are their IPs, `healthcheck` can be defined as an URL to ping on ntp success. This way you can be alerted if your clocks stop syncing, for example by [healthchecks.io](https://healthchecks.io).

## Running

- Clone this repo in your server
- (Optional) Create `config.json`
- Start the container with docker compose.

To apply [tzdata](https://pkgs.alpinelinux.org/package/v3.21/main/x86_64/tzdata) updates: `docker compose restart`
