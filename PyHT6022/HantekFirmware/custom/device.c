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
#include <delay.h>

#ifdef DEBUG_FIRMWARE
#include <stdio.h>
#else
#define printf(...)
#endif

// change to support as many interfaces as you need
BYTE altiface = 0; // alt interface
extern volatile WORD ledcounter;




BOOL set_voltage(BYTE channel, BYTE val)
{
    const static BYTE val2bits[] = { 1, 0x24*2, 0x24*1, 1, 1, 0x24*0,
			      1, 1, 1, 1, 0x24*3 };
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
    if (numchannels == 1 || numchannels == 2) {
	BYTE fifocfg = 7 + numchannels;
	EP2FIFOCFG = fifocfg;
	EP6FIFOCFG = fifocfg;
	return TRUE;
    }
    return FALSE;
}

void clear_fifo()
{
    GPIFABORT = 0xff;
    SYNCDELAY3;
    FIFORESET = 0x80;
    SYNCDELAY3;
    FIFORESET = 0x82;
    SYNCDELAY3;
    FIFORESET = 0x86;
    SYNCDELAY3;
    FIFORESET = 0;
}

void stop_sampling()
{
    GPIFABORT = 0xff;
    SYNCDELAY3;
    if (altiface == 0) {
	INPKTEND = 6;
    } else {
	INPKTEND = 2;
    }
}

void start_sampling()
{
    int i;
    clear_fifo();

    for (i = 0; i < 1000; i++);
    while (!(GPIFTRIG & 0x80)) {
	;
    }
    SYNCDELAY3;
    GPIFTCB1 = 0x28;
    SYNCDELAY3;
    GPIFTCB0 = 0;
    if (altiface == 0)
	GPIFTRIG = 6;
    else
	GPIFTRIG = 4;

    // set green led
    // don't clear led
    ledcounter = 0;
    PC0 = 1;
    PC1 = 0;
}

extern __code BYTE highspd_dscr;
extern __code BYTE fullspd_dscr;
void select_interface(BYTE alt)
{
    BYTE *pPacketSize = (USBCS & bmHSM ? &highspd_dscr : &fullspd_dscr)
	+ 9 + 16*alt + 9 + 4;
    altiface = alt;
    if (alt == 0) {
	// bulk on port 6
	EP2CFG = 0x00;
	EP6CFG = 0xe0;
	EP6GPIFFLGSEL = 1;

	EP6AUTOINLENL = pPacketSize[0];
	EP6AUTOINLENH = pPacketSize[1];
    } else {
	// iso on port 2
	EP2CFG = 0xd8;
	EP6CFG = 0x00;
	EP2GPIFFLGSEL = 1;

	EP2AUTOINLENL = pPacketSize[0];
	EP2AUTOINLENH = pPacketSize[1] & 0x7;
	EP2ISOINPKTS = (pPacketSize[1] >> 3) + 1;
    }
}

const struct samplerate_info {
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
    BYTE i = 0;
    while (samplerates[i].rate != rate) {
	i++;
	if (i == sizeof(samplerates)/sizeof(samplerates[0]))
	    return FALSE;
    }

    IFCONFIG = samplerates[i].ifcfg;
    GPIFABORT = 0xff;
    GPIFREADYCFG = 0xc0;
    GPIFCTLCFG = 0x00;
    GPIFIDLECS = 0x00;
    GPIFIDLECTL = 0x0f;
    GPIFWFSELECT = 0x00;
    GPIFREADYSTAT = 0x00;

    AUTOPTRSETUP = 7;
    AUTOPTRH2 = 0xE4;
    AUTOPTRL2 = 0x00;

    EXTAUTODAT2 = samplerates[i].wait0;
    EXTAUTODAT2 = samplerates[i].wait1;
    EXTAUTODAT2 = samplerates[i].jump;
    EXTAUTODAT2 = 0;
    EXTAUTODAT2 = 0;
    EXTAUTODAT2 = 0;
    EXTAUTODAT2 = 0;
    EXTAUTODAT2 = 0;

    EXTAUTODAT2 = 0;
    EXTAUTODAT2 = 2;
    EXTAUTODAT2 = samplerates[i].jopcode;
    EXTAUTODAT2 = 0;
    EXTAUTODAT2 = 0;
    EXTAUTODAT2 = 0;
    EXTAUTODAT2 = 0;
    EXTAUTODAT2 = 0;

    EXTAUTODAT2 = 0xff;
    EXTAUTODAT2 = samplerates[i].jopcode == 3 ? 0xff : 0xfb;
    EXTAUTODAT2 = 0xff;
    EXTAUTODAT2 = 0xff;
    EXTAUTODAT2 = 0xff;
    EXTAUTODAT2 = 0xff;
    EXTAUTODAT2 = 0xff;
    EXTAUTODAT2 = 0xff;

    EXTAUTODAT2 = 0;
    EXTAUTODAT2 = 0;
    EXTAUTODAT2 = 0x12;
    EXTAUTODAT2 = 0;
    EXTAUTODAT2 = 0;
    EXTAUTODAT2 = 0;
    EXTAUTODAT2 = 0;
    EXTAUTODAT2 = 0;

    for (i = 0; i < 96; i++)
	EXTAUTODAT2 = 0;
    return TRUE;
}

BOOL handle_get_descriptor() {
  return FALSE;
}

//************************** Configuration Handlers *****************************

// set *alt_ifc to the current alt interface for ifc
BOOL handle_get_interface(BYTE ifc, BYTE* alt_ifc) {
    (void) ifc; // ignore unused parameter
    *alt_ifc=altiface;
    return TRUE;
}
// return TRUE if you set the interface requested
// NOTE this function should reconfigure and reset the endpoints
// according to the interface descriptors you provided.
BOOL handle_set_interface(BYTE ifc,BYTE alt_ifc) {  
    printf ( "Set Interface.\n" );
    if (ifc == 0) {
      select_interface(alt_ifc);
    }
    return TRUE;
}

// handle getting and setting the configuration
// 1 is the default.  We don't support multiple configurations.
BYTE handle_get_configuration() { 
    return 0;
}

BOOL handle_set_configuration(BYTE cfg) { 
    //    handle_set_interface(cfg, 0);
    return TRUE;
}


//******************* VENDOR COMMAND HANDLERS **************************

BOOL handle_vendorcommand(BYTE cmd) {
    stop_sampling();
    // Set Red LED
    PC0 = 0;
    PC1 = 1;
    ledcounter = 1000;
    switch (cmd) {
    case 0xe0:
    case 0xe1:
	EP0BCH=0;
	EP0BCL=0;
	while (EP0CS & bmEPBUSY);
	set_voltage(cmd - 0xe0, EP0BUF[0]);
	return TRUE;
    case 0xe2:
	EP0BCH=0;
	EP0BCL=0;
	while (EP0CS & bmEPBUSY);
	set_samplerate(EP0BUF[0]);
	return TRUE;
    case 0xe3:
	EP0BCH=0;
	EP0BCL=0;
	while (EP0CS & bmEPBUSY);
	if (EP0BUF[0] == 1)
	    start_sampling();
	return TRUE;
    case 0xe4:
	EP0BCH=0;
	EP0BCL=0;
	while (EP0CS & bmEPBUSY);
	set_numchannels(EP0BUF[0]);
	return TRUE;
    }
    return FALSE; // not handled by handlers
}

//********************  INIT ***********************

void main_init() {
    EP4CFG = 0;
    EP8CFG = 0;

    set_voltage(0, 1);
    set_voltage(1, 1);
    set_samplerate(1);
    set_numchannels(2);
    select_interface(0);

    printf ( "Initialization Done.\n" );
}


void main_loop() {
}


