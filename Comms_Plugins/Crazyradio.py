# written based on instruction from 
# https://www.bitcraze.io/documentation/repository/crazyflie-clients-python/master/userguides/userguide_client/#firmware-configuration

import logging, time, threading

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger

# Crazyradio logger plugin
class CRTP_logger:

    def __init__(self, quadcopter, uri = None):
        # URI for the Crazyflie to connect to
        # check URI of crazyflie with a USB cable 
        self.uri = uri or "radio://0/80/2M/E7E7E7E7E7"
        self.quadcopter = quadcopter
        self.cf = None
        self.logconf = None
        self.is_connected = False

    def start(self):    
        # Initialize the low-level drivers
        cflib.crtp.init_drivers()

        # instantiate crazyflie object
        self.cf = Crazyflie(rw_cache="./cache")

        # add main callbacks (occurs under certain conditions, like an interrupt)
        self.cf.connected.add_callback(self._connected)
        self.cf.connection_failed.add_callback(self._connection_failed)
        self.cf.disconnected.add_callback(self._disconnected)

        self._setup_logging()

        print(f"Opening link to {self.uri}")
        self.cf.open_link(self.uri)

        # send controls in a separate thread
        threading.Thread(target=self._control_loop, daemon=True).start()

    def stop(self):
        # stops connection if was previously connected to a crazyflie object
        if self.cf is not None and self.is_connected:
            print("Closing Crazyflie link")
            self.cf.close_link()
    
    def _setup_logging(self):
        # add log variables that are desired, if unsure check by connecting to client and look at log TOC tab
        self.logconf = LogConfig(
            name='Stabilizer', 
            period_in_ms=10
        )
        # choose logged variables here, can find in the following list:
        # https://www.bitcraze.io/documentation/repository/crazyflie-firmware/master/api/logs/
        self.logconf.add_variable('stabilizer.roll', 'float')
        self.logconf.add_variable('stabilizer.pitch', 'float')
        self.logconf.add_variable('stabilizer.yaw', 'float')
        self.logconf.add_variable('pm.vbat', 'float')

        
        self.logconf.data_received_cb.add_callback(self._log_data_received)

    # callback functions (to be run in certain conditions)
    def _connected(self, uri):
        print(f"Connected to Crazyflie at {uri}")
        self.is_connected = True

        try:
            self.cf.log.add_config(self.logconf)
            self.logconf.start()
            print("Logging started")
        except Exception as e:
            print(f"Failed to start logging: {e}")


    def _connection_failed(self, uri, msg):
        print(f"Connection failed to {uri}: {msg}")
        self.is_connected = False

 
    def _disconnected(self, uri):
        print(f"Disconnected from {uri}")
        self.is_connected = False

    def _convbattery(self, voltage):
        v_min = 3.0
        v_max = 4.2

        percent = ((voltage - v_min) / (v_max - v_min)) * 100
        percent = max(0.0, min(100, percent))

        return percent



    def _log_data_received(self, timestamp, data, logconf):
        # updates values in quadcopter object based on readings from crazyflie
        self.quadcopter.update_attitude(
            roll=data['stabilizer.roll'],
            pitch=data['stabilizer.pitch'],
            yaw=data['stabilizer.yaw'],
            timestamp=timestamp / 1000.0
        )
        self.quadcopter.battery_voltage = round(data['pm.vbat'],2) 
        if (self.quadcopter.controls.thrust < 500):
            self.quadcopter.battery_percent = int(self._convbattery(data['pm.vbat']))



    def _control_loop(self):
        while True:
            if self.is_connected:
                self.send_controls()
            time.sleep(0.02) # ~50Hz

    # controls that will be sent to the crazyflie 
    def send_controls(self):
        if not self.is_connected:
            return
        self.cf.commander.send_setpoint(
            float(self.quadcopter.controls.roll),
            float(self.quadcopter.controls.pitch),
            float(self.quadcopter.controls.yaw_rate),
            int(self.quadcopter.controls.thrust)
        )
