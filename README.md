# VirtualBox Curses Remote

An ncurses client written in python3 for interfacing remotely with a linux server running ssh and VirtualBox. This is designed to be used with VRDE remote desktop enabled on each vm client.

This is a quick and dirty solution to managing numerous virtual machines on single host over a network.

Dependencies: python3, curses, xfreerdp, openssh or equivalent

## Completed (from original repo):
* Curses Menu for selecting machines
* MenuItem object with tooltip
* Open xfreerdp for the selected machine
* Turn selected machine on and off
* SSH public key authentication

## Added in fork
* Local mode
* Multiple hosts (just add them to the list on top of the "vcr" script
* Automatic SSH tunnel for RDP
* Changed rdesktop -> xfreerdp
* A bunch of refactoring and bugfixing
