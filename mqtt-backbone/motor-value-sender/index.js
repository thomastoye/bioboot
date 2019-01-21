const { Observable, Subject, ReplaySubject, from, of, combineLatest } = require('rxjs');
const { map, filter, startWith } = require('rxjs/operators');
const winston = require('winston');

const name = 'motor-value-sender';

const mqttPrefix = 'boat/1/'
const level = process.env.LOG_LEVEL || 'debug';
const brokerAddress = process.env.MQTT_BROKER || 'localhost';

const logger = winston.createLogger({
  level,
  defaultMeta: { service: name },
  transports: [
    new winston.transports.File({ filename: `${name}.log` }),
    new winston.transports.Console({ format: winston.format.simple()  }),
  ],
});

const mqtt = require('async-mqtt').connect('mqtt://' + brokerAddress, { will: { payload: '0', topic: `${mqttPrefix}status/${name}` } });

const mqttPublish$ = new Subject(); // messages published on this Subject get sent over MQTT. Message format: { topic: '...', message: '...' }

const joystickX$ = new Subject();
const joystickY$ = new Subject();

const joystick$ = combineLatest(
  joystickX$.pipe(startWith(0)),
  joystickY$.pipe(startWith(0)),
).pipe(map( ([ x, y ]) => ({ x, y }) ));

const motorOut$ = new Subject(); // Motor values to publish. Format { x: number, y: number }

// Debug
mqttPublish$.subscribe(n => logger.log('silly', 'To be sent over MQTT: ' + JSON.stringify(n)));
joystick$.subscribe(data => logger.log('silly', `New values for joystick, x=${data.x}, y=${data.y}`));

// Publish motor values
joystick$.subscribe( data => {
  mqttPublish$.next({ topic: `${mqttPrefix}actuators/motor/left`, message: data.y.toString() });
  mqttPublish$.next({ topic: `${mqttPrefix}actuators/motor/right`, message: data.y.toString() });
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
mqtt.subscribe([ `${mqttPrefix}sensors/controller/joystick/left/x`, `${mqttPrefix}sensors/controller/joystick/left/y` ], (err, granted) => {
  if (err) {
    logger.log('error', 'Error in subscription to MQTT motors', err);
  }
});

// Handle messages from MQTT
mqtt.on('message', (topic, message) => {
  switch (topic) {
    case `${mqttPrefix}sensors/controller/joystick/left/x`:
      joystickX$.next(parseInt(message));
      break;
    case `${mqttPrefix}sensors/controller/joystick/left/y`:
      joystickY$.next(parseInt(message));
      break;

    default:
      logger.log('warn', `Received message on unexpected topic: ${topic}. Message was ${message.toString()}`)
  }
});

