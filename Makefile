# Topfield-Launcher
#
# Copyright (C) 2010 Mark Blakeney, markb@berlios.de. This program is
# distributed under the terms of the GNU General Public License.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or any
# later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License at <http://www.gnu.org/licenses/> for more
# details.

# This simple Makefile merely installs the app in your ~/bin. You can
# install the app anywhere in your path of course.

PROG = Topfield-Launcher.py

all:

install:
	install -D $(PROG) $(HOME)/bin/
