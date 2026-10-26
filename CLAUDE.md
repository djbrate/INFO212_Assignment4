This project is built on a previous working Flask Application.

Context to the case: Ekte Mat AS is a small Bergen catering company that offers authentic, seasonal food for corporate lunches, private parties, confirmations and weddings. Today every order arrives by e-mail or phone, is copied into an Excel sheet and printed for the kitchen. Inquiries get lost, answers are slow in peak season, allergy information goes missing and invoicing is manual. The owner, Ingrid Solheim, has hired your student team to specify and design Ekte Mat Online: a web-based ordering and event-booking system with a kitchen view, integrated with the accounting system Fiken and the payment service Vipps. The team works in twoweek sprints; Ingrid is the product owner. You have just received a messy folder of project material from her.



The Code we will be working on now has two main parts: the "Admin panel" and "Customer Site".

WHAT: 
Admin panel (Ekte Mat staff): This consists of 4 main mechanics that should be available for "Ekte Mat" Staff to use. 
1. Food items. Add, edit and remove the food Ekte Mat caters: name, description, price in NOK, minimum order quantity, event categories, allergens and dietary labels, and whether the item is published.
2. Images. Upload a picture for each item, or write an instruction that an AI agent or image service uses to create or modify the picture. The admin previews the result before it is saved.
3. Orders. A list of all customer orders that can be filtered by status and event date, and a page per order to manage it: order status (submitted → approved → in preparation → delivered, or rejected/cancelled) and payment status (e.g. not paid, deposit paid, invoiced, paid).
4. Questions. Read and answer customers’ questions about their orders.

Customer Site (the published shop): 
1. Menu by event. Food items as cards, grouped by kind of event: birthday, confirmation, wedding, conference, Christmas party (julebord) and so on. Each card shows picture, price, minimum order and allergens.
2. Shopping cart. Add, change and remove items, with an estimated total cost. Quantities below an item’s minimum order are not accepted.
3. Order. Log in (or register) and submit the order: event date, number of guests, delivery address, and allergy and dietary notes per guest group. No payment solution is needed.
4. My orders. The customer’s own orders with their current status (submitted, approved, delivered, …) and payment status.
5. Questions. Ask a question about a specific order and read Ekte Mat’s answer.

Overall: 



WHY: 
Admin panel: The purpose of the admin panel, is to give the "Ekte Mat" Staff the ability to easily make simple editing changes, modifications, overview of orders and interact with customers. 
Customer Site: 
Overall: 


HOW: 
The techinal requirements for this project include:
- Architecture: Model–View–Controller, with Flask as the backend. Models hold the domain classes and all data access, views are Jinja2 templates or a separate front end that calls a JSON API, and controllers are Flask routes grouped in blueprints (e.g. shop, account, admin). The three layers must be visible in your folder structure.
- Front end: HTML, CSS and JavaScript if needed.
- Data storage: Neo4j is the storage layer of the finished system (see the box below). For this assignment a temporary store such as SQLite or JSON files is fine, as long as only repository classes in the model layer touch it, so that Neo4j can later replace it without changes to controllers or views.
- Security basics: Only customer login pages are fine.
- Running it: synthetic data only. A seed script creates sample food items, an admin and test customers, and the README gives the commands to install, seed, run and test the application.


NOTATER:
Front end languages: HTML, CSS, maybe Javascript
Data Storage: JSON
The Code follows MVC
