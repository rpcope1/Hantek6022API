donepacket code 04d7h

	ORG	08Fh + 4*3
	ljmp	handle_e4

	ORG	01123h

	;; clear length
handle_e4:
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
