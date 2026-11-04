# Ekte Mat Online – Requirements list

- **Date:** 2026-11-04
- **Status:** Draft for team review
- **Revision:** 2026-11-04, updated to match the revised `CLAUDE.md` (see section 9)

## How to read this document

**Based on:**
- `CLAUDE.md`, which is the scope we build against
- `docs/data_pack_analysis.md`
- the files in `Lab_EkteMat_DataPack_STUDENTS/EkteMat_project_inbox/` (shortened to `inbox/` below)

**Rule used:** a requirement that goes against `CLAUDE.md` is left out. Section 6 lists what was removed and why.

**Priority (MoSCoW):**
- **Must:** the core scope in `CLAUDE.md`.
- **Should / Could:** stakeholder needs that fit inside `CLAUDE.md` without contradicting it.

---

## 1. Admin panel (Ekte Mat staff)

### 1.0 Access

| ID | Requirement | Priority | Source |
|---|---|---|---|
| FR-A0.1 | The admin panel is reachable without login for now. Access control for staff is deferred (see section 8). | Must | Team decision 2026-11-04; `CLAUDE.md` (Admin panel; Security basics) |
| FR-A0.2 | The admin pages are reached from their own URL prefix (e.g. `/admin`) through the `admin` blueprint, so access control can be added later in one place. | Should | `CLAUDE.md` (HOW: Architecture); team decision 2026-11-04 |

### 1.1 Food items

| ID | Requirement | Priority | Source |
|---|---|---|---|
| FR-A1.1 | Staff can add, edit and remove a food item. Each item has a name, a description, a price in NOK, a minimum order quantity, event categories, allergens, dietary labels and a published flag. | Must | `CLAUDE.md` (Admin panel 1) |
| FR-A1.2 | Only published items are shown on the customer site. | Must | `CLAUDE.md` (Admin panel 1) |
| FR-A1.3 | Allergens are chosen from a fixed list that includes at least fish, milk, gluten, nuts, celery, mustard and shellfish. | Must | `inbox/lunch menu autumn.txt`; `inbox/customer_emails_export.csv` (E022) |
| FR-A1.4 | Dietary labels are chosen from a fixed list that includes at least vegan, vegetarian, gluten-free, lactose-free and halal. | Must | `inbox/orders_2024_2025_export.xlsx` (dietary_notes) |
| FR-A1.5 | The price must be greater than 0 NOK and the minimum order must be at least 1. Invalid values are rejected with a message. | Must | `inbox/orders_2024_2025_export.xlsx` (2 rows with price 0) |
| FR-A1.6 | A food item can record the origin of its main ingredients (farm, boat, region). | Should | `inbox/interview_Ingrid_owner.txt`; `inbox/interview_Mateo_head_chef.txt`; `inbox/customer_emails_export.csv` (E008) |
| FR-A1.7 | A food item can be marked as seasonal, with an availability period (e.g. rakfisk, November only). | Could | `inbox/lunch menu autumn.txt`; `inbox/interview_Mateo_head_chef.txt` |

### 1.2 Images

| ID | Requirement | Priority | Source |
|---|---|---|---|
| FR-A2.1 | Staff can upload a picture for each food item. | Must | `CLAUDE.md` (Admin panel 2) |
| FR-A2.2 | Instead of uploading, staff can write an instruction that an AI agent or image service uses to create or modify the picture. | Must | `CLAUDE.md` (Admin panel 2) |
| FR-A2.3 | Staff preview the resulting picture and must confirm before it is saved. | Must | `CLAUDE.md` (Admin panel 2) |
| FR-A2.4 | API keys for the image service are read from `.env` and never stored in the repository. | Must | `CLAUDE.md` (Security basics) |

### 1.3 Orders

| ID | Requirement | Priority | Source |
|---|---|---|---|
| FR-A3.1 | Staff see a list of all customer orders, which can be filtered by order status and by event date. | Must | `CLAUDE.md` (Admin panel 3) |
| FR-A3.2 | Each order has its own page showing customer, event date, guests, delivery address, items, estimated total and the allergy and dietary notes per guest group. | Must | `CLAUDE.md` (Admin panel 3, Customer Site 3) |
| FR-A3.3 | Staff can change the order status. Only these transitions are allowed: submitted → approved → in preparation → delivered; submitted/approved → rejected; submitted/approved/in preparation → cancelled. | Must | `CLAUDE.md` (Admin panel 3) |
| FR-A3.4 | Staff can set the payment status by hand: not paid, deposit paid, invoiced or paid. The system does not take payments (see section 6). | Must | `CLAUDE.md` (Admin panel 3; Customer Site 3: "No payment solution is needed") |
| FR-A3.5 | Allergy and dietary notes are highlighted on the order page so they cannot be missed. | Must | `inbox/interview_Sunniva_event_coordinator.txt`; `inbox/interview_Mateo_head_chef.txt` |
| FR-A3.6 | Staff can mark that the kitchen has seen an order's allergy information. The order shows when this was confirmed. | Should | `inbox/interview_Sunniva_event_coordinator.txt`; `inbox/customer_emails_export.csv` (E002) |
| FR-A3.7 | The order list shows the total guests already booked per event date, with a warning when a day exceeds 400 covers, or 250 when a served wedding dinner is booked. | Should | `inbox/interview_Sunniva_event_coordinator.txt`; `inbox/orders_2024_2025_export.xlsx` (README; 19 days over capacity) |
| FR-A3.8 | A kitchen view lists the orders for a chosen day, with portions per dish and allergies shown in red. | Could | `inbox/interview_Mateo_head_chef.txt` |
| FR-A3.9 | A prep list shows the total quantity of each food item for the next 3 days. | Could | `inbox/interview_Mateo_head_chef.txt` |

### 1.4 Questions

| ID | Requirement | Priority | Source |
|---|---|---|---|
| FR-A4.1 | Staff can read the customer questions linked to each order. | Must | `CLAUDE.md` (Admin panel 4) |
| FR-A4.2 | Staff can write an answer, which the customer then sees on the order. | Must | `CLAUDE.md` (Admin panel 4) |
| FR-A4.3 | Unanswered questions are clearly marked and can be listed, so that none get lost. | Should | `inbox/interview_Ingrid_owner.txt` (lost inquiries); `inbox/customer_emails_export.csv` (E006, E011) |

---

## 2. Customer site

### 2.1 Menu by event

| ID | Requirement | Priority | Source |
|---|---|---|---|
| FR-C1.1 | Published food items are shown as cards, grouped by event category: corporate lunch, private party, confirmation, wedding, conference, Christmas party (julebord), birthday and other events. | Must | `CLAUDE.md` (Context; Customer Site 1) |
| FR-C1.2 | Each card shows the picture, price in NOK, minimum order and allergens. | Must | `CLAUDE.md` (Customer Site 1) |
| FR-C1.3 | Dietary labels (e.g. gluten-free, vegan) are shown clearly on each card. | Should | `inbox/customer_emails_export.csv` (E019, E012) |
| FR-C1.4 | Each card shows the origin of the food when it is recorded (see FR-A1.6). | Should | `inbox/interview_Ingrid_owner.txt`; `inbox/customer_emails_export.csv` (E008) |
| FR-C1.5 | The menu can be viewed in Norwegian and English. | Could | `inbox/current_IT_landscape.txt`; `inbox/customer_emails_export.csv` (E012) |

### 2.2 Shopping cart

| ID | Requirement | Priority | Source |
|---|---|---|---|
| FR-C2.1 | Customers can add items to the cart, change quantities and remove items. | Must | `CLAUDE.md` (Customer Site 2) |
| FR-C2.2 | The cart shows an estimated total in NOK (quantity × price, summed). | Must | `CLAUDE.md` (Customer Site 2) |
| FR-C2.3 | A quantity below an item's minimum order is rejected with a clear message. | Must | `CLAUDE.md` (Customer Site 2) |
| FR-C2.4 | Quantities must be whole numbers greater than 0. | Must | `inbox/orders_2024_2025_export.xlsx` (negative guest numbers) |

### 2.3 Order

| ID | Requirement | Priority | Source |
|---|---|---|---|
| FR-C3.1 | A customer must log in, or register, before submitting an order. | Must | `CLAUDE.md` (Customer Site 3) |
| FR-C3.2 | The order form collects the event date, number of guests, delivery address, and allergy and dietary notes per guest group (e.g. "nut allergy × 2"). | Must | `CLAUDE.md` (Customer Site 3); `inbox/GDPR note from consultant.txt` |
| FR-C3.3 | Allergy notes are stored per guest group, never per named guest. | Must | `inbox/GDPR note from consultant.txt` |
| FR-C3.4 | The event date must be in the future. The number of guests must be between 1 and a sensible upper limit (e.g. 1000). | Must | `inbox/orders_2024_2025_export.xlsx` (event before order date; 5000 guests) |
| FR-C3.5 | A submitted order gets the status "submitted" and the payment status "not paid". No payment is taken. | Must | `CLAUDE.md` (Customer Site 3) |
| FR-C3.6 | After submitting, the customer sees a confirmation with the order number. | Should | `inbox/customer_emails_export.csv` (E011) |
| FR-C3.7 | The customer can choose delivery or pick-up. | Could | `inbox/customer_emails_export.csv` (E014); `inbox/orders_2024_2025_export.xlsx` (delivery_method) |
| FR-C3.8 | The customer can give a wanted delivery time or time window. | Could | `inbox/customer_emails_export.csv` (E018) |

### 2.4 My orders

| ID | Requirement | Priority | Source |
|---|---|---|---|
| FR-C4.1 | A logged-in customer sees a list of their own orders, with the current order status and payment status, and can open each order again later. | Must | `CLAUDE.md` (Customer Site 4; WHY: Customer Site) |
| FR-C4.2 | Customers can only see their own orders. | Must | `CLAUDE.md` (Customer Site 4) |
| FR-C4.3 | A customer can copy a previous order into the cart to re-order. | Could | `inbox/interview_Fjordtek_customer.txt`; `inbox/customer_emails_export.csv` (E028) |

### 2.5 Questions

| ID | Requirement | Priority | Source |
|---|---|---|---|
| FR-C5.1 | A customer can ask a question about one of their orders. | Must | `CLAUDE.md` (Customer Site 5) |
| FR-C5.2 | The customer can read Ekte Mat's answer on that order. | Must | `CLAUDE.md` (Customer Site 5) |

---

## 3. Non-functional and technical requirements

| ID | Requirement | Source |
|---|---|---|
| NFR-1 | The application uses MVC with Flask. Models hold the domain classes and all data access, views are Jinja2 templates (or a front end calling a JSON API), and controllers are Flask routes in blueprints (e.g. shop, account, admin). The three layers are visible in the folder structure. | `CLAUDE.md` (HOW) |
| NFR-2 | The front end uses HTML and CSS, plus JavaScript where needed. An `index.html` exists so the site can be opened with the "Go Live" extension. | `CLAUDE.md` (HOW: Front end; intro) |
| NFR-2a | The interface is easy to navigate and consistent between the admin panel and the customer site: one shared base layout, navigation and stylesheet. | `CLAUDE.md` (HOW: Front end) |
| NFR-3 | Neo4j is the storage layer of the finished system. It stores customers, staff, food items, event categories, orders, order items, questions and answers as nodes, linked by relationships (see DR-6). All database access is organised in the model/data-access layer (repository classes); controllers and templates never run queries. | `CLAUDE.md` (HOW: Data storage) |
| NFR-4 | Login pages are only required for customers. Passwords are stored hashed. The admin panel has no login for now (FR-A0.1). | `CLAUDE.md` (Security basics); team decision 2026-11-04 |
| NFR-5 | API keys and secrets live in `.env`, `.env` is in `.gitignore`, and no secrets are committed. | `CLAUDE.md` (Security basics) |
| NFR-6 | Only synthetic data is used. A seed script creates the event categories, sample food items, an admin (a Staff node) and test customers. | `CLAUDE.md` (Running it; HOW: Data storage) |
| NFR-7 | The README gives the commands to install, seed, run and test the application. | `CLAUDE.md` (Running it) |
| NFR-8 | Each feature has at least one automated test of its main behaviour, and the test suite is run before committing. | Project instructions |
| NFR-9 | Pages load fast (target < 2 s on a normal connection). The old booking plugin took about 10 s. | `inbox/interview_Mateo_head_chef.txt` |
| NFR-10 | Personal data is kept to a minimum. If the app is hosted, hosting must be in the EU/EEA. | `inbox/GDPR note from consultant.txt`; `inbox/current_IT_landscape.txt` |
| NFR-11 | Status values come from fixed lists (no free text), so no typos like "Confimed" and no channel written in 10 different ways. | `inbox/orders_2024_2025_export.xlsx` |
| NFR-12 | Dates are shown and stored as YYYY-MM-DD, and money is shown in NOK. | Project instructions |

---

## 4. Domain rules (for the model layer)

| ID | Rule | Source |
|---|---|---|
| DR-1 | Order status follows the state machine in FR-A3.3. Delivered, rejected and cancelled are final. | `CLAUDE.md` (Admin panel 3) |
| DR-2 | Payment status is one of: not paid, deposit paid, invoiced, paid. | `CLAUDE.md` (Admin panel 3) |
| DR-3 | The estimated total equals the sum of quantity × unit price for all order lines. It is calculated by the system, never typed in. | `CLAUDE.md` (Customer Site 2); `inbox/orders_2024_2025_export.xlsx` (12 rows with wrong totals) |
| DR-4 | Order numbers are unique (no duplicates). | `inbox/orders_2024_2025_export.xlsx` (5 duplicate rows) |
| DR-5 | Daily kitchen capacity is 400 covers, or 250 when a served wedding dinner is booked that day. Exceeding it gives a warning (FR-A3.7), not a block. | `inbox/interview_Sunniva_event_coordinator.txt`; `inbox/orders_2024_2025_export.xlsx` (README) |
| DR-6 | Graph model. Nodes: `Customer`, `Staff`, `FoodItem`, `EventCategory`, `Order`, `OrderItem`, `Question`, `Answer` (plus `GuestGroupNote` for allergy notes). Relationships: `(Customer)-[:PLACED]->(Order)`, `(Order)-[:HAS_ITEM]->(OrderItem)`, `(OrderItem)-[:OF]->(FoodItem)`, `(FoodItem)-[:IN_CATEGORY]->(EventCategory)`, `(Order)-[:HAS_NOTE]->(GuestGroupNote)`, `(Customer)-[:ASKED]->(Question)`, `(Question)-[:ABOUT]->(Order)`, `(Answer)-[:ANSWERS]->(Question)`, `(Staff)-[:WROTE]->(Answer)`. An `OrderItem` stores the quantity and the unit price at the time of ordering. | `CLAUDE.md` (HOW: Data storage); `inbox/GDPR note from consultant.txt` (notes per guest group) |

---

## 5. Suggested event categories for seed data

| Category | Example from the data pack | Source |
|---|---|---|
| Birthday | Birthday for 30 people | `CLAUDE.md`; `inbox/customer_emails_export.csv` (E009) |
| Confirmation | Konfirmasjon buffet, 395 NOK/pers | `CLAUDE.md`; `inbox/orders_2024_2025_export.xlsx` |
| Wedding | Wedding served dinner (3 courses), 875 NOK/pers | `CLAUDE.md`; `inbox/orders_2024_2025_export.xlsx` |
| Conference / corporate lunch | Seasonal lunch buffet 229 NOK/pers; Meeting sandwiches 129 NOK/pers | `CLAUDE.md`; `inbox/orders_2024_2025_export.xlsx` |
| Christmas party (julebord) | Traditional julebord buffet, 595 NOK/pers | `CLAUDE.md`; `inbox/orders_2024_2025_export.xlsx` |
| Private party | Private customers are 258 of 820 orders | `CLAUDE.md` (Context); `docs/data_pack_analysis.md` (2.2) |
| Other events | Catch-all for events not listed above | `CLAUDE.md` (Context) |
| Autumn lunch dishes | Fish soup 189 NOK; Voss lamb 245 NOK; beetroot salad 165 NOK; rakfisk 210 NOK | `inbox/lunch menu autumn.txt` |

---

## 6. Left out because they go against `CLAUDE.md`

| Stakeholder need | Why it is left out | Source of need | Conflicting rule |
|---|---|---|---|
| Take a 30 % deposit online when booking ("no deposit, no booking") | No payment solution is to be built. Staff can still record "deposit paid" by hand (FR-A3.4). | `inbox/interview_Ingrid_owner.txt` | `CLAUDE.md` (Customer Site 3) |
| Vipps payment for private customers, with e-mail receipt | Payment solution | `inbox/interview_Ingrid_owner.txt`; `inbox/customer_emails_export.csv` (E009) | `CLAUDE.md` (Customer Site 3) |
| Automatic invoicing via Fiken, monthly EHF invoices with PO numbers or cost-centre codes, automatic payment reminders | Payment and invoicing solution. Staff can record "invoiced" by hand. | `inbox/interview_Fjordtek_customer.txt`; `inbox/interview_Sunniva_event_coordinator.txt`; `inbox/customer_emails_export.csv` (E004, E016, E030) | `CLAUDE.md` (Customer Site 3) |
| PIN login for the kitchen tablet | Only customer login pages are in scope. A kitchen view (FR-A3.8) is still possible, without a separate login. | `inbox/interview_Mateo_head_chef.txt` | `CLAUDE.md` (Security basics) |
| Company accounts with several users, an approval step above 15 000 NOK, and read-only access for accountants | Needs roles and approvals beyond basic customer login. | `inbox/interview_Fjordtek_customer.txt`; `inbox/customer_emails_export.csv` (E016, E029) | `CLAUDE.md` (Security basics) |
| Keep orders in Excel or Google Drive, or import the real order sheet | Storage must be Neo4j (via the model layer), and only synthetic seed data is used. | `inbox/current_IT_landscape.txt`; `inbox/notes meeting 12 aug FINAL.txt` | `CLAUDE.md` (HOW: Data storage; Running it) |

## 7. Outside the scope for now (do not conflict, but not planned)

These are not against `CLAUDE.md`, but they are not part of its WHAT section. They can be added later if a stakeholder need is named.

| Item | Source |
|---|---|
| Automatic reminder e-mail 7 days before the event | `inbox/interview_Sunniva_event_coordinator.txt` |
| Kitchen view working offline | `inbox/interview_Mateo_head_chef.txt` |
| Ingredients linked to suppliers, prep list in kilos | `inbox/interview_Mateo_head_chef.txt` |
| Standing (recurring) weekly orders | `inbox/customer_emails_export.csv` (E007); `inbox/interview_Fjordtek_customer.txt` |
| Self-service access and deletion of personal data | `inbox/GDPR note from consultant.txt`; `inbox/customer_emails_export.csv` (E010) |
| Volume discounts, children's menu, CO₂ data per order | `inbox/customer_emails_export.csv` (E020, E027, E021) |

## 8. Deviations from `CLAUDE.md` agreed by the team

| Item | `CLAUDE.md` says | Decision | Source |
|---|---|---|---|
| Access to the admin panel | "Customers should have no acces to this panel." | No access control for now, because this is a school project. The admin pages stay under one blueprint (FR-A0.2), so a staff check can be added later in one place. | Team decision 2026-11-04; `CLAUDE.md` (Admin panel) |

## 9. Change log

| Date | Change | Source |
|---|---|---|
| 2026-11-04 | First draft. | `CLAUDE.md` (earlier version) |
| 2026-11-04 | Updated to the revised `CLAUDE.md`: added FR-A0.1 and FR-A0.2 (admin access) and NFR-2a (consistent interface); widened the event categories in FR-C1.1 and section 5; NFR-3 and the new DR-6 describe the Neo4j graph model; NFR-4 and NFR-6 updated; FR-C4.1 adds "open again later"; added sections 8 and 9. Removed the citation of `INFO212_Oblig4_EkteMat_Claude_Code.pdf` from NFR-3, because that file was deleted from the repository (commit `efcabae`). | `CLAUDE.md` (current version); team decision 2026-11-04 |
