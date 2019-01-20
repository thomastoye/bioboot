# MQTT BoaT (Boat of associated Things)

An MQTT-based architecture is presented for a boat-based platform with connected sensors and actuators to facilitate sail-by-wire and autonomous sailing.

## Topics

These topics are nested under `boat/:id`, where `:id` is the id of the boat (`0` for our testing float).

From here on, topics are assumed to be prefixed with `boat/:id` (e.g. `/status/motor/right` => `boat/1/status/motor/right`)

### Sensors

#### `/sensors/controller`


#### `/sensors/acceleration`

This topic captures the values of an accelerometer.

#### `/sensors/gyroscope`


#### `/sensors/magnetometer`


#### `/sensors/lidar`


### Actuators

#### `/actuators/motor/left`, `/actuators/motor/right`

These topics accept values in the range [-255, 255], where negative values indicate reverse.

### Status

#### Arduino status

* `/status/motor/right` and `/status/motor/left` give the value the Arduino sets the motors to
* `/status/arduino-comm`: `1` on connect, `0` on disconnect
* `/status/serial/in` and `/status/serial/out` show everything that is sent to and received from serial bus


