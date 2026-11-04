# Ekte Mat Online – Implementation plan

- **Date:** 2026-11-04
- **Status:** Reviewed – approved for implementation
- **Reviewer:** whole team, reviewed together in a group session · **Reviewed on:** 2026-11-04 · **Comments:** none, approved as written
- **Based on:** `CLAUDE.md` (current version); `docs/requirements.md` (revision 2026-11-04); decisions with Nathalia 2026-11-04. Requirement IDs (FR-, NFR-, DR-) refer to `docs/requirements.md`.

## Context

`INFO212_Assignment4` has no code yet. It contains only the scope (`CLAUDE.md`), the requirements (`docs/requirements.md`, revised 2026-11-04) and the data pack. This plan turns the **Must** and then the **Should** requirements into a Flask MVC application backed by Neo4j.

A teammate reviews this plan before any code is written, as the project instructions require.

**Decisions made with Nathalia (2026-11-04):**

- **Views:** Jinja2 templates rendered by Flask. A static `index.html` at the repo root works in Go Live and links to the running app.
- **Neo4j:** runs in Docker (`docker-compose.yml`).
- **Tests:** in-memory fake repositories for most tests. A few repository tests run against real Neo4j and are skipped if it isn't running.
- **Images:** a pluggable `ImageService`. A stub generator comes first; a real provider can be added later through `.env`.
- **Cart:** kept in the Flask session. Only submitted orders go to Neo4j.
- **Admin panel:** no access control for now (FR-A0.1). All admin routes go under one `admin` blueprint (FR-A0.2).
- **Team:** the foundation is built together, then each person owns whole features (feature slices).

## Target structure (three MVC layers visible, NFR-1)

```
INFO212_Assignment4/
  index.html                  # static Go Live landing page → links to http://localhost:5000 (NFR-2)
  run.py                      # flask entry point
  seed.py                     # synthetic data (NFR-6)
  docker-compose.yml          # neo4j:5
  requirements.txt  .env.example  pytest.ini  README.MD
  app/
    __init__.py               # create_app(config): loads .env, wires repos + services, registers blueprints
    config.py                 # Config / TestConfig (NEO4J_URI, USER, PASSWORD, SECRET_KEY, IMAGE_PROVIDER)
    models/                   # MODEL
      enums.py                # OrderStatus, PaymentStatus, Allergen, DietaryLabel (NFR-11, DR-2)
      food_item.py  event_category.py  customer.py  staff.py
      order.py                # Order, OrderItem, GuestGroupNote; status state machine (DR-1), total (DR-3)
      question.py             # Question, Answer
      cart.py                 # session cart logic (pure Python)
      validation.py           # shared validators → ValidationError
      services/image_service.py   # ImageService protocol, StubImageService, (later) real provider
      repositories/
        db.py                 # Neo4j driver lifecycle, constraints/indexes
        base.py               # repository interfaces (abstract)
        neo4j_*.py            # FoodItemRepo, CategoryRepo, CustomerRepo, StaffRepo, OrderRepo, QuestionRepo
        fake.py               # in-memory implementations for tests
    controllers/              # CONTROLLER (blueprints)
      shop.py                 # /, /menu, /cart
      account.py              # /register, /login, /logout, /orders, /orders/<no>, questions
      admin.py                # /admin/... (food items, images, orders, questions)
    templates/                # VIEW
      base.html               # shared layout + nav for shop and admin (NFR-2a)
      shop/  account/  admin/
    static/css/main.css  static/js/  static/uploads/ (gitignored)
  tests/
    conftest.py               # app + client fixtures using fake repos; neo4j fixture with skip
    unit/  integration/  repo/   # repo/ = real Neo4j tests
```

**Design rule:** controllers call repositories and services. Only the `neo4j_*.py` files contain Cypher (NFR-3). `create_app` chooses Neo4j or fake repositories based on the config, and stores them in `app.extensions["repos"]`.

## Graph model (DR-6)

`(Customer)-[:PLACED]->(Order)-[:HAS_ITEM]->(OrderItem {quantity, unit_price})-[:OF]->(FoodItem)-[:IN_CATEGORY]->(EventCategory)`

`(Order)-[:HAS_NOTE]->(GuestGroupNote {label, count})`

`(Customer)-[:ASKED]->(Question)-[:ABOUT]->(Order)` and `(Staff)-[:WROTE]->(Answer)-[:ANSWERS]->(Question)`

**Constraints:**

- Unique `Order.order_no` (DR-4).
- Unique `Customer.email`.
- Unique `EventCategory.slug`.
- Unique id on `FoodItem`.

## Phases

Each phase follows the project rule: a short plan note for the feature, teammate review, tests for its main behaviour, `pytest` green, then report the feature and commit.

### Phase 0: Housekeeping (together)

- Commit the current `CLAUDE.md`, `.gitignore` and `docs/`.
- Add `requirements.txt`: Flask, neo4j, python-dotenv, Werkzeug, pytest, Pillow.
- Add `.env.example`, `docker-compose.yml` and `pytest.ini`.

### Phase 1: Foundation (together, about 1 sprint)

1. `create_app`, `config.py`, `db.py` with constraints, and `base.html` plus `main.css` with shared navigation (NFR-2a).
2. `enums.py`, `validation.py` and all domain classes, with the `Order` state machine and the calculated total.
3. Repository interfaces, the fake implementations and the Neo4j implementations.
4. A first version of `seed.py`: event categories, one staff admin, two test customers, and the autumn and event dishes from `requirements.md` section 5.
5. `index.html`, plus README commands for install, `docker compose up -d`, `python seed.py`, `flask --app run run` and `pytest` (NFR-7).
6. **Tests:**
   - state-machine transitions, both allowed and forbidden
   - the total calculation
   - validators
   - repository round-trip against Neo4j (skipped without Neo4j)

### Phase 2: Must features (three parallel slices)

| Slice | Owner | Requirements | Main tests |
|---|---|---|---|
| **A. Catalogue and images** | Dev 1 | Admin create, edit and remove food items, with categories, allergens, dietary labels and the published flag (FR-A1.1–1.5). Image upload, or an AI instruction through `StubImageService`, then a preview page; the image is saved only on confirm (FR-A2.1–2.4). Customer menu cards grouped by category, showing image, price, minimum order and allergens (FR-C1.1–1.2). | Invalid price or minimum is rejected; unpublished items are hidden; the image is not saved before confirm; menu grouping |
| **B. Cart, account, ordering** | Dev 2 | Session cart: add, change, remove, estimated total, minimum-order and whole-number checks (FR-C2.1–2.4). Register and login with hashed passwords (FR-C3.1, NFR-4). Order form with event date, guests, address and notes per guest group, starting as submitted and not paid (FR-C3.2–3.5). My orders, showing only the customer's own orders (FR-C4.1–4.2). | A quantity below the minimum is rejected; a past date or guests outside 1–1000 are rejected; you must log in to submit; customer A cannot see B's order |
| **C. Admin orders and questions** | Dev 3 | Order list filtered by status and event date, order detail page, status changes through the state machine, payment status set by hand, highlighted allergy box (FR-A3.1–3.5). Customer asks a question on their own order (FR-C5.1–5.2); admin reads and answers it (FR-A4.1–4.2). | Filters; an illegal transition is refused; payment change; the answer appears on the customer's order page |

**How the slices depend on each other:** slice C needs orders, so in the meantime it uses orders created by `seed.py` and the fake repositories. Slice B's order form uses the categories and items from the Phase 1 seed.

### Phase 3: Should features (after Must is green)

- **FR-A1.6 and FR-C1.4:** an `origin` field on FoodItem, shown on the card.
- **FR-C1.3:** dietary label badges on the cards.
- **FR-C3.6:** confirmation page showing the order number.
- **FR-A3.6:** a "kitchen has seen allergies" button that stores `allergy_confirmed_at`.
- **FR-A3.7 and DR-5:** total covers per event date on the order list, with a warning above 400, or above 250 when a wedding served dinner is booked that day.
- **FR-A4.3:** unanswered questions are badged, and `/admin/questions?unanswered=1` lists them.

### Phase 4: Polish

- Update the seed data and the README.
- Check page speed (NFR-9; Neo4j queries should use the indexes).
- Make sure dates show as YYYY-MM-DD and prices in NOK everywhere (NFR-12).
- Final full test run.

## Verification

- **Unit and integration tests:** `pytest` runs with fake repositories and no Neo4j needed. `pytest -m neo4j` runs the repository tests after `docker compose up -d`.
- **Manual end-to-end:**
  1. `python seed.py`, then `flask --app run run`, then open `index.html` with Go Live and follow the link.
  2. As a customer: register, add a dish below its minimum (rejected), then a valid quantity, submit the order, see it under My orders, and ask a question.
  3. As admin at `/admin`: filter the order list, approve the order, mark it deposit paid, answer the question, then check the answer appears for the customer.
  4. Add a food item with a stub-generated image, confirm it, publish it, and check the card on `/menu`.
- **Neo4j Browser** (`localhost:7474`): run `MATCH p=(:Customer)-[:PLACED]->(:Order)-[:HAS_ITEM]->()-[:OF]->() RETURN p` to see the graph.
- **Secrets check:** `git status` shows that `.env` is not tracked, and `git grep -i "api_key"` only finds `.env.example`.
