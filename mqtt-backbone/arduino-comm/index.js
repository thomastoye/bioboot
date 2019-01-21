const SerialPort = require('serialport');
const Readline = require('@serialport/parser-readline');
const { Observable, Subject, ReplaySubject, from, of, combineLatest } = require('rxjs');
const { map, filter, startWith, auditTime, debounceTime } = require('rxjs/operators');
const leftPad = require('left-pad')
const winston = require('winston');

const name = 'arduino-comm';

const mqttPrefix = 'boat/1/'
const level = process.env.LOG_LEVEL || 'debug';
const brokerAddress = process.env.MQTT_BROKER || 'localhost';
const path = process.env.ARDUINO_PORT || '/dev/ttyUSB0';
const baudRate =process.env.ARDUINO_BAUD_RATE || 9600;

const logger = winston.createLogger({
  level,
  defaultMeta: { service: name },
  transports: [
    new winston.transports.File({ filename: `${name}.log` }),
    new winston.transports.Console({ format: winston.format.simple()  }),
  ],
});

const mqtt = require('async-mqtt').connect('mqtt://' + brokerAddress, { will: { payload: '0', topic: `${mqttPrefix}status/${name}` } });

const port = new SerialPort(path, { baudRate }, (e) => {
  if (e) {
    logger.log('error', 'Could not connect to serial port: ' + e, e);
    process.exit(1);
  }
});

const parser = new Readline()
port.pipe(parser)

const serialIn$ = new Subject(); // messages received over serial published on this Subject
const serialOut$ = new Subject(); // messages published on this Subject get sent over serial. Include a newline ('\n')
const mqttPublish$ = new Subject(); // messages published on this Subject get sent over MQTT. Message format: { topic: '...', message: '...' }

const motorRightToSet$ = new Subject(); // value that should be set from MQTT
const motorLeftToSet$ = new Subject(); // value that should be set from MQTT
const motorValuesToSet$ = combineLatest(
  motorRightToSet$.pipe(startWith(0)),
  motorLeftToSet$.pipe(startWith(0)),
).pipe(auditTime(100), map( ([ right, left ]) => ({ right, left }) ));

// Debug
mqttPublish$.subscribe(n => logger.log('silly', 'To be sent over MQTT: ' + JSON.stringify(n)));
serialIn$.subscribe(n => logger.log('silly', 'Received over serial: ' + JSON.stringify(n)));
serialOut$.subscribe(n => logger.log('silly', 'Sent out over serial: ' + JSON.stringify(n)));
motorValuesToSet$.subscribe(n => logger.log('debug', 'Set motor values to ' + JSON.stringify(n)));

// Publish serial in and out over MQTT
serialIn$.subscribe( message => mqttPublish$.next( { topic: `${mqttPrefix}status/serial/in`, message } ));
serialOut$.subscribe(message => mqttPublish$.next( { topic: `${mqttPrefix}status/serial/out`, message } ));

// Receive data from serial hook
parser.on('data', line => serialIn$.next(line));
parser.on('error', e => logger.log('Error with serial port (or parser): ' + e, e));

// Put data on serial port
serialOut$.subscribe(data => port.write(data));

// Put received motor values on serial out
motorValuesToSet$.subscribe(motorValues => {
  // See Arduino source code for format - basically 'r-255', 'l 255', 'l  10', 'r   0', ...
  const formatMotorValue = (value) => {
    const firstChar = value < 0 ? '-' : ' ';

    return firstChar + leftPad(Math.abs(value).toString(), 3, ' ') + '\n';
  };

  serialOut$.next('l' + formatMotorValue(motorValues.left));
  serialOut$.next('r' + formatMotorValue(motorValues.right));
});

// Publish data from serial in to MQTT topics
serialIn$.pipe(
  map(line => {
    try {
      return JSON.parse(line);
    } catch(e) {
      logger.log('warn', `${name} WARNING could not parse JSON line (if starting: this is expected): ` + line, line);
    }
  }),
  filter(json => json),
).subscribe(async (input) => {
  // Only publishes when index is set in obj
  const conditionalPublish = async (topic, index) => {
    if (input[index]) { 
      mqttPublish$.next({ topic: `${mqttPrefix}${topic}`, message: input[index].toString() });
    }
  };

  conditionalPublish('sensors/acceleration/x', 'mx');
  conditionalPublish('sensors/acceleration/y', 'my');
  conditionalPublish('sensors/acceleration/z', 'mz');

  conditionalPublish('sensors/gyroscope/x', 'gx');
  conditionalPublish('sensors/gyroscope/y', 'gy');
  conditionalPublish('sensors/gyroscope/z', 'gz');

  conditionalPublish('sensors/magnetometer/x', 'mx');
  conditionalPublish('sensors/magnetometer/y', 'my');
  conditionalPublish('sensors/magnetometer/z', 'mz');

  conditionalPublish('status/motor/left', 'left');
  conditionalPublish('status/motor/right', 'right');
});

// Publish MQTT messages when MQTT connection ready
mqtt.on('connect', mqttConnected);

async function mqttConnected() {
  logger.log('info', `${name} MQTT connected`);

	try {
    // Publish messages
    mqttPublish$.subscribe(message => {
      mqtt.publish(message.topic, message.message).catch(err => logger.log('error', `Could not publish to MQTT topic ${message.topic}`, err));
    });

    // Publish online status
		await mqtt.publish(`${mqttPrefix}status/${name}`, '1');

	} catch (e){
    logger.log('error', `${name} Could not publish to MQTT broker`, e.stack)
		console.log(e.stack);
		process.exit();
	}
}

// Subscribe to motor messages
mqtt.subscribe([ `${mqttPrefix}actuators/motor/left`, `${mqttPrefix}actuators/motor/right` ], (err, granted) => {
  if (err) {
    logger.log('error', 'Error in subscription to MQTT motors', err);
  }
});

// Handle messages from MQTT
mqtt.on('message', (topic, message) => {
  switch (topic) {
    case `${mqttPrefix}actuators/motor/left`:
      motorLeftToSet$.next(parseInt(message.toString()));
      break;
    case `${mqttPrefix}actuators/motor/right`:
      motorRightToSet$.next(parseInt(message.toString()));
      break;

    default:
      logger.log('warn', `Received message on unexpected topic: ${topic}. Message was ${message.toString()}`)
  }
});

