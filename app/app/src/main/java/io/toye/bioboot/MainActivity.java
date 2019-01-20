package io.toye.bioboot;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.os.Handler;
import android.support.annotation.NonNull;
import android.support.design.widget.BottomNavigationView;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.MenuItem;
import android.view.View;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.TextView;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.eclipse.paho.android.service.MqttAndroidClient;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttMessageListener;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.json.JSONException;
import org.json.JSONObject;

import de.nitri.gauge.Gauge;

public class MainActivity extends AppCompatActivity {
    private TextView mTextMessage;

    private static final String TAG = "MainActivity";

    private TextView statusMotorLeft;
    private TextView statusMotorRight;

    private ProgressBar barMotorLeft;
    private ProgressBar barMotorRight;

    private Gauge gaugeMotorRight;
    private Gauge gaugeMotorLeft;

    Mqtt mqtt;


    private BottomNavigationView.OnNavigationItemSelectedListener mOnNavigationItemSelectedListener
            = new BottomNavigationView.OnNavigationItemSelectedListener() {

        @Override
        public boolean onNavigationItemSelected(@NonNull MenuItem item) {
            switch (item.getItemId()) {
                case R.id.navigation_home:
                    mTextMessage.setText(R.string.title_home);
                    return true;
                case R.id.navigation_dashboard:
                    mTextMessage.setText(R.string.title_dashboard);
                    return true;
                case R.id.navigation_notifications:
                    mTextMessage.setText(R.string.title_notifications);
                    return true;
            }
            return false;
        }
    };

    @Override
    protected void onResume() {
        super.onResume();
    }

    @Override
    protected void onPause() {
        super.onPause();
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mTextMessage = findViewById(R.id.message);
        BottomNavigationView navigation = findViewById(R.id.navigation);
        navigation.setOnNavigationItemSelectedListener(mOnNavigationItemSelectedListener);

        gaugeMotorRight = findViewById(R.id.motor_right_gauge);
        gaugeMotorLeft = findViewById(R.id.motor_left_gauge);

        Log.i(TAG, "Main activity start");

        // Request location permission
        ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}, 1);

        // Register the listener with the Location Manager to receive location updates
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED && ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            Log.e(TAG, "Location permissions not granted!");
            return;
        } else {
            Log.d(TAG, "Location permissions are ok");
        }

        // Acquire a reference to the system Location Manager
        LocationManager locationManager = (LocationManager) getApplicationContext().getSystemService(Context.LOCATION_SERVICE);

        // Define a listener that responds to location updates
        LocationListener locationListener = new LocationListener() {
            public void onLocationChanged(Location location) {
                Log.d(TAG, "LocationListener.onLocationChanged");

                if (location == null) {
                    Log.i(TAG, "Location was null, not sending over");
                } else {
                    if (mqtt != null) {
                        mqtt.sendLocation(location);
                    } else {
                        Log.d(TAG, "Could not send location: mqtt is null");
                    }
                }

            }

            public void onStatusChanged(String provider, int status, Bundle extras) {
                Log.d(TAG, "LocationListener.onStatusChanged; provider=" + provider + " status=" + status);
            }

            public void onProviderEnabled(String provider) {
                Log.d(TAG, "LocationListener.onProviderEnabled; provider=" + provider);
            }

            public void onProviderDisabled(String provider) {
                Log.d(TAG, "LocationListener.onProviderDisabled; provider=" + provider);
            }
        };

        // Attach listener to GPS and network providers
        locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 0, 0, locationListener);
        locationManager.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 0, 0, locationListener);

        connectMqtt();
    }

    @Override
    protected void onStop() {
        super.onStop();
    }

    private void connectMqtt() {
        mqtt = new Mqtt(getApplicationContext());

        mqtt.onMotorUpdate(new Mqtt.OnMotorUpdateCallback() {
            @Override
            public void onLeftMotorUpdate(int value) {
                Log.i(TAG, "Received new motor left value: " + value);

                //gaugeMotorLeft.moveToValue(value); // Nice, but not fast enough
                gaugeMotorLeft.setValue(value);
                gaugeMotorLeft.setLowerText(""+value);
            }

            @Override
            public void onRightMotorUpdate(int value) {
                Log.i(TAG, "Received new motor right value: " + value);

                //gaugeMotorRight.moveToValue(value); // Nice, but not fast enough
                gaugeMotorRight.setValue(value);
                gaugeMotorRight.setLowerText(""+value);
            }
        });
    }
}
