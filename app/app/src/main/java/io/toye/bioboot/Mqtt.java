package io.toye.bioboot;

import android.content.Context;
import android.location.Location;
import android.util.Log;

import org.eclipse.paho.android.service.MqttAndroidClient;
import org.eclipse.paho.client.mqttv3.DisconnectedBufferOptions;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttCallbackExtended;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.json.JSONException;
import org.json.JSONObject;

public class Mqtt {

    public interface OnMotorUpdateCallback {
        void onLeftMotorUpdate(int value);
        void onRightMotorUpdate(int value);
    }

    private MqttAndroidClient mqttAndroidClient;

    private final String serverUri = "tcp://192.168.1.31:1883";

    private final String clientId = "AndroidClient_" + MqttClient.generateClientId();
    private final String subscriptionTopic = "boat/#";

    private OnMotorUpdateCallback onMotorUpdateCallback;

    private static final String TAG = "MQTT";

    public Mqtt(Context context){
        mqttAndroidClient = new MqttAndroidClient(context, serverUri, clientId);

        mqttAndroidClient.setCallback(new MqttCallbackExtended() {
            @Override
            public void connectComplete(boolean b, String s) {
                Log.i(TAG, "MQTT connect complete " + s);
            }

            @Override
            public void connectionLost(Throwable throwable) {
                Log.w(TAG, "MQTT connection lost", throwable);
            }

            @Override
            public void messageArrived(String topic, MqttMessage message) throws Exception {
                Log.d(TAG, "message arrived: " + message.toString());

                if (topic.endsWith("actuators/motor/right")) {
                    if (onMotorUpdateCallback != null) {
                        onMotorUpdateCallback.onRightMotorUpdate(Integer.parseInt(new String(message.getPayload())));
                    }
                } else if(topic.endsWith("actuators/motor/left")) {
                    if (onMotorUpdateCallback != null) {
                        onMotorUpdateCallback.onLeftMotorUpdate(Integer.parseInt(new String(message.getPayload())));
                    }
                } else {
                    Log.d(TAG, "Unhandled messages in topic " + topic);
                }
            }

            @Override
            public void deliveryComplete(IMqttDeliveryToken token) {

            }
        });

        connect();
    }

    public void onMotorUpdate(OnMotorUpdateCallback callback) {
        this.onMotorUpdateCallback = callback;
    }

    public void sendLocation(Location location) {
        if (mqttAndroidClient == null || !mqttAndroidClient.isConnected()) {
            Log.w(TAG, "Not sending location to MQTT broker: not connected to it");
            return;
        }

        JSONObject jsonObject = new JSONObject();

        try {
            jsonObject.put("location", packLocationToJSON(location));
        } catch (JSONException e) {
            Log.e(TAG, "Problem while creating request JSON", e);
        }

        Log.d(TAG, "Sending over data to MQTT: " + jsonObject.toString());

        MqttMessage message = new MqttMessage(jsonObject.toString().getBytes());

        try {
            mqttAndroidClient.publish("boat/1/sensors/location", message);
        } catch (MqttException e) {
            Log.e(TAG, "Could not publish MQTT location message", e);
            e.printStackTrace();
        }

    }

    private static JSONObject packLocationToJSON(Location location) {
        JSONObject jsonObject = new JSONObject();

        try {
            if (location == null) {
                return null;
            }

            jsonObject.put("lat", location.getLatitude());
            jsonObject.put("lon", location.getLongitude());
            jsonObject.put("accuracy", location.getAccuracy());
            jsonObject.put("bearing", location.getBearing());
            jsonObject.put("altitude", location.getAltitude());
            jsonObject.put("speed", location.getSpeed());
            jsonObject.put("provider", location.getProvider());

            return jsonObject;
        } catch (JSONException e) {
            Log.e(TAG, "JSONException encountered while trying to serialize location");
            e.printStackTrace();
            return new JSONObject();
        }
    }


    private void connect(){
        MqttConnectOptions mqttConnectOptions = new MqttConnectOptions();
        mqttConnectOptions.setAutomaticReconnect(true);
        mqttConnectOptions.setCleanSession(false);

        try {

            mqttAndroidClient.connect(mqttConnectOptions, null, new IMqttActionListener() {
                @Override
                public void onSuccess(IMqttToken asyncActionToken) {
                    Log.i(TAG, "Connected to MQTT broker");

                    DisconnectedBufferOptions disconnectedBufferOptions = new DisconnectedBufferOptions();
                    disconnectedBufferOptions.setBufferEnabled(true);
                    disconnectedBufferOptions.setBufferSize(100);
                    disconnectedBufferOptions.setPersistBuffer(false);
                    disconnectedBufferOptions.setDeleteOldestMessages(false);
                    mqttAndroidClient.setBufferOpts(disconnectedBufferOptions);
                    subscribeToTopic();
                }

                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    Log.w("Mqtt", "Failed to connect to: " + serverUri + exception.toString());
                }
            });


        } catch (MqttException ex) {
            Log.e(TAG, "MQTT exception while trying to connect", ex);
            ex.printStackTrace();
        }
    }


    private void subscribeToTopic() {
        try {
            mqttAndroidClient.subscribe(subscriptionTopic, 0, null, new IMqttActionListener() {
                @Override
                public void onSuccess(IMqttToken asyncActionToken) {
                    Log.w(TAG,"Subscribed to actuator topic!");
                }

                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    Log.w(TAG, "Could not subscribe");
                }
            });

        } catch (MqttException ex) {
            Log.e(TAG, "Could not subscribe", ex);
            ex.printStackTrace();
        }
    }
}
