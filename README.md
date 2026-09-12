_Created by Jonah Habel (2026) for Honours project at Flinders University._

# Quadcopter Digital Twin Framework
This Digital Twin client is designed to be a scalable platform to any quadcopter plant model (theoretically any plant), where plant models, communication systems, controllers and state estimators can be built atop the client as plugins.

Pre-loaded plugins created for Honours project:
- Crazyradio communication system
- 9 State quadcopter plant model
- 6DOF quadcopter EKF (using gyro, accelerometer and Loco positioning system)
- Model-free PID control system
- State space pole-placement control system

## Adding Custom Plugins
As plugins are added, they must be properly integrated to be able to be selected in the setup window. This must updated in the run_setup() function in GUI/windows/setup_window.py, where adding another string in the list will allow it to become selectable.  
<img width="416" height="82" alt="image" src="https://github.com/user-attachments/assets/43137608-cbbd-4d0b-b769-993cd47947e9" />

_Note that plant models are not currently selectable in the setup window, this is integrated into the state-feedback of the pole-placement controller and is set as future work to make this easily configurable._

Once selectable, follow the method below for the relevant plugin type to instantiate it. This will include adjusting the quadcopter class in quadcopter.py, or the main() function in runtime.py. 
### Communication System Plugins
1. Create a python script in /Comms_Plugins (_It is recommended to import the quadcopter object to this script, Crazyradio.py is worth using as an example_).
2. In runtime.py, navigate to the --COMMS-- section of the main() function and an an ELIF statement. This statement should check the quad.comms variable for the string that was entered into the list previously, and if found it should instantiate your comms plugin. See the Crazyradio statement as an example. 
<img width="312" height="123" alt="image" src="https://github.com/user-attachments/assets/e578df15-f067-4fc2-88f9-c4807e644c96" />

### Control System Plugins
1. Create a python script in /Controllers (_For state-space controllers it is recommended to leave an argument for a state observer, and for model-free controllers it is recommended to leave an argument for the quadcopter object. PID_stabiliser.py and PP_stabiliser.py are examples of both_).
2. In runtime.py, navigate to the main() function and instantiate the controller with the rest of the objects.<img width="436" height="216" alt="image" src="https://github.com/user-attachments/assets/0547cf87-5122-4e80-9985-e745a528b5a3" />
3. In runtime.py, add the object to the control_loop() function by adding it as an argument and inputting that in the thread instantiation.<img width="332" height="45" alt="image" src="https://github.com/user-attachments/assets/f4a29398-1c23-49eb-9d64-439aca8865db" /><img width="580" height="45" alt="image" src="https://github.com/user-attachments/assets/88ddd17e-1801-41b7-8d94-5f5c7c3aab16" />
4. In the control_loop() function, add a statement to check if the control_system variable is the string that denotes your control system plugin. Here, you can add the inputs to your system based on the controls seen in the manual control mode.<img width="715" height="236" alt="image" src="https://github.com/user-attachments/assets/b6771c0f-6ec2-476c-b24a-e888ee0369e3" />

_Note, the thrust_raw value is smoothed and once smoothed will be input to u[3,0]. This u array will be input to whatever the active plant is using the update_active() function._

### State Estimator Plugins
1. Create a python script in /Classes.
2. Create your state estimator (_See the ExtendedKalmanFilter.py script as an example_).
3. In the quadcopter class, add a statement to check if the estimator variable is the string that denotes your state estimator plugin.  <img width="362" height="63" alt="image" src="https://github.com/user-attachments/assets/1d8c50bf-bae2-4825-9693-f308752c673b" />
4. The current iteration of the quadcopter class has three placements for the EKF, in the update_position(), update_gyro() and update_acc() functions. If these are to be used, add the new estimator as an elif statement in these functions; if a new function is to be used, ensure that the estimator is only used if it is not none. This will allow for integration with other estimators in the future.
<img width="399" height="220" alt="image" src="https://github.com/user-attachments/assets/13fcd869-e4ed-4929-a065-913eeba910b5" />


## Installing Required Libraries
To install all required libraries, enter 

>pip install -r libraries.txt 

into a terminal. 

This will install the following Python packages seen in libraries.txt:
- numpy
- pygame (controller input)
- cflib (Crazyflie communication)
- PyQt6 (GUI framework)
- pyqtgraph + PyOpenGL (3D rendering)
- trimesh (3D model loading)
- PySimpleGUI (startup interface)

## Crazyflie Drivers
If using crazyflie, ensure USB drivers are installed for both crazyradio dongle and crazyflie. 
https://www.bitcraze.io/documentation/repository/crazyradio-firmware/master/building/usbwindows/
