# Shazall
Shazam all music being played using a microphone

## Stuff needed:
* Raspberry Pi 3 or greater.
* USB microphone. I used [MI-305](https://www.amazon.eg/-/en/MI-305-Mini-USB-Microphone-Black/dp/B0994PFKDD). I think most of these kinds of microphones work.
* LCD Screen. I used [XPT2046](https://www.amazon.com/Resistive-compatible-Raspberry-Pi-Raspbian/dp/B00OZQS5NY) on RPi3 and [MHS-3.5inch RPi Display](https://www.lcdwiki.com/MHS-3.5inch_RPi_Display) on RPi4. I think most of these kinds of screens work.

## Install

[Install Raspberry Pi OS Lite](https://www.raspberrypi.com/documentation/computers/getting-started.html).

SSH into your Raspberry Pi and run the following command: `sudo raspi-config`

Go to `Interface Options > SPI` and select `Yes`

Go to `System options > Auto login` and select `Yes`

Choose `Finish`

Go to `Reboot > Yes` and select `Yes`

After the reboot, SSH back into your Raspberry Pi and run the following commands to install stuff we need:

```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install raspberrypi-ui-mods git ffmpeg portaudio19-dev python3-pip
```

To install support for the Scrren, enter the following commands:

```
git clone https://github.com/goodtft/LCD-show.git
cd LCD-show
sudo ./LCD35-show
```

This reboots the machine automatically and should show the terminal login. If it's upside down enter this command: `sudo nano /boot/config.txt` and under `[all]`, change `dtoverlay=tft35a:rotate=90` to `dtoverlay=tft35a:rotate=270` and save. Then enter: `sudo reboot`

Next up is the install of Shazall itself. 

Enter the following commands:

```
git clone https://github.com/jonkpirateboy/shazall.git
cd shazall
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install sounddevice soundfile shazamio pydub pylast
sudo nano /etc/systemd/system/shazall.service
```

In this file enter this code:
```
[Unit]
Description=Show shazall on LCD via Python
After=multi-user.target

[Service]
ExecStart=/home/[yourusername]]/shazall/venv/bin/python3 /home/[yourusername]/shazall/shazall.py
WorkingDirectory=/home/[yourusername]/shazall
StandardOutput=journal
StandardError=journal
Restart=on-failure
User=[yourusername]
Group=[yourusername]
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Change `[yourusername]` to your username.

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
* Answer the quiestions and the script will get your session_key saved to shazall-settings.json automatically

Exit the venv: `deactivate`

After reboot, or restart of the service, Shazall will scrobble to Last.fm. 
