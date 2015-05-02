;;; Firmware mod to support 24, 12, and 2 MHz sample rate
;;  and to change the number of channels

samplerate_update code 03d3h
donepacket code 04d7h

GPIFCLK	 equ 0e601h
WAVEDATA equ 0e040h

	ORG	08Fh + 4*3
	ljmp	handle_e4

	;; we start patching at the table switch.
	;; our code is a bit smaller than the original one.
	org 02f5h

	dw	lbl1MHz
	db	1
	dw	lbl2MHz
	db	2
	dw	lbl4MHz
	db	4
	dw	lbl8MHz
	db	8
	dw	lbl100kHz
	db	10
	dw	lbl12MHz
	db	12
	dw	lbl16MHz
	db	16
	dw	lbl200kHz
	db	20
	dw	lbl24MHz
	db	24
	dw	lbl30MHz
	db	30
	dw	lbl48MHz
	db	48
	dw	lbl500kHz
	db	50
	dw      0
	dw	samplerate_update

lbl48MHz:
	mov	A, #0EAh	; 48 MHz, drive ifclk, async fifo, no gstate
	sjmp	lblhighspeed
lbl30MHz:
	mov	A, #0AAh	; 30 MHz, drive ifclk, async fifo, no gstate
lblhighspeed:
	mov	1ah, #1h
	sjmp	update_clock

lbl24MHz:
	mov	R1, #1          ; one wait
	mov	R2, #1		; one wait
	mov	R3, #9		; jmp to 1
	sjmp	lbllowspeed
lbl16MHz:
	mov	R1, #1		; total 1+1+1=3 wait
	mov	R2, #1
	mov	R3, #1		; jmp to 0
	sjmp	lbllowspeed
lbl12MHz:
	mov	R1, #1		; total 1+2+1=4 wait
	mov	R2, #2
	mov	R3, #1		; jmp to 0
	sjmp	lbllowspeed
lbl8MHz:
	mov	R1, #2		; total 2+3+1=6 wait
	mov	R2, #3
	mov	R3, #1		; jmp to 0
	sjmp	lbllowspeed
lbl4MHz:
	mov	R1, #5		; total 5+6+1=12 wait
	mov	R2, #6
	mov	R3, #1		; jmp to 0
	sjmp	lbllowspeed
lbl2MHz:
	mov	R1, #11		; total 11+12+1=24 wait
	mov	R2, #12
	mov	R3, #1		; jmp to 0
	sjmp	lbllowspeed
lbl1MHz:
	mov	R1, #23		; total 23+24+1=48 wait
	mov	R2, #24		; one wait
	mov	R3, #1		; jmp to 0
	sjmp	lbllowspeed
lbl500kHz:
	mov	R1, #47         ; total 47+48+1=96 wait
	mov	R2, #48
	mov	R3, #1		; jmp to 0
	sjmp	lbllowspeed
lbl200kHz:
	mov	R1, #119         ; total 119+120+1=240 wait
	mov	R2, #120
	mov	R3, #1		; jmp to 0
	sjmp	lbllowspeed
lbl100kHz:
	mov	R1, #239        ; total 239+240+1=480 wait
	mov	R2, #240
	mov	R3, #1		; jmp to 0

lbllowspeed:
	mov	DPTR, #WAVEDATA
	mov	A, R1
	movx	@DPTR, A
	inc	DPTR
	mov	A, R2
	movx	@DPTR, A
	inc	DPTR
	mov	A, R3
	movx	@DPTR, A
	clr	A
	mov	1ah, A
	mov	A, #0CAh

update_clock:
	mov	DPTR, #GPIFCLK
	movx	@DPTR, A
	sjmp	samplerate_update

	;; change number of channels
handle_e4:
	;; clear length
	clr	A
	mov	DPTR, #0E68Ah
	movx	@DPTR, A
	mov	DPTR, #0E68Bh
	movx	@DPTR, A
label1:
	mov	DPTR, #0E6A0h
	movx	A, @DPTR
	jb	0E1h, label1	; wait for setup token
	mov	DPTR, #0E740h	; data buffer
	movx	A, @DPTR
	jz	label2		; too small?
	subb	A, #3		; A < 3?
	jnc	label2
	add	A, #10		; add #7 in total (map 1 to 0x8,  2 to 0x9)
	mov	DPTR, #0E61Ah
	movx	@DPTR, A	; set EP6FIFOCFG to 0x9 or 0x8
label2:
	ljmp	donepacket

END

