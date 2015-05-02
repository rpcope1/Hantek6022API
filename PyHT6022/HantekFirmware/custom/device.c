/**
 * Copyright (C) 2009 Ubixum, Inc. 
 * Copyright (C) 2015 Jochen Hoenicke
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 **/

#include <fx2macros.h>

#ifdef DEBUG_FIRMWARE
#include <stdio.h>
#else
#define printf(...)
#endif




BOOL set_voltage(BYTE channel, BYTE val)
{
    const BYTE val2bits[] = { 1, 0x24*4, 0x24*2, 1, 1, 0x24*0, 
			      1, 1, 1, 1, 0x24*6 };
    BYTE bits = val < 11 ? val2bits[val] : -1;
    if (bits != 1) {
	int mask = channel ? 0xe0 : 0x1c;
	IOC = (IOC & ~mask) | (bits & mask);
	return TRUE;
    }
    return FALSE;
}

BOOL set_numchannels(BYTE numchannels)
{
    if (numchannels >=1 && numchannels <= 2) {
	BYTE fifocfg = 7 + numchannels;
	EP2FIFOCFG = fifocfg;
	EP6FIFOCFG = fifocfg;
	return TRUE;
    }
    return FALSE;
}

struct samplerate_info {
    BYTE rate;
    BYTE wait0;
    BYTE wait1;
    BYTE jump;
    BYTE jopcode;
    BYTE ifcfg;
} samplerates[] = {
    { 48,   1,   1, 9, 3, 0xea },
    { 30,   1,   1, 9, 3, 0xaa },
    { 24,   1,   1, 9, 1, 0xca },
    { 16,   1,   1, 1, 1, 0xca },
    { 12,   1,   2, 1, 1, 0xca },
    {  8,   2,   3, 1, 1, 0xca },
    {  4,   5,   6, 1, 1, 0xca },
    {  2,  11,  12, 1, 1, 0xca },
    {  1,  23,  24, 1, 1, 0xca },
    { 50,  47,  48, 1, 1, 0xca },
    { 20, 119, 120, 1, 1, 0xca },
    { 10, 239, 240, 1, 1, 0xca }
};

BOOL set_samplerate(BYTE rate)
{
    int i;
    for (i = 0; i < sizeof(samplerates)/sizeof(samplerates[0]); i++) {
	if (samplerates[i].rate == rate) {
	    BYTE* data;
	    IFCONFIG = samplerates[i].ifcfg;
	    GPIFABORT = 0xff;
	    GPIFREADYCFG = 0xc0;
	    GPIFCTLCFG = 0x00;
	    GPIFIDLECS = 0x00;
	    GPIFIDLECTL = 0x0f;
	    GPIFWFSELECT = 0x00;
	    GPIFREADYSTAT = 0x00;

	    data = &GPIF_WAVE_DATA + 0;
	    *data++ = samplerates[i].wait0;
	    *data++ = samplerates[i].wait1;
	    *data++ = samplerates[i].jump;
	    data += 5;
	    *data++ = 1;
	    *data++ = 2;
	    *data++ = samplerates[i].jopcode;
	    data += 5;
	    *data++ = 0xff;
	    *data++ = samplerates[i].jopcode == 3 ? 0xff : 0xfb;
	    *data++ = 0xff;
	    data += 5;
	    *data++ = 0x0;
	    *data++ = 0x0;
	    *data++ = 0x12;
	    return TRUE;
	}
    }
    return FALSE;
}

BOOL handle_get_descriptor() {
  return FALSE;
}

//************************** Configuration Handlers *****************************

// change to support as many interfaces as you need
volatile BYTE alt=0; // alt interface

// set *alt_ifc to the current alt interface for ifc
BOOL handle_get_interface(BYTE ifc, BYTE* alt_ifc) {
    *alt_ifc=alt;
    return TRUE;
}
// return TRUE if you set the interface requested
// NOTE this function should reconfigure and reset the endpoints
// according to the interface descriptors you provided.
BOOL handle_set_interface(BYTE ifc,BYTE alt_ifc) {  
    printf ( "Set Interface.\n" );
    if (ifc == 0) {
      alt = alt_ifc;
    //    select_interface(ifc);
    }
    return TRUE;
}

// handle getting and setting the configuration
// 1 is the default.  If you support more than one config
// keep track of the config number and return the correct number
// config numbers are set int the dscr file.
volatile BYTE config=1;
BYTE handle_get_configuration() { 
    return config;
}

// NOTE changing config requires the device to reset all the endpoints
BOOL handle_set_configuration(BYTE cfg) { 
    printf ( "Set Configuration.\n" );
    config=cfg;
    return TRUE;
}


//******************* VENDOR COMMAND HANDLERS **************************

extern volatile __bit active;

BOOL handle_vendorcommand(BYTE cmd) {
    active = 1;
    switch (cmd) {
    case 0xa0:
	// handled by EZ-USB
	return TRUE;

    case 0xe0:
    case 0xe1:
	while (EP0CS & bmEPBUSY);
	set_voltage(cmd - 0xe0, EP0BUF[0]);
	EP0BCH=0;
	EP0BCL=0;
	return TRUE;
    case 0xe2:
	while (EP0CS & bmEPBUSY);
	set_samplerate(EP0BUF[0]);
	EP0BCH=0;
	EP0BCL=0;
	return TRUE;
    case 0xe4:
	while (EP0CS & bmEPBUSY);
	set_numchannels(EP0BUF[0]);
	EP0BCH=0;
	EP0BCL=0;
	return TRUE;
    }
    return FALSE; // not handled by handlers
}

//********************  INIT ***********************

void main_init() {

    REVCTL=3;
    SETIF48MHZ();

    EP4CFG = 0;
    EP8CFG = 0;

    set_voltage(0, 1);
    set_voltage(1, 1);
    set_samplerate(1);
    set_numchannels(1);

    printf ( "Initialization Done.\n" );
}


void main_loop() {
}


