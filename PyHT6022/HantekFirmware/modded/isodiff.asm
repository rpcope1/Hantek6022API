	org	03aah
	db	018h		; EP2FIFOCFG

	org 	0bbfh
	db	0abh
	;; mov	A, 0ABh		; EP24FIFOFLGS


	org 	0bdbh
	db	04h
	;; mov	0BBh, 04h	; GPIFTRIG: READ 2


	org 	0cc8h
	db	0d8h
	;; mov	A, 0d8h		; EP2CFG = 0xd8 In ISO 1024byte

	org 	0cd9h
	;; mov	A, 000h		; EP6CFG = 0x00 not valid


	org 	0d09h
	db	09h
	;; mov	A, 09h		; EP2FIFOCFG = 0x09 (AUTOOUT, WORD)
	;; ...
	org 	0d10h
	db	040h, 074h, 03h
	;; mov	DPTR, #0e640h
	;; mov	A, 03h		; EP2ISOINPKTS = 3 packets per frame
	
	org	0d1bh
	db	01h
	;; mov	A, #1h		; EP2GPIFFLGSEL = 0x01

 	org	0e1ch
	;; high speed configuration:
	db	9		; length
	db	2		; Configuration
	db	25, 0		; len including interface and endpoints (25 bytes)
	db	1		; number of interfaces
	db	1		; configuration number
	db	0		; configuration name (string index) = None
	db	080h		; attributes - Bus Powered, No Wakeup
	db	50		; maximum power 100 mA
	
	db	9		; length
	db	4		; interface descriptor
	db	0		; interface number
	db	0		; alternate setting value
	db	1		; number of endpoints
	db	0ffh,0,0	; interface class: vendor specific
	db	0		; name (None)

	db	7		; length
	db	5		; end point
	db	82h		; endpoint address: IN 2
	db	5		; attributes (ISO)
	db	00h,14h		; maxPacket size 3*(1024)
	db	1		; polling interval in ms

	org	0e3ch
	;; low speed configuration:
	db	9		; length
	db	2		; Configuration
	db	25, 0		; len including interface and endpoints (25 bytes)
	db	1		; number of interfaces
	db	1		; configuration number
	db	0		; configuration name (string index) = None
	db	080h		; attributes - Bus Powered, No Wakeup
	db	50		; maximum power 100 mA
	
	db	9		; length
	db	4		; interface descriptor
	db	0		; interface number
	db	0		; alternate setting value
	db	4		; number of endpoints
	db	0ffh,0,0	; interface class: vendor specific
	db	0		; name (None)

	db	7		; length
	db	5		; end point
	db	82h		; endpoint address: IN 2
	db	1		; attributes (ISO async)
	db	0ffh,03h	; maxPacket size (64)
	db	1		; polling interval in ms


	;; set EP2 max size to 1024/1023
	;; instead of setting EP6 maxsize to 512/64
	org	01058h
	db	020h, 074h, 04h
	org	01062h
	db	021h

	org	0106eh
	mov	A, #03h
	mov	DPTR, #0e620h
	
	org	01078h
	db	021h, 074h, 0ffh
