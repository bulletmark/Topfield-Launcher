## Topfield-Launcher

Topfield-Launcher connects to a specified ftpd-topfield host and lists recorded
files available on the connected Topfield TF5000 series PVR. The user can
navigate about the PVR directories and select a file to play to his PC. The
Topfield-Launcher will start the specified media player (VLC is recommended) to
stream the requested file from the remote PVR, to the user's screen.

Topfield-Launcher also provides the user with the ability to delete or
rename recorded files.

See screenshots at
<http://wiki.github.com/bulletmark/Topfield-Launcher/>.

### License

Copyright (C) 2010 Mark Blakeney. This program is distributed under the
terms of the GNU General Public License.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or any later
version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License at <https://en.wikipedia.org/wiki/GNU_General_Public_License> for more details.

### Prerequisites

You need a Topfield PVR with a USB connection to a computer or
[NSLU2](http://en.wikipedia.org/wiki/NSLU2)
or similar device running
[ftpd-topfield](http://www.nslu2-linux.org/wiki/Puppy/FtpdTopfield).
That instance of
[ftpd-topfield](http://www.nslu2-linux.org/wiki/Puppy/FtpdTopfield)
may be running on your own user-end PC, or on another remote PC/server
such as a NSLU2 to which you have a network connection from your user
PC. You install Topfield-Launcher and any necessary software as
described below, on your user PC.

You will find that VLC will not stream recorded files at real-time speed
unless you have installed the USB accelerator TAP or firmware patch on
your Topfield. Get the USB accelerator TAP or patch from
<http://www.tapworld.net/>. Note that you don't need to use
ftpd-topfield turbo mode. Performance is excellent. I find that scrolling
through a program is much faster using VLC than on the toppy itself.

I developed and tested Topfield-Launcher on Linux Ubuntu with
ftpd-topfield versions 0.7.6 and 0.7.7 running on my NSLU2 running
Debian. See <http://www.cyrius.com/debian/nslu2/> for instructions on
installing Debian. My wife uses Topfield-Launcher on Windows XP where it
looks and runs as well as on linux.

### Installation on Linux

1. Ensure you have at least python version 2.4 or later (not python 3).

2. Install wxpython 2.8+ and dependent packages. Also install the
   python-dateutil 3rd party package and VLC. (e.g. on ubuntu):

        sudo apt-get update
        sudo apt-get install python-wxgtk2.8 python-dateutil vlc

3. Click/run Topfield-Launcher.py and ensure player path and Topfield
   host are appropriate for your setup. If you run ftpd-topfield on your
   local PC then the Topfield-Launcher host must be set to "localhost".

### Installation on Windows

1. Download and install python 2.6.x or later (not python 3) Windows
   installer from <http://python.org/download/>.
   Do a default install. I have not tested with 3rd party python
   distributions, e.g. ActivePython, but it should work.

2. Download and install wxpython 2.8+ runtime for python 2.6
   (win32/64-unicode) from <http://www.wxpython.org/download.php#binaries>.
   Do a default install.

3. Download the python dateutil library from <http://labix.org/python-dateutil>.

   Unpack the archived file. Winrar is a good small windows archiver
   which will unpack .bz2 files. Get it from
   <http://www.rarsoft.com/download.htm>. A recent
   version of Winzip will also unpack bz2 files.
   Copy the dateutil\dateutil folder to C:\Python2X\Lib\site-packages\.
   Make sure you copy the "\dateutil" sub-folder only! You can then
   delete the dateutil stuff you downloaded.

4. Download and install VLC from <http://www.videolan.org/vlc/>.
   Do default install.

5. The Topfield-Launcher.py file requires a ".pyw" extension on Windows
   to avoid a secondary console window appearing. So rename it manually.

6. Click/run Topfield-Launcher.py and ensure player path and Topfield
   host are appropriate for your setup.

### Installation on Mac

I haven't tried installing this on a Mac yet but it will probably run fine
there and the procedure will be similar to the Linux instructions above.
Mac OS includes python by default so you just need WX python 2.8+,
dateutil, and vlc.

### Other Notes

The specified host name can be an alphanumeric name or a numeric IP
address. If for some reason you are running ftpd-topfield on a
non-standard port then you can specify the host as host:port.

You can add startup options to the specified player if you like. E.g.
Add '-f' if you prefer VLC start in full screen.

The player and host settings are stored permanently (in the usual
platform dependent locations) and so are remembered between invocations.

You can start a file playing, or enter a directory, either by selecting
it and then clicking the select button; or simply by double clicking on
the entry.

You can delete a file by selecting it and clicking the delete button.
Deletes are only actioned after a confirm dialog is presented. Directory
deletion is not allowed. You can also rename files.

The refresh button forces the display to update from the Topfield PVR
disk.

Steve Bennett, the author of ftpd-topfield, has created a patch for vlc
which fixes the skip forwards/backwards hotkeys for streamed media. It
also corrects the total time length displayed. This patch is superb and
provides easy ad-skipping functionality. For some odd reason the patch
has not yet been integrated into the vlc source tree. If you can build
vlc from source then get the patch from
<http://trac.videolan.org/vlc/ticket/2985>.

That should be it. Email me if you have any questions.

### Author

Mark Blakeney, markb@berlios.de. I was user "markb" on the Topfield
Australia forums before they disappeared.
