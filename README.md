# FalconBMSToSerial
QT6 app for reading Falcon BMS sharedmem and sending the data over serial written in python

## Setup
After cloning this repository you should run the following to add the submodules required.
```
git submodule init
git submodule update
```

### Requirements
This app uses two packages: `PyQt6` and `pyserial`. You can install them using the following command.
```
pip install pyserial PyQt6
```

## Making an executable
To make an executable you should install the `pyinstaller` pip package. After which you can run the following to create an executable.
```
pyinstaller main.spec
```
