import time, hmac, base64, hashlib, struct


def pack_counter(t):
	return struct.pack(">Q", t)


def dynamic_truncate(raw_bytes, length):
	offset = raw_bytes[19] & 0x0f
	decimal_value = ((raw_bytes[offset] & 0x7f) << 24) | (
	    (raw_bytes[offset + 1] & 0xff) << 16
	) | ((raw_bytes[offset + 2] & 0xFF) << 8) | (raw_bytes[offset + 3] & 0xFF)
	return str(decimal_value)[-length:]


def hotp(secret, counter, length=6):
	if type(counter) != bytes: counter = pack_counter(int(counter))
	if type(secret) != bytes: secret = base64.b32decode(secret)
	digest = hmac.new(secret, counter, hashlib.sha1).digest()
	return dynamic_truncate(digest, length)


def totp(secret, period=30, length=6):
	"""TOTP is implemented as HOTP, but with the counter being the floor of
           the division of the Unix timestamp by the period (typically 30)."""
	counter = pack_counter(round(time.time() // period))
	return hotp(secret, counter, length)
