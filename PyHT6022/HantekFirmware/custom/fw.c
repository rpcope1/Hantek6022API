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
#include <fx2ints.h>
#include <autovector.h>
#include <delay.h>
#include <setupdat.h>

#ifdef DEBUG_FIRMWARE 
#include <serial.h>
#include <stdio.h>
#else
#define printf(...)
#endif

volatile WORD ledcounter = 0;


volatile __bit dosud=FALSE;
volatile __bit dosuspend=FALSE;

// custom functions
extern void main_loop();
extern void main_init();

void main() {

 SETCPUFREQ(CLK_12M); // save energy

 main_init();

 // set up interrupts.
 USE_USB_INTS();
 
 ENABLE_SUDAV();
 ENABLE_USBRESET();
 ENABLE_HISPEED(); 
 ENABLE_SUSPEND();
 ENABLE_RESUME();

 EA=1;

 // init timer2
    RCAP2L = -500 & 0xff;
    RCAP2H = (((WORD)-500) >> 8) & 0xff;
    T2CON = 0;
    ET2 = 1;
    TR2 = 1;

// iic files (c2 load) don't need to renumerate/delay
// trm 3.6
#ifndef NORENUM
 RENUMERATE();
#else
 USBCS &= ~bmDISCON;
#endif
 
    PORTCCFG = 0;
    PORTACFG = 0;
    OEC = 0xff;
    OEA = 0x80;

 while(TRUE) {

     main_loop();

     if (dosud) {
       dosud=FALSE;
       handle_setupdata();
     }

     if (dosuspend) {
        dosuspend=FALSE;
        do {
           printf ( "I'm going to Suspend.\n" );
           WAKEUPCS |= bmWU|bmWU2; // make sure ext wakeups are cleared
           SUSPEND=1;
           PCON |= 1;
           __asm
           nop
           nop
           nop
           nop
           nop
           nop
           nop
           __endasm;
        } while ( !remote_wakeup_allowed && REMOTE_WAKEUP()); 
        printf ( "I'm going to wake up.\n");

        // resume
        // trm 6.4
        if ( REMOTE_WAKEUP() ) {
            delay(5);
            USBCS |= bmSIGRESUME;
            delay(15);
            USBCS &= ~bmSIGRESUME;
        }

     }

 } // end while

} // end main

void resume_isr() __interrupt RESUME_ISR {
 CLEAR_RESUME();
}
  
void sudav_isr() __interrupt SUDAV_ISR {
 dosud=TRUE;
 CLEAR_SUDAV();
}
void usbreset_isr() __interrupt USBRESET_ISR {
 handle_hispeed(FALSE);
 CLEAR_USBRESET();
}
void hispeed_isr() __interrupt HISPEED_ISR {
 handle_hispeed(TRUE);
 CLEAR_HISPEED();
}

void suspend_isr() __interrupt SUSPEND_ISR {
 dosuspend=TRUE;
 CLEAR_SUSPEND();
}

void timer2_isr() __interrupt TF2_ISR {
  PA7 = !PA7;
  if (ledcounter) {
    if (--ledcounter == 0) {
      // clear LED
      PC0 = 1;
      PC1 = 1;
    }
  }
  TF2 = 0;
}
