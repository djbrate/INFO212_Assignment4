## Assignment 4 – Ekte Mat Online

A web-based ordering system for Ekte Mat AS, a catering company in Bergen. It has a
**customer site** (menu by event, cart, ordering, my orders, questions) and an
**admin panel** for staff (food items, pictures, orders, questions).

- Scope: `CLAUDE.md`
- Requirements: `docs/requirements.md`
- Plan: `docs/implementation_plan.md`

Synthetic data only. Built with Flask (MVC) and Neo4j.

### Folder structure (MVC)

```
app/models/        MODEL       domain classes, rules, repositories (all Neo4j access), image service
app/templates/     VIEW        Jinja2 templates (shared base.html for shop and admin)
app/controllers/   CONTROLLER  blueprints: shop.py, account.py, admin.py (/admin)
app/static/        CSS, JavaScript, uploaded pictures (static/uploads is git-ignored)
seed.py            synthetic sample data
index.html         static start page for the VS Code "Go Live" extension
tests/             unit/ and integration/ (no database needed), repo/ (real Neo4j)
```

### 1. Install

Requires Python 3.11+ and Docker.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then set NEO4J_PASSWORD and SECRET_KEY in .env
```

`.env` holds secrets and is git-ignored. Never commit it.

### 2. Start Neo4j

```bash
docker compose up -d               # Neo4j Browser: http://localhost:7474
```

### 3. Seed

```bash
python seed.py                     # adds sample data (safe to run again)
python seed.py --reset             # deletes ALL data in the database first
```

This creates the event categories, 10 food items with placeholder pictures, an admin
(Staff), 3 orders, 2 questions and these test customers (synthetic):

| E-mail | Password |
|---|---|
| kari@example.com | ektemat-test-1 |
| lunch@fjordtek.example | ektemat-test-2 |

### 4. Run

```bash
flask --app run run                # http://localhost:5000
```

- Customer site: http://localhost:5000/menu
- Admin panel: http://localhost:5000/admin/ (no login for now, see FR-A0.1 in `docs/requirements.md`)
- Go Live: open `index.html` with the Go Live extension. It links to the running Flask app.

### 5. Test

Run pytest with the same Python you installed the requirements into (activate `.venv` first,
or use `python -m pytest`).

```bash
pytest                             # all tests; the Neo4j tests are skipped if Neo4j is not running
pytest -m "not neo4j"              # only the fast tests (in-memory fake repositories)
pytest -m neo4j                    # only the repository tests against Neo4j
```

**Warning:** the Neo4j tests wipe the database they connect to. To keep your seeded data,
point them at a separate database with `NEO4J_TEST_URI`, `NEO4J_TEST_USER` and
`NEO4J_TEST_PASSWORD` in `.env`.

**Troubleshooting:** `cannot import name 'GraphDatabase' from 'neo4j' (unknown location)` means the
`neo4j` driver is not installed for the Python running pytest. Run `python -m pip install -r requirements.txt`.

### Pictures

On a food item, choose **Picture**. You can upload a file, or write an instruction for
the image service. You always see a preview first, and nothing is saved until you confirm.
With `IMAGE_PROVIDER=stub` (the default), placeholder pictures are made locally with no
API key. A real image service can be added in `app/models/services/image_service.py`.
Its key goes in `.env` as `IMAGE_API_KEY`.
