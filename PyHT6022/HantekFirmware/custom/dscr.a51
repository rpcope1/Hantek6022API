; Copyright (C) 2009 Ubixum, Inc. 
;
; This library is free software; you can redistribute it and/or
; modify it under the terms of the GNU Lesser General Public
; License as published by the Free Software Foundation; either
; version 2.1 of the License, or (at your option) any later version.
; 
; This library is distributed in the hope that it will be useful,
; but WITHOUT ANY WARRANTY; without even the implied warranty of
; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
; Lesser General Public License for more details.
; 
; You should have received a copy of the GNU Lesser General Public
; License along with this library; if not, write to the Free Software
; Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

; this is a the default 
; full speed and high speed 
; descriptors found in the TRM
; change however you want but leave 
; the descriptor pointers so the setupdat.c file works right
 

.module DEV_DSCR 

; descriptor types
; same as setupdat.h
DSCR_DEVICE_TYPE=1
DSCR_CONFIG_TYPE=2
DSCR_STRING_TYPE=3
DSCR_INTERFACE_TYPE=4
DSCR_ENDPOINT_TYPE=5
DSCR_DEVQUAL_TYPE=6

; for the repeating interfaces
DSCR_INTERFACE_LEN=9
DSCR_ENDPOINT_LEN=7

; endpoint types
ENDPOINT_TYPE_CONTROL=0
ENDPOINT_TYPE_ISO=1
ENDPOINT_TYPE_BULK=2
ENDPOINT_TYPE_INT=3

    .globl	_dev_dscr, _dev_qual_dscr, _highspd_dscr, _fullspd_dscr, _dev_strings, _dev_strings_end
; These need to be in code memory.  If
; they aren't you'll have to manully copy them somewhere
; in code memory otherwise SUDPTRH:L don't work right
    .area	DSCR_AREA	(CODE)

_dev_dscr:
	.db	dev_dscr_end-_dev_dscr    ; len
	.db	DSCR_DEVICE_TYPE		  ; type
	.dw	0x0002					  ; usb 2.0
	.db	0xff  					  ; class (vendor specific)
	.db	0xff					  ; subclass (vendor specific)
	.db	0xff					  ; protocol (vendor specific)
	.db	64						  ; packet size (ep0)
	.dw	0xB504					  ; vendor id 
	.dw	0x2260					  ; product id
	.dw	0x0000					  ; version id
	.db	1		                  ; manufacturure str idx				
	.db	2				          ; product str idx	
	.db	0				          ; serial str idx 
	.db	1			              ; n configurations
dev_dscr_end:

_dev_qual_dscr:
	.db	dev_qualdscr_end-_dev_qual_dscr
	.db	DSCR_DEVQUAL_TYPE
	.dw	0x0002                              ; usb 2.0
	.db	0
	.db	0
	.db	0
	.db	64                                  ; max packet
	.db	1									; n configs
	.db	0									; extra reserved byte
dev_qualdscr_end:

_highspd_dscr:
	.db	highspd_dscr_end-_highspd_dscr      ; dscr len											;; Descriptor length
	.db	DSCR_CONFIG_TYPE
    ; can't use .dw because byte order is different
	.db	(highspd_dscr_realend-_highspd_dscr) % 256 ; total length of config lsb
	.db	(highspd_dscr_realend-_highspd_dscr) / 256 ; total length of config msb
	.db	1								 ; n interfaces
	.db	1								 ; config number
	.db	0								 ; config string
	.db	0x80                             ; attrs = bus powered, no wakeup
	.db	55                               ; max power = 110mA
highspd_dscr_end:

; all the interfaces next 
; BULK interface
	.db	DSCR_INTERFACE_LEN
	.db	DSCR_INTERFACE_TYPE
	.db	0				 ; index
	.db	0				 ; alt setting idx
	.db	1				 ; n endpoints	
	.db	0xff			 ; class
	.db	0
	.db	0
	.db	0	             ; string index	

; endpoint 6 in 
	.db	DSCR_ENDPOINT_LEN
	.db	DSCR_ENDPOINT_TYPE
	.db	0x86				;  ep1 dir=in and address
	.db	ENDPOINT_TYPE_BULK	; type
	.db	0x00				; max packet LSB
	.db	0x02				; max packet size=512 bytes
	.db	0x00				; polling interval

; ISOCHRONOUS interface
	.db	DSCR_INTERFACE_LEN
	.db	DSCR_INTERFACE_TYPE
	.db	0				 ; index
	.db	1				 ; alt setting idx
	.db	1				 ; n endpoints	
	.db	0xff			 ; class
	.db	0
	.db	1
	.db	0	             ; string index	

; endpoint 2 in 
	.db	DSCR_ENDPOINT_LEN
	.db	DSCR_ENDPOINT_TYPE
	.db	0x82				;  ep1 dir=in and address
	.db	ENDPOINT_TYPE_ISO	; type
	.db	0x00				; max packet LSB
	.db	0x14				; max packet size=3*1024 bytes
	.db	0x01				; polling interval

; ISOCHRONOUS interface  16MB/s
	.db	DSCR_INTERFACE_LEN
	.db	DSCR_INTERFACE_TYPE
	.db	0				 ; index
	.db	2				 ; alt setting idx
	.db	1				 ; n endpoints	
	.db	0xff			 ; class
	.db	0
	.db	1
	.db	0	             ; string index	

; endpoint 2 in 
	.db	DSCR_ENDPOINT_LEN
	.db	DSCR_ENDPOINT_TYPE
	.db	0x82				;  ep1 dir=in and address
	.db	ENDPOINT_TYPE_ISO	; type
	.db	0x00				; max packet LSB
	.db	0x0c				; max packet size=2*1024 bytes
	.db	0x01				; polling interval

; ISOCHRONOUS interface  8MB/s
	.db	DSCR_INTERFACE_LEN
	.db	DSCR_INTERFACE_TYPE
	.db	0				 ; index
	.db	3				 ; alt setting idx
	.db	1				 ; n endpoints	
	.db	0xff			 ; class
	.db	0
	.db	1
	.db	0	             ; string index	

; endpoint 2 in 
	.db	DSCR_ENDPOINT_LEN
	.db	DSCR_ENDPOINT_TYPE
	.db	0x82				;  ep1 dir=in and address
	.db	ENDPOINT_TYPE_ISO	; type
	.db	0x00				; max packet LSB
	.db	0x04				; max packet size=1024 bytes
	.db	0x01				; polling interval

; ISOCHRONOUS interface  4MB/s
	.db	DSCR_INTERFACE_LEN
	.db	DSCR_INTERFACE_TYPE
	.db	0				 ; index
	.db	4				 ; alt setting idx
	.db	1				 ; n endpoints	
	.db	0xff			 ; class
	.db	0
	.db	1
	.db	0	             ; string index	

; endpoint 2 in 
	.db	DSCR_ENDPOINT_LEN
	.db	DSCR_ENDPOINT_TYPE
	.db	0x82				;  ep1 dir=in and address
	.db	ENDPOINT_TYPE_ISO	; type
	.db	0x00				; max packet LSB
	.db	0x04				; max packet size=1024 bytes
	.db	0x02				; polling interval


; ISOCHRONOUS interface  2MB/s
	.db	DSCR_INTERFACE_LEN
	.db	DSCR_INTERFACE_TYPE
	.db	0				 ; index
	.db	5				 ; alt setting idx
	.db	1				 ; n endpoints	
	.db	0xff			 ; class
	.db	0
	.db	1
	.db	0	             ; string index	

; endpoint 2 in 
	.db	DSCR_ENDPOINT_LEN
	.db	DSCR_ENDPOINT_TYPE
	.db	0x82				;  ep1 dir=in and address
	.db	ENDPOINT_TYPE_ISO	; type
	.db	0x00				; max packet LSB
	.db	0x04				; max packet size=1024 bytes
	.db	0x03				; polling interval

; ISOCHRONOUS interface  1MB/s
	.db	DSCR_INTERFACE_LEN
	.db	DSCR_INTERFACE_TYPE
	.db	0				 ; index
	.db	6				 ; alt setting idx
	.db	1				 ; n endpoints	
	.db	0xff			 ; class
	.db	0
	.db	1
	.db	0	             ; string index	

; endpoint 2 in 
	.db	DSCR_ENDPOINT_LEN
	.db	DSCR_ENDPOINT_TYPE
	.db	0x82				;  ep1 dir=in and address
	.db	ENDPOINT_TYPE_ISO	; type
	.db	0x00				; max packet LSB
	.db	0x04				; max packet size=1024 bytes
	.db	0x04				; polling interval

; ISOCHRONOUS interface 500 kB/s
	.db	DSCR_INTERFACE_LEN
	.db	DSCR_INTERFACE_TYPE
	.db	0				 ; index
	.db	7				 ; alt setting idx
	.db	1				 ; n endpoints	
	.db	0xff			 ; class
	.db	0
	.db	1
	.db	0	             ; string index	

; endpoint 2 in 
	.db	DSCR_ENDPOINT_LEN
	.db	DSCR_ENDPOINT_TYPE
	.db	0x82				;  ep1 dir=in and address
	.db	ENDPOINT_TYPE_ISO	; type
	.db	0x00				; max packet LSB
	.db	0x02				; max packet size=512 bytes
	.db	0x04				; polling interval


highspd_dscr_realend:

.even
_fullspd_dscr:
	.db	fullspd_dscr_end-_fullspd_dscr      ; dscr len
	.db	DSCR_CONFIG_TYPE
    ; can't use .dw because byte order is different
	.db	(fullspd_dscr_realend-_fullspd_dscr) % 256 ; total length of config lsb
	.db	(fullspd_dscr_realend-_fullspd_dscr) / 256 ; total length of config msb
	.db	2								 ; n interfaces
	.db	1								 ; config number
	.db	0								 ; config string
	.db	0x80                             ; attrs = bus powered, no wakeup
	.db	55                               ; max power = 110mA
fullspd_dscr_end:


; all the interfaces next 
; BULK interface
	.db	DSCR_INTERFACE_LEN
	.db	DSCR_INTERFACE_TYPE
	.db	0				 ; index
	.db	0				 ; alt setting idx
	.db	1				 ; n endpoints	
	.db	0xff			 ; class
	.db	0
	.db	0
	.db	0	             ; string index	

; endpoint 6 in 
	.db	DSCR_ENDPOINT_LEN
	.db	DSCR_ENDPOINT_TYPE
	.db	0x86				;  ep1 dir=in and address
	.db	ENDPOINT_TYPE_BULK	; type
	.db	0x40				; max packet LSB
	.db	0x00				; max packet size=512 bytes
	.db	0x00				; polling interval

; ISOCHRONOUS interface 1 MB/s
	.db	DSCR_INTERFACE_LEN
	.db	DSCR_INTERFACE_TYPE
	.db	0				 ; index
	.db	1				 ; alt setting idx
	.db	1				 ; n endpoints	
	.db	0xff			 ; class
	.db	0
	.db	1
	.db	0	             ; string index	

; endpoint 2 in 
	.db	DSCR_ENDPOINT_LEN
	.db	DSCR_ENDPOINT_TYPE
	.db	0x82				;  ep1 dir=in and address
	.db	ENDPOINT_TYPE_ISO	; type
	.db	0xff				; max packet LSB
	.db	0x03				; max packet size=1023 bytes
	.db	0x01				; polling interval

; ISOCHRONOUS interface 500 kB/s
	.db	DSCR_INTERFACE_LEN
	.db	DSCR_INTERFACE_TYPE
	.db	0				 ; index
	.db	2				 ; alt setting idx
	.db	1				 ; n endpoints	
	.db	0xff			 ; class
	.db	0
	.db	1
	.db	0	             ; string index	

; endpoint 2 in 
	.db	DSCR_ENDPOINT_LEN
	.db	DSCR_ENDPOINT_TYPE
	.db	0x82				;  ep1 dir=in and address
	.db	ENDPOINT_TYPE_ISO	; type
	.db	0x00				; max packet LSB
	.db	0x02				; max packet size=512 bytes
	.db	0x01				; polling interval

fullspd_dscr_realend:

.even
_dev_strings:
; sample string
_string0:
	.db	string0end-_string0 ; len
	.db	DSCR_STRING_TYPE
    .db 0x09, 0x04 ; 0x0409 is the language code for English.  Possible to add more codes after this. 
string0end:
; add more strings here
_string1:
	.db	string1end-_string1 ; len
	.db	DSCR_STRING_TYPE
    .ascii 'O\0D\0M\0'
string1end:
_string2:
	.db	string2end-_string2 ; len
	.db	DSCR_STRING_TYPE
    .ascii 'H\0a\0n\0t\0e\0k\0D\0S\0O\0006\0000\0002\0002\0B\0E\0'
string2end:


_dev_strings_end:
    .dw 0x0000  ; in case you wanted to look at memory between _dev_strings and _dev_strings_end
