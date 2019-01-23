import paho.mqtt.client as mqtt
import copy
import random
import string

def random_string():
    # Used for client name
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))


data = {
  'acceleration': { 'x': 0, 'y': 0, 'z': 0 },
  'gyroscope': { 'x': 0, 'y': 0, 'z': 0 },
  'magnetometer': { 'x': 0, 'y': 0, 'z': 0 },
}

# TODO Probably want to use something other than global state here
def get_current_data():
    return data

# TODO Probably want to use something other than global state here
def set_current_data(new_data):
    print('data updated to')
    print(new_data)
    data = new_data


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribe to topics
    topics = [
      'boat/1/sensors/acceleration/x',
      'boat/1/sensors/acceleration/y',
      'boat/1/sensors/acceleration/z',
      'boat/1/sensors/gyroscope/x',
      'boat/1/sensors/gyroscope/y',
      'boat/1/sensors/gyroscope/z',
      'boat/1/sensors/magnetometer/x',
      'boat/1/sensors/magnetometer/y',
      'boat/1/sensors/magnetometer/z'
    ]

    for topic in topics:
        client.subscribe(topic)


#The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    try:
        result_data = copy.deepcopy(data) # Deep copy so we don't modify existing data
        value = int(str(msg.payload.decode('utf-8')))

        print('value ' +str(value))

        if msg.topic.endswith('acceleration/x'):
            result_data['acceleration']['x'] = value
        elif msg.topic.endswith('acceleration/y'):
            result_data['acceleration']['y'] = value
        elif msg.topic.endswith('acceleration/z'):
            result_data['acceleration']['z'] = value
        elif msg.topic.endswith('gyroscope/x'):
            result_data['gyroscope']['x'] = value
        elif msg.topic.endswith('gyroscope/y'):
            result_data['gyroscope']['y'] = value
        elif msg.topic.endswith('gyroscope/z'):
            result_data['gyroscope']['z'] = value
        elif msg.topic.endswith('magnetometer/x'):
            result_data['magnetometer']['x'] = value
        elif msg.topic.endswith('magnetometer/y'):
            result_data['magnetometer']['y'] = value
        elif msg.topic.endswith('magnetometer/z'):
            result_data['magnetometer']['z'] = value
        else:
            print('WARNING Unknown topic ' + msg.topic)

        set_current_data(result_data)

    except Exception as e:
        print('Exception encountered in on_message!')
        print(e)

client = mqtt.Client('autopilot_'+random_string(), clean_session=True)
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()


