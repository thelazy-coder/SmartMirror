#!/bin/bash
mkdir datasets
mkdir tempaudio
mkdir data
sudo apt autoremove -y
sudo apt update -y
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get dist-upgrade -y
sudo apt-get install flac -y
sudo apt-get install python3 -y
sudo apt-get install python3-opencv -y
sudo apt-get install python3-pyaudio -y
sudo apt-get install python3-matplotlib -y
sudo apt-get install python3-dev python3-pip -y
sudo apt install libjasper1 -y
sudo apt-get install libatlas-base-dev -y
sudo apt-get install libqtwebkit4 libqt4-test -y
sudo apt-get install libhdf5-dev libhdf5-serial-dev -y
sudo apt-get install libatlas-base-dev -y

sudo pip3 install -r requirements.txt
