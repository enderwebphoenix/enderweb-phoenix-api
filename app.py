#!/usr/bin/env python3

import sqlite3, os, os.path, functools, base64, time, totp

from flask import *

app = Flask(__name__)

DATABASE = "page_credentials.db"

# util methods


def _get_db():
	ret = sqlite3.connect(DATABASE)
	ret.row_factory = sqlite3.Row
	return ret


def get_db():
	db = getattr(g, "_database", None)
	if db is None:
		db = g._database = _get_db()
	return db


def query_db(query, *args, one=False, raw=False, write=False):
	db = _get_db() if raw else get_db()
	cur = db.execute(query, args)
	rv = cur.fetchall()
	cur.close()
	if write: db.commit()
	if raw: db.close()
	return (rv[0] if rv else None) if one else rv


@app.teardown_request
def teardown(exc):
	db = getattr(g, "_database", None)
	if db is not None:
		db.close()


def generate_key(bits=160):
	"""Generates a random key of at least {bits} bits."""
	_bytes = bits / 8
	if round(_bytes % 1, 3) > 0:
		_bytes = (_bytes - round(_bytes % 1, 3)) + 1
	_bytes = int(_bytes)
	return os.urandom(_bytes)


def normalize_id(id):
	try:
		assert type(id) == str, f"ID {id!r} is not a string!"
	except AssertionError:
		if type(id) != int: raise
		id = str(id)
	assert len(id) <= 6, f"ID {id!r} is too long!"
	assert id.isdigit(), f"ID {id!r} is not numeric!"
	return id.rjust(6, "0")


def generate_valid_tokens(key):
	key = base64.b32decode(key)
	current_totp_stamp = round(time.time() / 30)
	ret = []
	for i in (-1, 0, 1):  # accept slightly late/early tokens
		ret.append(totp.hotp(key, current_totp_stamp + i))
	return ret


# db helper methods


def get_page_record(id, raw=False):
	return query_db(
	    "SELECT * FROM pages WHERE page_id = ?", id, one=True, raw=raw
	)


def add_page_record(id, raw=False):
	id = normalize_id(id)
	assert get_page_record(
	    id, raw=raw
	) == None, f"Record already exists for page {id}!"
	key = generate_key()
	key_repr = base64.b32encode(key).decode().strip("=")
	query_db(
	    "INSERT INTO pages (page_id, key) VALUES (?, ?)",
	    id,
	    key_repr,
	    raw=raw,
	    write=True
	)
	return key_repr


# routes


@app.route("/api/getPage/<id>")
def _get_page(id):
	try:
		id = normalize_id(id)
	except AssertionError as e:
		return {"error": e.args[0]}, 400
	fn = os.path.join("pages", id + ".xml")
	if os.path.exists(fn):
		return send_file(fn)
	return _get_page(404)


@app.route("/api/info/<id>")
def _page_info(id):
	try:
		id = normalize_id(id)
	except AssertionError as e:
		return {"error": e.args[0]}, 400
	fn = os.path.join("pages", id + ".xml")
	ret = dict()
	ret["exists"] = os.path.exists(fn)
	creds = get_page_record(id)
	ret["system"] = (creds is None) and ret["exists"]
	ret["mtime"] = os.path.getmtime(fn) if ret["exists"] else None


@app.route("/api/setPage/<id>", methods=["POST"])
def _set_page(id):
	try:
		id = normalize_id(id)
	except AssertionError as e:
		return {"error": e.args[0]}, 400
	token = request.args.get("token")
	if not token:
		return {"error": "Must provide token!"}, 401
	row = get_page_record(id)
	if not row:
		return {
		    "error":
		    f"No key on record! Either page {id} doesn't exist or it's a system page."
		}, 404
	key = row['key']
	valid_tokens = generate_valid_tokens(key)
	if token not in valid_tokens:
		return {"error": "Invalid token!"}, 403
	file = request.files["page"]
	fn = os.path.join("pages", id + ".xml")
	file.save(fn)
	return "", 204
