# Auto-pilot

## Input data

### Realsense

Connected with USB3.

### MQTT

Channels:

* `boat/{id}/sensors/acceleration/{x,y,z}`
* `boat/{id}/sensors/gyroscope/{x,y,z}`
* `boat/{id}/sensors/magnetometer/{x,y,z}`

## Status

On connecting, the autopilot should publish `1` to `boat/{id}/status/autopilot`.

As a [last will](https://www.hivemq.com/blog/mqtt-essentials-part-9-last-will-and-testament/), the auto-pilot should publish `0` to `boat/{id}/status/`autopilot`.

## Output

The output should be sent to the following channels:

* `boat/{id}/sensors/autopilot/motor/left`
* `boat/{id}/sensors/autopilot/motor/right`

The value should be a number ∈ [-255, 255], sent to an MQTT channel as an UTF-8 string.

