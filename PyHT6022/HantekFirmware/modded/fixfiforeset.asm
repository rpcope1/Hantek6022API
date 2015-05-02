	;; Fix FIFORESET sequences

	;;  orig firmware writes 0x80, 0x02, 0x06, 0x00
	;;  but high bit should remain active: 0x80, 0x82, 0x86, 0x00
	
	ORG	0b94h
	db	082h
	ORG	0b9ah
	db	086h

	ORG	0cf0h
	db	082h
	ORG	0cf6h
	db	086h
