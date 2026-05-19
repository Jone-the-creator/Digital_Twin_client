Created by Jonah Habel for Honours project at Flinders University

This client is designed to be scalable to any quadcopter with any communication system; controllers and estimators can then be built atop this client as plugins.

**Comms Plugins**
For a communication system that is not included in Comms Plugins, add them as a class in the folder.

This needs to:
 - Log values from telemetry and update the quadcopter object (at minimum, gyro (x,y,z), acc (x, y) and battery voltage must be logged)
 - Send controls through telemtry based on selected controller (e.g. read controls from stabiliser.hover())

Use Crazyradio.py as an example if required.

To integrate a new plugin to the setup GUI, in GUI/setup.py the title must be added to 'comms_options' in run_setup(). Then, in runtime.py in main(),
a statement must be added to instantiate the comms system (follow example of the crazyradio if needed).

**Controller Plugins**
TO BE EXPLAINED

**Estimator Plugins**
TO BE EXPLAINED


**Quadcopter Class**
If variables imported into the quadcopter object are adjusted, these must be changed throughout each other plugin.

**Installing Libraries**
To install all required libraries, enter 
~~
pip install -r libraries.txt 
~~
into a terminal. 

This project requires the following Python packages:
- numpy
- pygame (controller input)
- cflib (Crazyflie communication)
- PyQt6 (GUI framework)
- pyqtgraph + PyOpenGL (3D rendering)
- trimesh (3D model loading)
- PySimpleGUI (startup interface)

**Crazyradio Drivers**
If using crazyflie, ensure USB drivers are installed for both crazyradio dongle and crazyflie. 
https://www.bitcraze.io/documentation/repository/crazyradio-firmware/master/building/usbwindows/
