const { Observable, Subject, BehaviorSubject, ReplaySubject, from, of, combineLatest } = require('rxjs');
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

const speed$ = new BehaviorSubject(0);

const joystickX$ = new Subject();
const joystickY$ = new Subject();

const r1$ = new Subject(); // true if pressed, false if not
const l1$ = new Subject(); // true if pressed, false if not
const r2$ = new Subject(); // true if pressed, false if not
const l2$ = new Subject(); // true if pressed, false if not
const cross$ = new Subject(); // true if pressed, false if not

// Used to cap value, e.g. cap speed e [ -255, 255 ]: capValue(speed, -255, 255)
const capValue = (value, min, max) => Math.min(Math.max(value, min), max);

// Debug
mqttPublish$.subscribe(n => logger.log('silly', 'To be sent over MQTT: ' + JSON.stringify(n)));
combineLatest(
    joystickX$.pipe(startWith(0)),
    joystickY$.pipe(startWith(0)),
).pipe(map(([x, y]) => ({x, y}))).subscribe(data => logger.log('silly', `New values for joystick, x=${data.x}, y=${data.y}`));
speed$.subscribe(speed => logger.log('debug', 'Speed set to ' + speed.toString()));

// Change speed on r1 and l1 press
combineLatest(
    r1$.pipe(startWith(0)),
    l1$.pipe(startWith(0)),
).pipe(map(( [r1, l1] ) => {
  // maps speed change
  if (r1) {
    return 20;
  } else if(l1) {
    return -20;
  } else {
    return 0;
  }
})).subscribe(change => speed$.next(capValue(speed$.getValue() + change, -255, 255)));

// Reset speed on 'X' button press
cross$.pipe(pressed => pressed).subscribe(() => speed$.next(0));
// Set speed to max reverse on L2 press
l2$.pipe(pressed => pressed).subscribe(() => speed$.next(-255));
// Set speed to max on R2 press
r2$.pipe(pressed => pressed).subscribe(() => speed$.next(255));

// Calculate motor values based on joystick x and speed

/**
 * @param speed The total speed, e [-255, 255]
 * @param deltaJoystick How much the joystick is leaning towards the direction the current motor controls, e [ -128, 127 ]
 */
const calcMotorSpeed = (speed, deltaJoystick) => {
    if (deltaJoystick > -8) {
      return speed;
    } else {
      // linear function from (-128, -speed) to (-8, speed)
      return speed + 2 * (speed / 120) * (deltaJoystick + 8);
    }
};

combineLatest(
    speed$.pipe(startWith(0)),
    joystickX$.pipe(startWith(128)),
).pipe(map(([ speed, x ]) => ( {x, speed }))).subscribe( data => {
  logger.log('debug', 'delta joy ' + (data.x - 128));
  const deltaJoystick = data.x - 128;

  mqttPublish$.next({ topic: `${mqttPrefix}actuators/motor/left`, message: calcMotorSpeed(data.speed, -1 * deltaJoystick).toString() });
  mqttPublish$.next({ topic: `${mqttPrefix}actuators/motor/right`, message: calcMotorSpeed(data.speed, deltaJoystick).toString() });
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
mqtt.subscribe([
  `${mqttPrefix}sensors/controller/joystick/left/x`,
  `${mqttPrefix}sensors/controller/joystick/left/y`,
  `${mqttPrefix}sensors/controller/r1/pressed`,
  `${mqttPrefix}sensors/controller/l1/pressed`,
  `${mqttPrefix}sensors/controller/r2/pressed`,
  `${mqttPrefix}sensors/controller/l2/pressed`,
  `${mqttPrefix}sensors/controller/x/pressed`,
], (err, granted) => {
  if (err) {
    logger.log('error', 'Error in subscription to MQTT motors', err);
  }
});

// Handle messages from MQTT
mqtt.on('message', (topic, message) => {
  logger.log('silly', `Received message on ${topic}: ${message}`);

  switch (topic) {
    case `${mqttPrefix}sensors/controller/joystick/left/x`:
      joystickX$.next(parseInt(message));
      break;
    case `${mqttPrefix}sensors/controller/joystick/left/y`:
      joystickY$.next(parseInt(message));
      break;

    case `${mqttPrefix}sensors/controller/r1/pressed`:
      r1$.next(message.toString() === '1');
      break;

    case `${mqttPrefix}sensors/controller/l1/pressed`:
      l1$.next(message.toString() === '1');
      break;

    case `${mqttPrefix}sensors/controller/r2/pressed`:
      r2$.next(message.toString() === '1');
      break;

    case `${mqttPrefix}sensors/controller/l2/pressed`:
      l2$.next(message.toString() === '1');
      break;

    case `${mqttPrefix}sensors/controller/x/pressed`:
      cross$.next(message.toString() === '1');
      break;

    default:
      logger.log('warn', `Received message on unexpected topic: ${topic}. Message was ${message.toString()}`)
  }
});

