# Copyright (C) 2010 Ubixum, Inc. 
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA



# change location of fx2libdir if needed
FX2LIBDIR=../fx2lib
SOURCES=fw.c device.c
A51_SOURCES=dscr.a51
BASENAME=firmware


DSCR_AREA=-Wl"-b DSCR_AREA=0x3d00"
INT2JT=-Wl"-b INT2JT=0x3f00"
CODE_SIZE=--code-size 0x3c00
XRAM_LOC=--xram-loc 0x3c00
XRAM_SIZE=--xram-size 0x0100

include $(FX2LIBDIR)/lib/fx2.mk

