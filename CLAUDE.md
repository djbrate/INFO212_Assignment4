Context: Ekte Mat AS is a small Bergen catering company that offers authentic, seasonal food for:
 - corporate lunches 
 - private parties
 - confirmations
 - weddings.
 - conferences
 - christmas parties
 - birthdays
 - other events

  Today every order arrives by e-mail or phone, is copied into an Excel sheet and printed for the kitchen. 
  this creates the following problems
  - Inquiries get lost
  - answers are slow in peak season
  - allergy information goes missing
  - invoicing is manual
 
   The owner, Ingrid Solheim, has hired your student team to specify and design Ekte Mat Online: a web-based ordering and event-booking system with a kitchen view, integrated with the accounting system Fiken and the payment service Vipps. The team works in twoweek sprints; Ingrid is the product owner.


The Code we will be working on now has two main parts: the "Admin panel" and "Customer Site". It should also be possible to use the "go live" extension, so there should be a index.html.

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



WHY: 
Admin panel: The purpose of the admin panel, is to give the "Ekte Mat" Staff the ability to easily make simple editing changes, modifications, overview of orders and interact with customers. 
Customer Site: Customer can easily choose their option and later acces it.
Overall: 


HOW: 
The techinal requirements for this project include:
- Architecture: Model–View–Controller, with Flask as the backend. 
    Models hold the domain classes and all data access 
    Views are Jinja2 templates or a separate front end that calls a JSON API
    controllers are Flask routes grouped in blueprints (e.g. shop, account, admin).
  The three layers must be visible in your folder structure.

- Front end: HTML, CSS and JavaScript if needed. The interface should be easy to navigate and consintent between admin and customer, and appropirate.

- Data storage: 
    Neo4j is the storage layer of the finished system and should represent relationships between Customers, Staff, Food items, Event catagories, Orders, Order items, Quenstions and answers. Use appropriate realtionships between nodes. All database acces should be organzied within the model/data-access layer. 

- Security basics: Only customer login pages are fine. While coming code on github – make sure that your project does not include Claude API key. Keep API keys in .env, Add .env to .gitignore and never commit secrets. 
- Running it: synthetic data only. A seed script creates sample food items, an admin and test customers, and the README gives the commands to install, seed, run and test the application.
