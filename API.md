# EnderWeb Phoenix API

This document is a reference for the EnderWeb Phoenix API.

## Data types

### Page ID

For now, page IDs consist of 6 numbers, as in the original EnderWeb. Expansion may occur at some time in future if needed.

### Page/EnderWeb Page

Pages are written in a special format based on XML. The full documentation of this format will be forthcoming.

## API Routes

Routes are given relative to the host (i.e; `GET /api/getPage/<id>` is the endpoint at `https://enderweb.twilightparadox.com/api/getPage/<id>`).

Unless otherwise stated, endpoints return a JSON dict on failure, with an English error message in `error`.

### `GET /api/getPage/<id>`

Gets the contents of the page with page ID `id`. Returns an EnderWeb Page on success.

### `GET /api/info/<id>`

Gets info about the page with page ID `id`. Returns a JSON dict on success.

 - `exists` - Whether the page exists (i.e; has a file).
 - `system` - True if the page exists but has no credentials (meaning the page can only be edited in-place on the deployed system).
 - `mtime` - If the page exists, the UNIX timestamp of the last time the file was modified; otherwise, `null`.

### `POST /api/setPage/<id>?token=<token>`

Updates the contents of the page with page ID `id` with the POST body. `token` is a time-based one time password generated from a key given to the page owner when the page is created. This is how page updates are authenticated.
