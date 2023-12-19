# Portal Turret OS
The main application that runs on the hand build Turret.
You can get a better idea on what this project is about by watching the following videos, or just keep reading :)

# 3D files
The turret is completely 3D printed in PLA, with some PETG parts.
This is not a tutorial, but if you want to give it a go and print my file to recreate this turret, make sure you print the files in the provided orientation.
Some parts can be printed a lot better and without supports by just rotating them, but don't do that. The parts are small enough that layer direction affects some tolerances.
(I mean you can try to print them in a different orientation if your printer is dialed in and you are sure they will be printed accuratly!)
You can print everything in PLA, idealy in the colors of choice (black and white).
On the main body, the black strip is painted by hand. If you have a multimaterial printer, you can try to print the black stripe.

# Hardware
The complete list of components is as follows:
-Raspberry pi zero W
-16gb microsd card
-NoIR Pi zero camera
-Speaker with amp
-4x servos
-8x red smd leds (for the eye ring)
-4x High power 5mm LED (for the guns)
-3x mosfets
-3x 1k resistors
-2x 500ohm resistors
-1x cap xxxuf
-1x cap yyyuf
-2x 1k resistors
-Male/female header pins
-10x threaded insters + screws- 

# Schematic
XXXXXXXXXXXXXX

# Software
The raspberry pi runs Rasbian Buster, the minimal installation (no GUI)
Extra packages that are required:
pip3 (installation guide here, needed for installing pygame)
pigpio (installation guide here, make sure to automatically start it at boot using cron (how to))
pygame (installation guide here, needed for loading and playing sound effects)
motion (installation guide here, configuration in the "motion config" folder, needed for video monitoring, motion detection)

Extra contiguration needed:
Enable SSH
Enable Legacy Pi Camera in raspi-config
Enable the analog audio output on pin xx (add xxxxxx to /boot/config.txt)

TBD
