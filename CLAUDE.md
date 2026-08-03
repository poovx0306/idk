# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

CONAFE/CONAAP — a Spanish-language web app for early detection of developmental/autism indicators in children, used by teachers ("docentes"), parents ("padres"), and administrators ("administrativos"). Built on **web.py** (not Flask/Django), with SQLite as the datastore.

## Commands

Run the app:
```bash
python app.py
```
web.py's dev server binds by default; pass a port as an arg if needed (`python app.py 8080`).

Install dependencies:
```bash
pip install -r requirements.txt
```
Note: `requierements.txt` (misspelled, typo file) also exists at the repo root and is slightly out of sync (different `multipart` pin). Use `requirements.txt`; don't edit the misspelled one unless asked to reconcile them.

There is no test suite, linter, or build step configured in this repo.

### Database

The app uses a single SQLite file at `sql/conaap.db`. Schema lives in `sql/script.sql` (idempotent `CREATE TABLE IF NOT EXISTS` statements — re-run it to (re)create tables). Other one-off scripts in `sql/`:
- `sql/crear_usuarios.py`, `sql/asignar_telefono.py` — data seeding/migration helpers, run directly with `python sql/<script>.py`.
- `preguntas.py` (repo root) — drops and reseeds the `preguntas` (questionnaire) table; run with `python preguntas.py`.

`conaap.db` is a real (non-ignored) file checked into git — recent commit history shows merge conflicts on this binary file being resolved by hand ("Resolviendo conflicto de base de datos"). Be careful about local edits to the DB clashing with what's committed.

## Architecture

### Routing

`app.py` is the single entry point. It imports controller classes from every feature module and wires them into one flat `urls` tuple (web.py's URL-pattern-to-classname mapping), then builds `app = web.application(urls, globals())`. **Any new route must be added both as an import and as a `urls` tuple entry in `app.py`.**

Session state is a `web.session.Session` backed by `web.session.DiskStore('sessions')` (session files land in `sessions/`), initialized with `id_usuario`, `nombre`, `rol`, `id_referencia`, `id_infante_actual`. It's attached as `web.config._session` so any controller can reach it via `web.config._session` (or `web.ctx.session`).

Route protection is centralized in `inicios_sesion/proteccion.py`: `RUTAS_PROTEGIDAS` maps specific paths to a required `rol` ('docente' | 'padre' | 'administrativo'); `verificar_sesion()` checks `web.config._session` and redirects to the role's login page (`LOGIN_POR_ROL`) if the session is missing or has the wrong role. Note this list is currently sparse — most feature routes are not yet present in `RUTAS_PROTEGIDAS`, so don't assume a route is protected just because it looks sensitive; check the dict.

### Module layout

Each feature is a self-contained top-level package following this shape:
```
<feature_name>/
  controllers/   # one class per route (GET/POST methods), typically one file
  views/         # web.template templates (.html), rendered via web.template.render('<feature>/views')
```
Login flows are nested one level deeper under `inicios_sesion/<rol>/controllers` and `inicios_sesion/<rol>/views` (`inicios_sesion/docentes`, `inicios_sesion/padres`, `inicios_sesion/administrativos`), plus `inicios_sesion/recuperar` (password recovery) and standalone `inicios_sesion/cerrar_sesion.py` (logout) and `inicios_sesion/proteccion.py` (auth guard, described above).

Controller classes follow the web.py convention: a `GET`/`POST` method per class, `web.input(...)` to read query/form params (with defaults), and `render.<template_name>(...)` to render. There is no shared base template/layout — each view module renders its own full HTML.

Feature modules present: `portal_inicio` (landing page), `inicio_docente`/`inicio_padres` (role dashboards), `deteccion_temprana` (the detection questionnaire flow: registro → cuestionario/api_preguntas → resultado), `estrategias_didacticas` (teaching strategies + activity sheets), `actividades_guardadas` (saved/assigned activities), `actividades_postcrisis` (post-crisis activities for parents), `guias_hogar`/`guias_rapidas` (guides), `boton_crisis` (crisis protocol button + logging to `crisis_atendida`), `avance_infante` (child progress), `mi_perfil_docente` (teacher profile), `administrativos` (admin: questionnaire CRUD under `administrativos/controllers/cuestionarios.py`, admin home under `inicio.py`).

### Data access pattern

There is no ORM or shared DB helper module — **every controller opens its own `sqlite3.connect('sql/conaap.db')` connection**, uses parameterized queries (`?` placeholders — this convention is followed consistently and should be preserved to avoid SQL injection), and closes the connection when done (see `boton_crisis/controllers/boton_crisis.py` and `inicios_sesion/docentes/controllers/index.py` for the idiomatic try/except/finally shape used in login controllers). When adding a new controller that touches the DB, follow this same open/query/close-per-request pattern rather than introducing a new abstraction.

### Auth

Passwords are hashed with SHA-256 (`hashlib.sha256(...).hexdigest()`, see `encriptar()` in each login controller) and compared against the `contrasena` column — no salting/bcrypt. Each role (`docente`, `padre`, `administrativo`) has its own login controller under `inicios_sesion/<rol>/controllers/index.py`, each with its own near-identical `buscarUsuario`/`encriptar` implementation (duplicated per role rather than shared — match this pattern for consistency rather than refactoring into a shared module unless asked). Login failure messages are intentionally generic ("El correo o la contrasena no son correctos.") to avoid leaking whether the email or password was wrong.

### Static assets

`static/images` and `static/js` hold shared static assets served by web.py's default static file handling from `/static/...`.

## Reglas del proyecto

- Todo el código, comentarios y mensajes de commit en español
- Nunca commitear `sql/conaap.db`, la carpeta `sessions/`, `.env`
  ni datos reales de alumnos
- No reescribas `inicios_sesion/`: en ese módulo explícame los
  cambios paso a paso en lugar de aplicarlos
- Contexto: proyecto escolar de UTEC, grupo TICs 32, para CONAFE

