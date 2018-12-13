package bioboot.ugent.toye.io.bioboot;

import android.Manifest;
import android.annotation.SuppressLint;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.os.Message;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.os.Handler;
import android.view.View;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Toast;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.Set;
import java.util.UUID;

public class MainActivity extends AppCompatActivity {
    private static final String TAG = "MyActivity";
//    public static final String BACKBONE_BLUETOOTH_MAC = "A0:A8:CD:9F:08:89"; // Laptop Toye
    public static final String BACKBONE_BLUETOOTH_MAC = "DC:A2:66:66:30:3E"; // Laptop Nicolas
    public static final UUID BLUETOOTH_CONNECTION_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");

    // Message types sent from the BluetoothReadService Handler
    public static final int MESSAGE_STATE_CHANGE = 1;
    public static final int MESSAGE_READ = 2;
    public static final int MESSAGE_WRITE = 3;
    public static final int MESSAGE_DEVICE_NAME = 4;
    public static final int MESSAGE_TOAST = 5;

    // Key names received from the BluetoothChatService Handler
    public static final String DEVICE_NAME = "device_name";
    public static final String TOAST = "toast";

    // Name of the connected device
    private String mConnectedDeviceName = null;

    // The REQUEST_ENABLE_BT constant passed to startActivityForResult() is a locally defined integer that must be greater than 0.
    // The system passes this constant back to you in your onActivityResult() implementation as the requestCode parameter.
    public static final int REQUEST_ENABLE_BT = 1000;

    private static BluetoothSerialService mSerialService = null;

    Context mainActivity;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        mainActivity = this;

        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                mSerialService.write("Hello World!".getBytes());
                Snackbar.make(view, "Sent text over BT!", Snackbar.LENGTH_LONG)
                        .setAction("Action", null).show();
            }
        });

        FloatingActionButton locationFab = (FloatingActionButton) findViewById(R.id.location);
        locationFab.setOnClickListener(new View.OnClickListener() {
            @SuppressLint("MissingPermission")
            @Override
            public void onClick(View v) {
                // Acquire a reference to the system Location Manager
                LocationManager locationManager = (LocationManager) mainActivity.getSystemService(Context.LOCATION_SERVICE);

                Location location = locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER);

                if (location == null) {
                    Log.e(TAG, "Could not get last known location! location was null.");
                    return;
                }

                // Called when a new location is found by the network location provider.
                // Pack location in JSON object and send it over BT
                JSONObject jsonObject = MainActivity.packLocationToJSON(location);

                if (jsonObject == null) {
                    Log.i(TAG, "Location was null, not sending over Bluetooth");
                } else {
                    Log.d(TAG, "GPS information: " + jsonObject.toString());
                    mSerialService.write((jsonObject.toString() + '\n').getBytes());
                }

            }
        });

        Log.i(TAG, "Main activity start");

        BluetoothAdapter mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        if (mBluetoothAdapter == null) {
            // Device doesn't support Bluetooth
            Log.e(TAG, "Device does not support Bluetooth!");
        }

        if (!mBluetoothAdapter.isEnabled()) {
            Log.d(TAG, "Bluetooth not enabled, enabling...");
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT);
        }

        Set<BluetoothDevice> pairedDevices = mBluetoothAdapter.getBondedDevices();

        BluetoothDevice backboneDevice = null;

        if (pairedDevices.size() > 0) {
            // There are paired devices. Get the name and address of each paired device.
            for (BluetoothDevice device : pairedDevices) {
                String deviceName = device.getName();
                String deviceHardwareAddress = device.getAddress(); // MAC address

                if (deviceHardwareAddress.equals(BACKBONE_BLUETOOTH_MAC)) {
                    mBluetoothAdapter.cancelDiscovery();
                    backboneDevice = device;
                    Log.i(TAG, "Backbone found!");
                    break;
                } else {
                    Log.d(TAG, "Device found, but not backbone: " + deviceName + " -- " + deviceHardwareAddress + " (looking for " + BACKBONE_BLUETOOTH_MAC + ")");
                }
            }
        }

        if (backboneDevice == null) {
            Log.e(TAG, "Backbone device not found!");
        }

        mSerialService = new BluetoothSerialService(this, mHandlerBT);
        mSerialService.setAllowInsecureConnections(true);
        mSerialService.connect(backboneDevice);

        // Request location permission
        ActivityCompat.requestPermissions(this,new String[] {Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}, 1);

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

                // Called when a new location is found by the network location provider.
                // Pack location in JSON object and send it over BT
                JSONObject jsonObject = MainActivity.packLocationToJSON(location);

                if (jsonObject == null) {
                    Log.i(TAG, "Location was null, not sending over Bluetooth");
                } else {
                    Log.d(TAG, "GPS information: " + jsonObject.toString());
                    mSerialService.write((jsonObject.toString() + '\n').getBytes());
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

    // The Handler that gets information back from the BluetoothService
    private final Handler mHandlerBT = new Handler() {

        @Override
        public void handleMessage(Message msg) {
            switch (msg.what) {
                case MESSAGE_STATE_CHANGE:
                    Log.d(TAG, "MESSAGE_STATE_CHANGE: " + msg.arg1);
                    switch (msg.arg1) {
                        case BluetoothSerialService.STATE_CONNECTED:
//                            if (mMenuItemConnect != null) {
//                                mMenuItemConnect.setIcon(android.R.drawable.ic_menu_close_clear_cancel);
//                                mMenuItemConnect.setTitle(R.string.disconnect);
//                            }
//
//                            mInputManager.showSoftInput(mEmulatorView, InputMethodManager.SHOW_IMPLICIT);
//
//                            mTitle.setText( R.string.title_connected_to );
//                            mTitle.append(" " + mConnectedDeviceName);
//                            break;
                            Log.d(TAG, "BluetoothSerialService.STATE_CONNECTED");
                            break;

                        case BluetoothSerialService.STATE_CONNECTING:
                            Log.d(TAG, "BluetoothSerialService.STATE_CONNECTING");
//                            mTitle.setText(R.string.title_connecting);
                            break;

                        case BluetoothSerialService.STATE_LISTEN:
                        case BluetoothSerialService.STATE_NONE:
//                            if (mMenuItemConnect != null) {
//                                mMenuItemConnect.setIcon(android.R.drawable.ic_menu_search);
//                                mMenuItemConnect.setTitle(R.string.connect);
//                            }
//
//                            mInputManager.hideSoftInputFromWindow(mEmulatorView.getWindowToken(), 0);
//
//                            mTitle.setText(R.string.title_not_connected);
                            Log.d(TAG, "BluetoothSerialService.STATE_LISTEN | BluetoothSerialService.STATE_NONE");

                            break;
                    }
                    break;
                case MESSAGE_WRITE:
                    Log.d(TAG, "MESSAGE_WRITE");
//                    if (mLocalEcho) {
//                        byte[] writeBuf = (byte[]) msg.obj;
//                        mEmulatorView.write(writeBuf, msg.arg1);
//                    }

                    break;

            case MESSAGE_READ:
                byte[] readBuf = (byte[]) msg.obj;
                Log.d(TAG, "MESSAGE_READ");
                Log.d(TAG, new String(readBuf));
//                mEmulatorView.write(readBuf, msg.arg1);

                break;

                case MESSAGE_DEVICE_NAME:
                    // save the connected device's name
                    mConnectedDeviceName = msg.getData().getString(DEVICE_NAME);
                    Log.d(TAG, "MESSAGE_DEVICE_NAME");
                    Log.d(TAG, "Connected to " + mConnectedDeviceName);

                    Toast.makeText(getApplicationContext(), getString(R.string.toast_connected_to) + " "
                            + mConnectedDeviceName, Toast.LENGTH_SHORT).show();
                    break;
                case MESSAGE_TOAST:
                    Log.d(TAG, "MESSAGE_TOAST: " + msg.getData().getString(TOAST));
                    Toast.makeText(getApplicationContext(), msg.getData().getString(TOAST), Toast.LENGTH_SHORT).show();
                    break;
            }
        }
    };

    public static JSONObject packLocationToJSON(Location location) {
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

            return jsonObject;
        } catch (JSONException e) {
            Log.e(TAG, "JSONException encountered while trying to serialize location");
            e.printStackTrace();
            return new JSONObject();
        }
    }
}

/*

Linux serial server setup:

# Did this, not sure if needed...
#mknod -m 666 /dev/rfcomm0 c 216 0


# Start from clean slate
sudo service bluetooth restart

# Choose channel that is unused, e.g. 11
sudo sdptool browse local | grep Channel

# Sometimes needed? Not sure...
#rfcomm release 0

# Create serial channel
sudo sdptool add --channel=11 SP

# Watch for connections and accept them
sudo rfcomm watch 0 1

# In different terminal
cat /dev/rfcomm0


 */
