# Shazall
Shazam all music being played using a microphone

So now you can see what song is playing on the radio, in the TV show or movie you're watching, on your turntable, what the DJ is playing, what's playing in the record shop, or whatever.

And with the bonus feature of scrobbling everything, you don't have to fear that people don't know what exquisite in music you have when you're not streaming, it can be scrobbled anyway! ;)

## Stuff needed:
* Raspberry Pi 3 or greater.
* USB microphone. I used [MI-305](https://www.amazon.eg/-/en/MI-305-Mini-USB-Microphone-Black/dp/B0994PFKDD). I think most of these kinds of microphones work.
* LCD Screen. I used [XPT2046](https://www.amazon.com/Resistive-compatible-Raspberry-Pi-Raspbian/dp/B00OZQS5NY) on RPi3 and [MHS-3.5inch RPi Display](https://www.lcdwiki.com/MHS-3.5inch_RPi_Display) on RPi4. I think most of these kinds of screens work.

## Install

### OS

[Install Raspberry Pi OS Lite](https://www.raspberrypi.com/documentation/computers/getting-started.html).

When starting up your Raspberry Pi, the screen will not display anything, that will be fixed

SSH into your Raspberry Pi and run the following command: `sudo raspi-config`

Go to `Interface Options > SPI` and select `Yes`

Go to `System options > Auto login` and select `Yes`

Choose `Finish`

```
sudo apt-get update
sudo apt-get upgrade
```

### Packages

Now, run the following command to install stuff we need:

```
sudo apt-get install raspberrypi-ui-mods git ffmpeg portaudio19-dev python3-pip
```

### LCD screen
To install support for the LCD screen, enter the following commands:

```
git clone https://github.com/goodtft/LCD-show.git
cd LCD-show
sudo ./LCD35-show
```

This reboots the machine automatically and should show the terminal login on the LCD screen. 

If it's upside down enter this command: `sudo nano /boot/config.txt` and under `[all]`, change `dtoverlay=tft35a:rotate=90` to `dtoverlay=tft35a:rotate=270` and save. Then enter: `sudo reboot`

And this is a bit of a strange one. During the installation of LCD-show, raspi-config is uninstalled for some reason. So now it's time to reinstall it: `sudo apt-get install raspi-config`

### Shazall

Next up is the install of Shazall itself. 

Enter the following commands:

```
git clone https://github.com/jonkpirateboy/shazall.git
cd shazall
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install sounddevice soundfile shazamio pydub pylast pillow
deactivate
sudo cp shazall.service /etc/systemd/system/
sudo nano /etc/systemd/system/shazall.service
```

In this file change `[yourusername]` to your username.

If you need to change the duration of how long Shazam should listen, the samplerate, or the screen resultion, you can do that in the `shazall-settings.json` file.

Then add this code to make Shazall autostart on boot:

```
sudo systemctl daemon-reload
sudo systemctl enable shazall.service
sudo systemctl start shazall.service
````

And then reboot the machine and you sould see Shazall listening: `sudo reboot`

### Bonus: Scrobble to Last.fm

* [Create an API account with Last.fm](https://www.last.fm/api/account/create)
* For `Application name`, choose whatever you like, for example `Shazall`. You don't need to fill out the rest.
* SSH into your Raspberry Pi 
* Edit the file `shazall-settings.json`, change `scrobble` to `true`, and enter your Last.fm credentials:

```
api_key = API key
api_secret = Shared secret
session_key = Leave empty
username = Registered to
````

Save and exit and, then we continue:

* Enter the venv: `source sazall/venv/bin/activate`
* Enter this command: `python3 shazall-lastfm-get-session.py`
* Enter your username and password when promted, and the script will get your session_key and seve it to shazall-settings.json automatically.

Exit the venv: `deactivate`

After reboot, or restart of the service, Shazall will scrobble to Last.fm. 
