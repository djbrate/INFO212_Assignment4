# Ekte Mat Online – Analysis of the project data pack

- **Date:** 2026-11-04
- **Source folder:** `Lab_EkteMat_DataPack_STUDENTS/EkteMat_project_inbox/`
- **Status:** Draft for team review
- **Note:** All source material is synthetic (INFO212 Lab 7). No inbox files were modified.

---

## 1. Problems today

| # | Problem | Evidence | Source |
|---|---------|----------|--------|
| P1 | Inquiries are lost or answered late | Three julebord requests found in spam after the date had passed (≈ 60 000 NOK lost). First reply takes 1–2 days, up to 7 in December and May. A customer went to another caterer after waiting 6 days. | `interview_Ingrid_owner.txt`, `interview_Sunniva_event_coordinator.txt`, `asis_order_process.md`, `customer_emails_export.csv` (E006) |
| P2 | Manual, fragile process | E-mail or phone → quote in Word → Excel row → printout on the kitchen board. Changes, deposit requests and the 7-day confirmation are "sometimes forgotten". | `asis_order_process.md` |
| P3 | Allergy information is a safety risk | Nut incident in 2024. Customers ask whether the kitchen got their allergy information, add allergies on the day, and report missing vegan dishes. | `interview_Sunniva_event_coordinator.txt`, `customer_emails_export.csv` (E002, E017, E019, E022) |
| P4 | Manual invoicing and reconciliation | Invoices created by hand in Fiken and reconciled against Excel monthly. A PDF invoice was rejected (EHF required), and a reminder was sent for a bill that had already been paid. | `asis_order_process.md`, `customer_emails_export.csv` (E004, E030) |
| P5 | No overview of kitchen capacity | Capacity is checked by "gut feeling". The orders data shows 19 days over capacity (see 2.4). | `asis_order_process.md`, `orders_2024_2025_export.xlsx` |
| P6 | No customer database | Customer details exist only in e-mail threads. | `current_IT_landscape.txt` |

---

## 2. Orders data (`orders_2024_2025_export.xlsx`)

### 2.1 Overview
- **Rows:** 820 rows, 256 distinct customers.
- **Event dates:** 2024-01-01 to 2025-12-28.
- **Revenue (raw totals):** ≈ 10 341 000 NOK in 2024 and ≈ 12 428 000 NOK in 2025.

### 2.2 Customer mix

| Customer type | Orders | Avg. guests | Revenue (NOK) | Median lead time (days) |
|---|---|---|---|---|
| Corporate | 406 | 52 | ≈ 7 799 000 | 16 |
| Private | 258 | 66 | ≈ 5 619 000 | 17 |
| Wedding | 86 | 105 | ≈ 7 971 000 | 196 |
| Confirmation | 62 | 50 | ≈ 1 208 000 | 18 |
| (missing) | 8 | – | – | – |

Weddings are few but bring about as much revenue as corporate orders, and they are booked about six months ahead.

### 2.3 Channels and response time
- **Channels:** e-mail ≈ 50 %, phone ≈ 29 %, website form ≈ 15 %, walk-in ≈ 6 %.
- **Median reply time:** ≈ 22 hours overall. In normal months it is 15–17 hours; in the peak months (May, June, November, December) it rises to 26–30 hours.
- **Slow replies:** ≈ 12 % of inquiries waited more than 48 hours.

### 2.4 Capacity
The kitchen can serve about 400 covers a day, or about 250 when a served wedding dinner is on the same day (`orders_2024_2025_export.xlsx`, README sheet; `interview_Sunniva_event_coordinator.txt`).

After cleaning (duplicates, invalid rows and cancellations removed):
- **Days over capacity:** 19. Twelve were in November or December and seven were wedding days in May or June.
- **Worst day:** 934 covers on 2025-12-26.

### 2.5 Dietary needs
- **Share of orders:** 71 % have a dietary note.
- **Notes recorded:** vegan, halal, shellfish allergy, vegetarian, nut allergy, gluten-free and lactose-free, fairly evenly spread (77–96 orders each).
- **Format:** notes are already recorded per group, for example "vegan x4".

### 2.6 Data-quality issues (input for validation rules and the seed script)

| Issue | Count |
|---|---|
| Fully duplicated rows (same `order_id`) | 5 |
| Missing `customer_type` | 8 |
| Negative guest numbers | 3 |
| Unrealistic guest number (5000) | 1 |
| Price per guest = 0 NOK | 2 |
| Total ≠ guests × price per guest | 12 |
| Event date before order date | 4 |
| Badly formatted postcode ("5 011") | 1 |
| Misspelt status "Confimed" | 3 |
| Inconsistent channel values (Email/EMAIL/e-mail/E-post/Phone call …) | 10 variants |

---

## 3. Stakeholder needs

### Ingrid Solheim – owner, product owner (`interview_Ingrid_owner.txt`)
- Customers can see menus and prices and send booking requests at any time.
- Kitchen order overview.
- 30 % deposit at booking ("no deposit, no booking").
- Vipps for private customers, invoices for companies, keep Fiken.
- Menus show where the food comes from (farm or boat).

### Sunniva Berg – event coordinator (`interview_Sunniva_event_coordinator.txt`)
- Calendar showing guests already booked per day, to prevent overbooking (400/250 covers).
- Automatic reminder to customers about final guest numbers 7 days before the event.
- Allergies and diets per guest group on every order, with kitchen confirmation that they have been seen.
- No deposit for corporate customers. Monthly EHF invoice instead, deposit for weddings.

### Mateo Rinaldi – head chef (`interview_Mateo_head_chef.txt`)
- Wall tablet with PIN login.
- Daily view of orders, portions per dish, with allergies in red.
- Edits seasonal menus himself (4 times a year).
- Ingredients linked to suppliers, so origin can be shown.
- Prep list: total kilos per ingredient for the next 3 days.
- Today's orders still visible when the internet is down.
- Fast pages.

### Henrik Aas – Fjordtek AS, corporate customer (`interview_Fjordtek_customer.txt`)
- Company login with several users, standing orders and copying last week's order.
- Changes to guest numbers allowed until 10:00 the day before.
- Approval by one person for orders above 15 000 NOK.
- One monthly EHF invoice with a cost-centre code on each line. No prepayment.
- Data stored in the EU/EEA, and employees' names deleted when the company stops being a customer.

### Additional needs from customer e-mails (`customer_emails_export.csv`)

| Need | E-mail |
|---|---|
| See available dates online | E001 |
| Confirm allergy info has reached the kitchen | E002 |
| Change guest numbers easily | E003 |
| EHF invoice with PO number | E004 |
| Wedding capacity and deposit information | E005 |
| Standing (recurring) orders | E007 |
| Food origin | E008 |
| Vipps payment and e-mail receipt | E009 |
| Delete personal data (GDPR) | E010 |
| Order confirmation and status | E011 |
| Menu in English with allergens | E012 |
| Cancellation terms | E013 |
| Pick-up instead of delivery | E014 |
| Quote or price list as PDF | E015 |
| Several users, one monthly invoice | E016 |
| Correct delivery contents | E017 |
| Exact delivery time window | E018 |
| Clear gluten-free labels | E019 |
| Discount for large groups | E020 |
| Local-ingredient / CO₂ data per order (ESG) | E021 |
| Late allergy changes | E022 |
| Website form errors | E023 |
| Phone ordering for non-digital customers | E024 |
| Supplier contact (out of scope) | E025 |
| Children's menu | E027 |
| Re-order a previous order | E028 |
| Read-only access for the customer's accountant | E029 |
| Correct payment reminders | E030 |

---

## 4. Constraints

| Constraint | Source |
|---|---|
| Budget 450 000 NOK incl. 12 months of hosting | `budget and constraints.txt`, `interview_Ingrid_owner.txt` |
| Running cost < 3 000 NOK/month | `budget and constraints.txt`, `current_IT_landscape.txt` |
| Go-live 2027-03-01 (hard); wedding season from May 2027 | `budget and constraints.txt`, `notes meeting 12 aug FINAL.txt` |
| 3 student developers, 2-week sprints; PO available Tuesdays 09–10 | `budget and constraints.txt`, `notes meeting 12 aug FINAL.txt` |
| Integrate with Fiken (REST API, EHF) and Vipps; Google Workspace in use | `current_IT_landscape.txt`, `notes meeting 12 aug FINAL.txt` |
| Data in EU/EEA; Norwegian and English UI; nobody technical in-house | `current_IT_landscape.txt` |
| Allergy data is health data (GDPR art. 9): store per guest group | `GDPR note from consultant.txt` |
| Keep bookkeeping data 5 years; shorter retention for other personal data | `GDPR note from consultant.txt` |
| Customers can request access and deletion | `GDPR note from consultant.txt` |
| Data processing agreement with any cloud/SaaS provider | `GDPR note from consultant.txt` |
| MVC with Flask, Neo4j storage, synthetic seed data, secrets in `.env` | `CLAUDE.md` |

---

## 5. Conflicts and open questions

| # | Topic | Conflict | Sources | Suggested next step |
|---|---|---|---|---|
| C1 | Deposit | Ingrid wants a 30 % deposit on all bookings. Sunniva and Fjordtek say corporate customers cannot prepay. | `interview_Ingrid_owner.txt`, `interview_Sunniva_event_coordinator.txt`, `interview_Fjordtek_customer.txt` | Propose: deposit for weddings and private events, monthly EHF invoice for corporate customers. Decide with Ingrid at the Tuesday meeting. |
| C2 | Payment scope | Course scope says "No payment solution is needed", but stakeholders require Vipps and Fiken. | `CLAUDE.md`, `notes meeting 12 aug FINAL.txt` | Keep payment status in the system now; plan the Vipps and Fiken integration as a later release. |
| C3 | Build or buy | Own system or configure an off-the-shelf catering SaaS is still open. | `notes meeting 12 aug FINAL.txt` | Benchmark against the competitors (`competitor links.txt`) and the budget. |
| C4 | Data storage location | Neo4j hosting must meet the EU/EEA and data processing agreement requirements. | `CLAUDE.md`, `GDPR note from consultant.txt` | Choose an EU-hosted option. |

---

## 6. File inventory

| File | Content | Value for requirements |
|---|---|---|
| `interview_Ingrid_owner.txt` | Owner interview, 2026-08-14 | High |
| `interview_Sunniva_event_coordinator.txt` | Coordinator interview, 2026-08-15 | High |
| `Kopi av interview Sunniva (2).txt` | Exact duplicate of the file above | None (duplicate) |
| `interview_Mateo_head_chef.txt` | Chef interview, 2026-08-15 | High |
| `interview_Fjordtek_customer.txt` | Corporate customer interview, 2026-08-19 | High |
| `asis_order_process.md` | As-is process in 12 steps | High |
| `customer_emails_export.csv` | Customer e-mails, 2026-05 to 2026-08 | High |
| `orders_2024_2025_export.xlsx` | 820 historical orders + README | High |
| `GDPR note from consultant.txt` | Data-protection advice, 2026-08-20 | High |
| `current_IT_landscape.txt` | Current systems and constraints | High |
| `budget and constraints.txt` | Budget, deadline, team | High |
| `notes meeting 12 aug FINAL.txt` | Kick-off meeting, 2026-08-12 | Medium |
| `vision_draft_v0.3.docx` | Draft vision statement | Medium |
| `lunch menu autumn.txt` | 4 dishes with prices and allergens | Medium (seed data) |
| `competitor links.txt` | 4 competitor websites | Low (benchmarking) |
| `untitled.txt` | Sprint 0 tasks + personal note | Low |
| `logo ideas.txt` | Logo brainstorm | None |
