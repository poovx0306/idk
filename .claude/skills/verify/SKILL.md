---
name: verify
description: Build/launch/drive recipe for verifying changes to the CONAAP web.py app at runtime.
---

# Verifying CONAAP (web.py server)

## Launch

```bash
.venv/bin/python app.py <PORT> &> /tmp/app.log &
echo $! > /tmp/app.pid
for i in {1..30}; do curl -sf http://localhost:<PORT>/ > /dev/null && break; sleep 0.3; done
```

Requires `.venv/` with deps from `requirements.txt` (already present in
this environment) and `sql/conaap.db` present at repo root (already
present; do not recreate/reseed unless asked).

## Gotcha: app.py may fail to import at all

As of 2026-08-03, several controller modules define their class as
`class index` (or `class marcar`) rather than the PascalCase name
`app.py` imports (e.g. `guias_hogar/controllers/guias_hogar.py` has
`class index`, but `app.py` does `from ... import GuiasHogar`). If a
launch fails with `ImportError: cannot import name 'X'`, check the
actual class name in the target file and compare against `app.py`'s
import line — this is a naming-convention mismatch bug in the repo,
not an environment problem. Fix (if in scope) by aliasing the import:
`from module import index as X`.

Quick repo-wide check for this class of bug:
```bash
python3 - <<'EOF'
import re
app = open('app.py').read()
for mod, names in re.findall(r'from ([\w.]+) import (.+)', app):
    if mod.startswith(('inicios_sesion', 'administrativos', 'portal_inicio')):
        continue
    path = mod.replace('.', '/') + '.py'
    try:
        content = open(path).read()
    except FileNotFoundError:
        print(f"MISSING FILE: {path}"); continue
    classes = set(re.findall(r'^class (\w+)', content, re.M))
    for n in [x.strip() for x in names.split(',')]:
        if n not in classes:
            print(f"MISMATCH: {mod} expects '{n}', file has {classes}")
EOF
```

## Drive

Landing page and logins are always safe smoke routes:
```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:<PORT>/
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:<PORT>/login/docente
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:<PORT>/login/padre
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:<PORT>/login/administrativo
```

Most other routes read `web.config._session` / require role-specific
session state (docente/padre/administrativo) and will error or behave
oddly hit anonymously via curl — that's expected, not necessarily a
regression. To drive an authenticated flow, POST valid creds to the
relevant `/login/<rol>` route first and reuse the session cookie
(`curl -c cookies.txt -b cookies.txt ...`).

Note: the central auth guard (`inicios_sesion/proteccion.py`,
`verificar_sesion()`) is currently dead code — never wired into
`app.py` — so routes nominally in `RUTAS_PROTEGIDAS` are NOT actually
enforced. Don't be surprised that "protected" routes return 200 with
no session.

## Known pre-existing DB/schema errors (not caused by typical code changes)

These 500 with `sqlite3.OperationalError` against the current
`sql/conaap.db`, independent of app code — don't mistake them for a
regression in whatever you're verifying:
- `/padre/inicio`, `/padre/guias` — `no such column: publico`
- `/padre/postcrisis` — `no such table: actividad_postcrisis`
- `/padre/postcrisis/marcar` (POST) — `no such table: actividad_postcrisis_realizada`
- `/padre/avance` — `no such table: racha_infante`

## Stop

```bash
lsof -ti:<PORT> -sTCP:LISTEN | xargs -r kill
```
