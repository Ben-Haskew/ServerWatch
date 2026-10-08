### What is this?
The idea behind this project is to be able to easily monitor basic functions of a home server system
### Why?
I got tired of ssh'ing into my server all the time just to check basic details of whether it was running alright or not. With ServerWatch, I can just have a little device that sits on my desk always on telling me these things at a glance.
### How does it work?
This works by connecting over local wifi. You could have it set up in a way where you can access it outside the network, but that is beyond the scope of this project. The host (server) can only communicate with the client when on the same local network. The host parses data from the *lm-sensors* / *sensors* module, and sends it over the internet to the client where it processes that information and simply displays it in an easy to understand format. Alongside the displaying of information, when certain metrics reach certain thresholds, the LED may go red or start blinking. A beeping noise will play if temperatures or usage rates (cpu, memory) go above a predefined limit. If you wish, you can edit these limits in *display.py*, under the *updateLight* function.
### You keep mentioning the client. What is it?
In this case, the client is a Raspberry Pi Zero 2 W (acting as the main processor), along with a Whisplay LED screen (HAT) on the top to display the data. 
## Prerequisites
On linux, the *lm-sensors* module is required.\
Install with\
'sudo apt-get install lm-sensors'\
A Raspberry Pi Zero 2 W\
A PiSugar Whisplay HAT\
Micro-USB power cable (duh)\
Whisplay screen drivers, which can be found here:\
https://github.com/PiSugar/whisplay \

## System Requirements
Linux (Kernal 5.6+)\
Python 3.13 and above\
[This is for the host script]\
[Kernal requirement is for the drivetemp module]

Windows and MacOS are NOT supported
## Installation
To install, simply download all the files.\
You will have to download twice, once for the server that will monitored and once for the client.\
in future I will create releases with *Host* and *Client* files in their own folders.\
On the host, run *serverwatchHost.py*
On the client, run *serverwatchClient.py*\

THIS WILL NOT WORK WITHOUT A WHISPLAY SCREEN.\

You may need to tinker around with connection settings to make sure it connects properly, as this is NOT a one size fits all program (although it intends to be... somewhat)


