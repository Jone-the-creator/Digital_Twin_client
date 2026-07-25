# Written by Jonah Habel 2026
# Flinders University
#
# written based on instruction from 
# https://www.bitcraze.io/documentation/repository/crazyflie-clients-python/master/userguides/userguide_client/#firmware-configuration

import time, threading

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig

# Crazyradio logger plugin
class CRTP_logger:

    def __init__(self, quadcopter, uri = None):
        # URI for the Crazyflie to connect to
        # check URI of crazyflie with a USB cable 
        self.uri = uri or "radio://0/80/2M/E7E7E7E7E7"
        self.quadcopter = quadcopter
        self.cf = None
        self.logconf_acc = None
        self.logconf_gyro = None
        self.logconf_periph = None
        self.logconf_pos = None
        self.is_connected = False
        self.last_update_time = time.time()

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
        self.logconf_gyro = LogConfig(
            name='Gyroscope', 
            period_in_ms=15
        )
        self.logconf_acc = LogConfig(
            name='Accelerometer', 
            period_in_ms=15
        )
        self.logconf_periph = LogConfig(
            name='Peripherals', 
            period_in_ms=250
        )
        self.logconf_pos = LogConfig(
            name='Position',
            period_in_ms=25
        )
        # choose logged variables here, can find in the following list:
        # https://www.bitcraze.io/documentation/repository/crazyflie-firmware/master/api/logs/
        self.logconf_gyro.add_variable('gyro.x', 'float')
        self.logconf_gyro.add_variable('gyro.y', 'float')
        self.logconf_gyro.add_variable('gyro.z', 'float')

        self.logconf_acc.add_variable('acc.x', 'float')
        self.logconf_acc.add_variable('acc.y', 'float')
        self.logconf_acc.add_variable('acc.z', 'float')

        self.logconf_periph.add_variable('pm.vbat', 'float')

        self.logconf_pos.add_variable('kalman.stateX', 'float')
        self.logconf_pos.add_variable('kalman.stateY', 'float')
        self.logconf_pos.add_variable('kalman.stateZ', 'float')

        self.logconf_gyro.data_received_cb.add_callback(self._log_gyro_data_received)
        self.logconf_acc.data_received_cb.add_callback(self._log_acc_data_received)
        self.logconf_periph.data_received_cb.add_callback(self._log_periph_data_received)
        self.logconf_pos.data_received_cb.add_callback(self._log_pos_data_received)

    # callback functions (to be run in certain conditions)
    def _connected(self, uri):
        print(f"Connected to Crazyflie at {uri}")
        self.is_connected = True

        try:
            self.cf.log.add_config(self.logconf_gyro)
            self.logconf_gyro.start()
            self.cf.log.add_config(self.logconf_acc)
            self.logconf_acc.start()
            self.cf.log.add_config(self.logconf_periph)
            self.logconf_periph.start()
            self.cf.log.add_config(self.logconf_pos)
            self.logconf_pos.start()
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

    def _log_gyro_data_received(self, timestamp, data, logconfig):
        # updates values in quadcopter object based on readings from crazyflie
        self.quadcopter.update_gyro(
            roll_vel=data['gyro.x'],
            pitch_vel=data['gyro.y'],
            yaw_vel=data['gyro.z'],
        )

    def _log_acc_data_received(self, timestamp, data, logconfig):
        # updates values in quadcopter object based on readings from crazyflie
        self.quadcopter.update_acc(
            a_x = data['acc.x'],
            a_y = data['acc.y'],
            a_z = data['acc.z']
        )

    def _log_pos_data_received(self, timestamp, data, logconfig):
        # updates values in quadcopter object based on readings from crazyflie
        self.quadcopter.update_position(
            x = data['kalman.stateX'],
            y = data['kalman.stateY'],
            alt = data['kalman.stateZ'],
        )
        # print(f"z = {data['kalman.stateZ']}")

    def _log_periph_data_received(self, timestamp, data, logconfig):
        # if no thrust, battery percentage can be safely calculated
        if (self.quadcopter.controls.thrust < 500):
            self.quadcopter.battery_percent = int(self._convbattery(data['pm.vbat']))

        # always log battery voltage
        self.quadcopter.battery_voltage = round(data['pm.vbat'],2)



    def _control_loop(self):
        # set attitude flight mode to rate
        self.cf.param.set_value('flightmode.stabModeRoll', 0)
        self.cf.param.set_value('flightmode.stabModePitch', 0)
        self.cf.param.set_value('flightmode.stabModeYaw', 0) # sets yaw mode to carefree (Carefree(0), plusmode(1), xmode(2))
        self.cf.param.set_value('stabilizer.controller', 0) # disables built-in on-board stabiliser
        while True:
            #send controls and use microsleeps to achieve the desired loop rate
            start_time = time.time()
            if self.is_connected:
                self.send_controls()
            loop_time = time.time() - start_time
            while(loop_time < 0.0025): # 500Hz
                time.sleep(0.00001)
                loop_time = time.time() - start_time
            # print(f"actual loop time = {time.time()-start_time}")

    # controls that will be sent to the crazyflie 
    def send_controls(self):
        if not self.is_connected:
            return
        
        #kill switch
        if getattr(self.quadcopter, "killed", False):
            self.cf.commander.send_stop_setpoint()

        else: 
            # calculate change in time
            now = time.time()
            dt = now - self.last_update_time
            self.last_update_time = now
            self.cf.commander.send_setpoint(
                roll = float(self.quadcopter.controls.roll),
                pitch = float(self.quadcopter.controls.pitch),
                yawrate = float(self.quadcopter.controls.yaw_rate),
                thrust = int(self.quadcopter.controls.thrust)
            )
            # print(f"transmitted pitch rate {float(self.quadcopter.controls.pitch)}")
            # print(f"transmitted thrust = {int(self.quadcopter.controls.thrust)}")
