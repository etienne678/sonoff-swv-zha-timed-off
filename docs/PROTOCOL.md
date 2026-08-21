# Protocol and behavior notes

## Per-opening timer

The project sends the On/Off cluster server command `0x42`, commonly named
`On With Timed Off`, with these fields:

```yaml
on_off_control: 0
on_time: 10
off_wait_time: 10
```

On the tested SONOFF SWV, a raw `on_time` value of `10` produced approximately
10 seconds of physical opening. This is empirical device behavior. Do not infer
that every device or firmware interprets the raw value identically; perform the
controlled test described in `TESTING.md`.

`off_wait_time` is transmitted as the tested raw value `10`. It is not used by
this project as the requested watering duration.

## Command policy

| Incoming cluster command | Quirk behavior |
| --- | --- |
| `0x00` OFF | Cancel pending state-refresh task and send OFF |
| `0x01` ON | Send `0x42` with `on_time=1800` |
| `0x02` TOGGLE | Send OFF; fail closed |
| `0x42` with `on_time=1..1800` | Send `0x42` with the requested value |
| `0x42` with invalid value | Send `0x42` with `on_time=1800` |
| Other On/Off cluster command | Reject with `ValueError` |

The fallback is a maximum-runtime policy, not a guarantee of operation. A
normal ON command is intentionally unable to open the valve indefinitely.

## Why the quirk refreshes state

The tested valve closes itself after the hardware timeout but does not reliably
report that transition to ZHA. The quirk schedules an attribute read one second
after the requested timeout. This refresh affects only Home Assistant's view;
the physical timer runs in the valve.

A new ON or an OFF cancels the previous refresh task so an old timer cannot
perform a stale read in the middle of a new cycle.

## Attribute `0x5011`

`0x5011` belongs to the SONOFF manufacturer cluster `0xFC11`. It is named
`auto_close_water_shortage` in the current upstream SWV quirk. Upstream exposes
it as a boolean-style `Water shortage auto-close` switch using values `0` and
`30`:

<https://github.com/zigpy/zha-device-handlers/blob/dev/zhaquirks/sonoff/swv.py>

It is not the `on_time` field of command `0x42` and must not be presented as a
general per-opening `Auto Close Time` duration.

This project defines the attribute so reports can be decoded, but deliberately
does not expose it as a Home Assistant entity. That avoids suggesting it is part
of the timed-opening feature. Users who need the water-shortage feature should
use or adapt the upstream implementation and test it separately.

## Hardware timer versus software OFF

The hardware timer begins when the valve accepts the command. A Home Assistant
software delay generally begins after command execution and state confirmation,
so the software OFF can occur a few seconds later. That is expected redundancy.

During a Home Assistant, coordinator, or radio outage, the software OFF may not
be delivered. The preloaded hardware timer is the layer intended to continue in
that failure case. Mechanical failure remains possible.
