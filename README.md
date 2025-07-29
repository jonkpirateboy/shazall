# shazall
Shazam all music being played using a microphone

Stuff needed:
* Raspberry Pi 3 or greater.
* USB microphone. I used [MI-305](https://www.amazon.eg/-/en/MI-305-Mini-USB-Microphone-Black/dp/B0994PFKDD). I think most of these kinds of screens work.
* LCD Screen. I used [XPT2046](https://www.amazon.com/Resistive-compatible-Raspberry-Pi-Raspbian/dp/B00OZQS5NY) on RPi3 and [MHS-3.5inch RPi Display](https://www.lcdwiki.com/MHS-3.5inch_RPi_Display) on RPi4. I think most of these kinds of screens work.

Install:

I will make this more readable soon :)

sudo raspi-config
Interface Options > SPI > Yes
System options > Auto login > Yes
Finish
Reboot > Yes

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install raspberrypi-ui-mods git ffmpeg portaudio19-dev python3-pip

git clone https://github.com/goodtft/LCD-show.git
cd LCD-show
sudo ./LCD35-show
Reboots automatically and should show the terminal login. If it's upside down:
sudo nano /boot/config.txt
Under [all], change "dtoverlay=tft35a:rotate=90" to:
dtoverlay=tft35a:rotate=270
sudo reboot

git clone https://github.com/jonkpirateboy/shazall.git

cd shazall

python3 -m venv venv

source venv/bin/activate

pip install --upgrade pip

pip install sounddevice soundfile shazamio pydub pylast

sudo nano /etc/systemd/system/shazall.service

[Unit]
Description=Show shazall on LCD via Python
After=multi-user.target

[Service]
ExecStart=/home/jonk/shazall/venv/bin/python3 /home/jonk/shazall/shazall.py
WorkingDirectory=/home/jonk/shazall
StandardOutput=journal
StandardError=journal
Restart=on-failure
User=jonk
Group=jonk
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target

sudo systemctl daemon-reload
sudo systemctl enable shazall.service
sudo systemctl start shazall.service

sudo reboot