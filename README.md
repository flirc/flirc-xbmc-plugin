flirc-xbmc-plugin
=================

Official Flirc XBMC Plugin

Installation
------------

## Manually

Copy src/script.flirc to the plugin loctation of your repository.

		Mac			/Users/<your_user_name>/Library/Application Support/XBMC/addons
		Linux		~/.xbmc/addons
		OpenELEC	 /storage/.xbmc/addons
		Windows XP	 %appdata%\XBMC\addons\
		Windows 7	 %appdata%\XBMC\addons\
		Windows 8	 %appdata%\XBMC\addons\

If using linux, see "Linux Requirements"

## Through XBMC

You can add the xbmc repository to your XBMC:

		http://xbmc.flirc.tv

If using linux, see "Linux Requirements"

## Linux Requirements
Linux users need a udev rule in order for the XBMC plugin to be able to open
flirc.

Copy the file in the linux directory, 51-flirc.rules into /udev/rules.d/

You must be the root user in order to do this.

