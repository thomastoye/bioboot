package bioboot.ugent.toye.io.bioboot;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.View;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.EditText;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import org.json.JSONException;
import org.json.JSONObject;

public class MainActivity extends AppCompatActivity {
    private static final String TAG = "MyActivity";

    private RequestQueue queue;
    private Context mainActivity;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        mainActivity = this;
        queue = Volley.newRequestQueue(this);

        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Snackbar.make(view, "Deze knop doet niets ATM", Snackbar.LENGTH_LONG)
                        .setAction("Action", null).show();
            }
        });

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

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    private String getUrl() {
        EditText url = (EditText) findViewById(R.id.backbone_url);
        return url.getText().toString();
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
                        //mTextView.setText("Response: " + response.toString());
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
