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

# URI for the Crazyflie to connect to
uri = uri_helper.uri_from_env(default= 'radio://0/80/2M/E7E7E7E7E7')
#check URI of crazyflie with a USB cable 
# https://www.bitcraze.io/documentation/repository/crazyflie-clients-python/master/userguides/userguide_client/#firmware-configuration

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

def simple_log(scf, logconf):
    with SyncLogger(scf, logconf) as logger:

        for log_entry in logger:

            timestamp = log_entry[0]
            data = log_entry[1]
            logconf_name = log_entry[2]

            print('[%d][%s]: %s' % (timestamp, logconf_name, data))

            break

def simple_connect():

    print("Yeah, I'm connected! :D")
    time.sleep(3)
    print("Now I will disconnect :'(")

if __name__ == '__main__':
    # Initialize the low-level drivers
    cflib.crtp.init_drivers()

    # add log variables that are desired, if unsure check by connecting to client and look at log TOC tab
    # https://www.bitcraze.io/documentation/repository/crazyflie-lib-python/master/user-guides/sbs_connect_log_param/ 
    lg_stab = LogConfig(name='Stabilizer', period_in_ms=10)
    lg_stab.add_variable('stabilizer.roll', 'float')
    lg_stab.add_variable('stabilizer.pitch', 'float')
    lg_stab.add_variable('stabilizer.yaw', 'float')

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:

        simple_connect()