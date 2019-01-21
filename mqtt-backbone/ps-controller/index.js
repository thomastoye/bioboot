const { Observable, Subject, ReplaySubject, from, of, combineLatest } = require('rxjs');
const { map, filter, startWith } = require('rxjs/operators');
const winston = require('winston');
const dualShock = require('./node-dualshock-controller/src/dualshock');

const controller = dualShock({ config: "dualShock3" });

const name = 'ps-controller';

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
const controllerError$ = new Subject();

const publishUnderPrefix = (topic, message) => mqttPublish$.next({
  topic: `${mqttPrefix}sensors/controller/${topic}`,
  message: message.toString(),
});

// Debug
controllerError$.subscribe(err => logger.log('error', 'Error with Dualshock controller: ' + err, err));
mqttPublish$.subscribe(data => logger.log('silly', `publishing to topic ${data.topic}: ${JSON.stringify(data.message)}`))

// Publish controller erors
controller.on('error', err => controllerError$.next(err));

// Publish controller values
controller.on('connected', () => {
  logger.log('info', 'Controller connected');
  publishUnderPrefix('connected', '1');
});

controller.on('connection:change', data => publishUnderPrefix('connection', data));
controller.on('battery:change', data => publishUnderPrefix('battery', data));

controller.on('left:move', data => {
  publishUnderPrefix('joystick/left/x', data.x);
  publishUnderPrefix('joystick/left/y', data.y);
});

controller.on('right:move', data => {
  publishUnderPrefix('joystick/right/x', data.x);
  publishUnderPrefix('joystick/right/y', data.y);
});

[ 'l1', 'l2', 'r1', 'r2', 'triangle', 'circle', 'x', 'square', 'start', 'select', 'dpadUp', 'dpadDown', 'dpadLeft', 'dpadRight' ].forEach(button => {
  controller.on(`${button}:press`, () => publishUnderPrefix(`${button}/pressed`, '1'));
  controller.on(`${button}:release`, () => publishUnderPrefix(`${button}/pressed`, '0'));
});


// Publish MQTT messages when MQTT connection ready
mqtt.on('connect', mqttConnected);

async function mqttConnected() {
  logger.log('info', `${name} MQTT connected`);

  try {
    // Publish messages
    mqttPublish$.subscribe(message => {
      if (!message || !message.topic || !message.message) {
        logger.log('error', `Error while publishing MQTT message: you tried to publish an undefined message or topic: ${JSON.stringify(message)}`);
        return;
      }

      mqtt.publish(message.topic, message.message).catch(err => {
        logger.log('error', `Could not publish to MQTT topic ${message.topic}`, err)
      });
    });

    // Publish online status
    await mqtt.publish(`${mqttPrefix}status/${name}`, '1');

  } catch (e){
    logger.log('error', `${name} Could not publish to MQTT broker`, e.stack)
    console.log(e.stack);
    process.exit();
  }
}

// Subscribe to actuator topics
mqtt.subscribe([ `${mqttPrefix}actuators/controller/rumble/left`, `${mqttPrefix}actuators/rumble/right` ], (err, granted) => {
  if (err) {
    logger.log('error', 'Error in subscription to MQTT actuators', err);
  }
});


// Handle messages from MQTT

const parseRumbleLevel = (rumble) => {
  return parseInt(rumble);
};

mqtt.on('message', (topic, message) => {
  logger.log('silly', `Incoming message on ${topic}: ${message}`);

  switch (topic) {
    case `${mqttPrefix}actuators/controller/rumble/left`:
      controller.setExtras({ rumbleLeft: parseRumbleLevel(message) });
      break;

    case `${mqttPrefix}actuators/controller/rumble/right`:
      controller.setExtras({ rumbleLeft: parseRumbleLevel(message) });
      break;

    default:
      logger.log('warn', `Received message on unexpected topic: ${topic}. Message was ${message.toString()}`)
  }
});



