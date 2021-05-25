import app, argparse


class DatabaseCommands:
	@classmethod
	def init(cls):
		app.query_db(
		    "CREATE TABLE IF NOT EXISTS pages (page_id VARCHAR(6) NOT NULL, key VARCHAR(32) NOT NULL, comment VARCHAR(1024), reveal_comment BOOL DEFAULT 0)",
		    raw=True
		)

	@classmethod
	def provision(cls, id, comment="", reveal_comment=""):
		reveal_comment = ((reveal_comment or "no").lower()[0] == "y")
		id = app.normalize_id(id)
		key = app.add_page_record(id, True)
		app.query_db(
		    "UPDATE pages SET comment = ?, reveal_comment = ? WHERE key = ?",
		    comment,
		    reveal_comment,
		    key,
		    raw=True,
		    write=True
		)
		print(f"Page {id} provisioned! TOTP key is {key}.")

	@classmethod
	def set_comment(cls, id, comment):
		id = app.normalize_id(id)
		app.query_db(
		    "UPDATE pages SET comment = ? WHERE page_id = ?",
		    comment,
		    id,
		    raw=True,
		    write=True
		)

	@classmethod
	def get_comment(cls, id):
		id = app.normalize_id(id)
		print(
		    app.query_db(
		        "SELECT comment FROM pages WHERE page_id = ?",
		        id,
		        one=True,
		        raw=True
		    )["comment"]
		)

	@classmethod
	def get_key(cls, id):
		id = app.normalize_id(id)
		print(
		    app.query_db(
		        "SELECT key FROM pages WHERE page_id = ?",
		        id,
		        one=True,
		        raw=True
		    )["key"]
		)

	@classmethod
	def delete(cls, id):
		id = app.normalize_id(id)
		app.query_db(
		    "DELETE FROM pages WHERE page_id = ?", id, raw=True, write=True
		)


COMMANDS = {
    k: getattr(DatabaseCommands, k)
    for k in DatabaseCommands.__dict__ if not k.startswith("_")
}

parser = argparse.ArgumentParser(
    description="Database admin tool for EnderWeb."
)
parser.add_argument(
    "subcommand",
    help="Command to run. Commands are: " +
    ", ".join([repr(k) for k in COMMANDS])
)
parser.add_argument("args", nargs="*", help="Arguments for subcommand.")
args = parser.parse_args()

if args.subcommand not in COMMANDS:
	parser.error(f"no such command {args.subcommand}")

COMMANDS[args.subcommand](*args.args)
