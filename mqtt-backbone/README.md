# MQTT BoaT (Boat of associated Things)

An MQTT-based architecture is presented for a boat-based platform with connected sensors and actuators to facilitate sail-by-wire and autonomous sailing.

## Topics

These topics are nested under `boat/{id}`, where `{id}` is the id of the boat (`0` for our testing float).

From here on, topics are assumed to be prefixed with `boat/{id}` (e.g. `/status/motor/right` => `boat/1/status/motor/right`)

### Sensors

#### `/sensors/location`

GPS data is published here. Example message:

```
{"location":{"lat":50.8612345,"lon":3.3512345,"accuracy":22.5,"bearing":0,"altitude":0,"speed":0,"provider":"network"}}

```

#### `/sensors/controller`

##### Joysticks

Joystick values are published on `sensors/controller/joystick/{left,right}/{x,y}`. Both `x` and `y` values range from 0-255.

##### Buttons

Only pressed state is sent. These states are published under `sensors/controller/{button}/pressed`. The value is either `0` (not pressed) or `1` (pressed).

The following buttons are sent:

* `l1`, `l2`, `r1`, `r2`
* `triangle`, `circle`, `x`, `square`
* `start`, `select`
* `dpadUp`, `dpadDown`, `dpadLeft`, `dpadRight`

#### `/sensors/acceleration`

This topic captures the values of an accelerometer.

#### `/sensors/gyroscope`


#### `/sensors/magnetometer`


#### `/sensors/lidar`


### Actuators

#### `/actuators/motor/left`, `/actuators/motor/right`

These topics accept values in the range [-255, 255], where negative values indicate reverse.

#### `actuators/controller/rumble/left`, `actuators/controller/rumble/right`

These topics accept `0` (no rumble) and `1` (rumble). Upon receiving a `1`, the controller will rumble for 5 seconds. This can be cancelled by sending `0` during rumbling.

### Status

#### Arduino status

* `/status/motor/right` and `/status/motor/left` give the value the Arduino sets the motors to
* `/status/arduino-comm`: `1` on connect, `0` on disconnect
* `/status/serial/in` and `/status/serial/out` show everything that is sent to and received from serial bus


