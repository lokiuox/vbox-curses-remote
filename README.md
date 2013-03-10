# VirtualBox Curses Remote

An ncurses client written in python3 for interfacing remotely with a linux server running ssh and VirtualBox. This is designed to be used with VRDE remote desktop enabled on each vm client.

This is a quick and dirty solution to managing numerous virtual machines on single host over a network.

Dependencies: python3, curses, rdesktop, openssh or equivalent

## Completed:
* Curses Menu for selecting machines
* MenuItem object with tooltip
* Open rdesktop for the selected machine
* Turn selected machine on and off
* SSH public key authentication

## Todo:
### General:
* Installers
* Config files
* Python Documentation
* Fix thread blocking on subprocess

### Curses:
* Menu class options ( scrolling, etc. )
* Scrolling textboxes

### Virtualbox
* Snapshots
* Managing VM Properties
* VM Info
* VM password authentication
