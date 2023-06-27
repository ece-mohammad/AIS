# Automatic Irrigation System (SIA)

## What Is SIA

SIA is the reversed acronym for Automatic Irrigation System (AIS). SIA is an automated irrigation system, where you hook up your devices and monitor their sensors (soil temperature, moisture, salts concentration, water level, etc) and control their actuators (water valve, water pump, motors, etc) either from the dashboard or by settings actions that trigger on certain conditions.

SIA is not a home automation system!!! There's an awesome open source home automation system [here](https://github.com/home-assistant/core), check it out.

## Features

- SIA is 100% local. The core (backend server and services) run from any PC (or PC-like device like raspberry-pi), and requires no internet connection. Your data is your own
- Wireless connection to the devices, no wires required
- Setup once and forget about it
- The core supports RESTful APIs and MQTT for data exchange with the devices
- Open source, SIA is licensed under MIT license
- Not a home automation system!

## Why

- I like my plants, but sometimes I forget watering them
- I also like python, and I wanted to try Django
- I worked on a home automation system backend once before, but it was hacky at best and I wanted to try and make something a bit less hacky

## To-Do List

- [ ] home page (dashboard)
- [x] Accounts
  - [x] user login
  - [x] user logout
  - [x] sign up
  - [x] password reset
  - [x] password change
  - [x] edit account
  - [x] deactivate account
  - [x] delete account

- [ ] Device Groups
  - [x] device group add/create
    - [x] only available for logged in users
  - [ ] device group details
    - [ ] only for group's owner
    - [ ] only available for logged in users
    - [ ] list devices in the group
  -[ ] device group list
    - [ ] only available for logged in users
    - [ ] only for group's owner
  - [ ] device group edit
    - [ ] only available for logged in users
    - [ ] only for group's owner
    - [ ] change device's group from device's edit
  - [ ] device group delete
    - [ ] only available for logged in users
    - [ ] only for group's owner

- [ ] Devices
  - [ ] device add/create
    - [ ] only for logged in users
    - [ ] only when at least 1 device group is created
    - [ ] create new device group from
  - [ ] device details
    - [ ] only for logged in users
    - [ ] only for device's owner
    - [ ] show last 10 data messages
  - [ ] list devices
    - [ ] only for logged in users
    - [ ] only for device's owner
    - [ ] group by device group
  - [ ] edit device
    - [ ] only for logged in users
    - [ ] only for device's owner
    - [ ] can change device's group

- [ ] DeviceData
  - [ ] list device data history
    - [ ] only for logged in users
    - [ ] only for device's owner

- [ ] control part
- [ ] RESTful
- [ ] MQTT
- [ ] Actions
- [ ] Backup
