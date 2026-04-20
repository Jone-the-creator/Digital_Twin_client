# written based on instruction from 
# https://www.bitcraze.io/documentation/repository/crazyflie-clients-python/master/userguides/userguide_client/#firmware-configuration

import logging
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper

from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger

# Crazyradio logger plugin
class CRTP_logger:

    def __init__(self, quadcopter):
        # URI for the Crazyflie to connect to
        self.uri = uri_helper.uri_from_env(default= 'radio://0/80/2M/E7E7E7E7E7')
        self.quadcopter = quadcopter
        #check URI of crazyflie with a USB cable 
        # https://www.bitcraze.io/documentation/repository/crazyflie-clients-python/master/userguides/userguide_client/#firmware-configuration

    def start(self):    
        # Initialize the low-level drivers
        cflib.crtp.init_drivers()

        # add log variables that are desired, if unsure check by connecting to client and look at log TOC tab
        # https://www.bitcraze.io/documentation/repository/crazyflie-lib-python/master/user-guides/sbs_connect_log_param/ 

        with SyncCrazyflie(self.uri, cf=Crazyflie(rw_cache='./cache')) as scf:
            logconf = LogConfig(name='Stabilizer', period_in_ms=10)
            logconf.add_variable('stabilizer.roll', 'float')
            logconf.add_variable('stabilizer.pitch', 'float')
            logconf.add_variable('stabilizer.yaw', 'float')

        scf.cf.log.add_config(logconf)
        logconf.data_received_cb.add_callback(self._on_log)
        logconf.start()

        time.sleep(5)

        # Only output errors from the logging framework
        logging.basicConfig(level=logging.ERROR)

        
    def _on_log(self, timestamp, data, logconf):
        self.quadcopter.update_attitude(
            roll=data['stabilizer.roll'],
            pitch=data['stabilizer.pitch'],
            yaw=data['stabilizer.yaw'],
            timestamp=timestamp / 1000.0
        )
        print("Quadcopter update success!")
