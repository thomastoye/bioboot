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

import org.json.JSONException;
import org.json.JSONObject;

public class MainActivity extends AppCompatActivity {

    private TextView mTextMessage;

    private static final String TAG = "MainActivity";

    private RequestQueue queue;
    private Context mainActivity;

    private TextView statusMotorLeft;
    private TextView statusMotorRight;

    private ProgressBar barMotorLeft;
    private ProgressBar barMotorRight;

    Handler backbonePullDataHandler = new Handler();
    int backbonePullDataInterval = 500;
    Runnable backbonePullDataRunnable;

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
        backbonePullDataHandler.postDelayed( backbonePullDataRunnable = new Runnable() {
            public void run() {
                getInformation(getUrl());

                backbonePullDataHandler.postDelayed(backbonePullDataRunnable, backbonePullDataInterval);
            }
        }, backbonePullDataInterval);

        super.onResume();
    }

    @Override
    protected void onPause() {
        backbonePullDataHandler.removeCallbacks(backbonePullDataRunnable);

        super.onPause();
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mTextMessage = (TextView) findViewById(R.id.message);
        BottomNavigationView navigation = (BottomNavigationView) findViewById(R.id.navigation);
        navigation.setOnNavigationItemSelectedListener(mOnNavigationItemSelectedListener);

        mainActivity = this;
        queue = Volley.newRequestQueue(this);

        setContentView(R.layout.activity_main);

        statusMotorLeft = (TextView) findViewById(R.id.status_motor_left);
        statusMotorRight = (TextView) findViewById(R.id.status_motor_right);

        barMotorLeft = (ProgressBar) findViewById(R.id.bar_motor_left);
        barMotorRight = (ProgressBar) findViewById(R.id.bar_motor_right);

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
        LocationManager locationManager = (LocationManager) mainActivity.getSystemService(Context.LOCATION_SERVICE);

        // Define a listener that responds to location updates
        LocationListener locationListener = new LocationListener() {
            public void onLocationChanged(Location location) {
                Log.d(TAG, "LocationListener.onLocationChanged");

                if (location == null) {
                    Log.i(TAG, "Location was null, not sending over");
                } else {
                    sendInformation(getUrl(), location);
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
    }

    private String getUrl() {
        EditText url = (EditText) findViewById(R.id.backbone_url);
        return url.getText().toString();
    }

    private void getInformation(String url) {
        Log.d(TAG, "Getting current status from backbone...");

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.GET, url + "/pull", null, new Response.Listener<JSONObject>() {

                    @Override
                    public void onResponse(JSONObject response) {
                        Log.d(TAG, "Successfully received data from backbone");
                        try {
                            int left = Integer.parseInt(response.getString("left"));
                            int right = Integer.parseInt(response.getString("right"));
                            Log.d(TAG, "Received from backbone: right="+right+", left="+left);

                            statusMotorLeft.setText("" + left);
                            statusMotorRight.setText("" + right);
                            barMotorLeft.setProgress(left);
                            barMotorRight.setProgress(right);
                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                    }
                }, new Response.ErrorListener() {

                    @Override
                    public void onErrorResponse(VolleyError error) {
                        Snackbar.make(findViewById(R.id.container), "Kon data niet ophalen", Snackbar.LENGTH_SHORT).show();
                        Log.e(TAG, "Could not pull data from backbone", error);
                    }
                });

        jsonObjectRequest.setShouldCache(false);

        queue.add(jsonObjectRequest);
    }

    private void sendInformation(String url, Location location) {

        JSONObject jsonObject = new JSONObject();

        try {
            jsonObject.put("location", packLocationToJSON(location));
        } catch (JSONException e) {
            Log.e(TAG, "Problem while creating request JSON", e);
        }

        Log.d(TAG, "Sending over data to backbone: " + jsonObject.toString());
        Log.d(TAG, "URL to send to (should not end in '/'): " + url);

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest
                (Request.Method.POST, url + "/push", jsonObject, new Response.Listener<JSONObject>() {

                    @Override
                    public void onResponse(JSONObject response) {
                        Log.d(TAG, "Successfully sent data to backbone");
                    }
                }, new Response.ErrorListener() {

                    @Override
                    public void onErrorResponse(VolleyError error) {
                        // TODO: Handle error
                        Log.e(TAG, "Error while sending data to backbone", error);
                    }
                });


        // Add the request to the RequestQueue.
        queue.add(jsonObjectRequest);
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

}
