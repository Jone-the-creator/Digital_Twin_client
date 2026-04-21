Created by Jonah Habel for Honours project at Flinders University

This client is designed to be scalable to any quadcopter with any communication system.

**Comms plugins**
For a communication system that is not included in Comms Plugins, add them as a class in the folder.
They need to be added to the logging section of runtime.py (following example of Crazyradio), 
and add the title to comms_options to be able to select it in init GUI.

**Quadcopter Class**
If variables imported into the quadcopter object are adjusted, these must be changed throughout each other plugin.

