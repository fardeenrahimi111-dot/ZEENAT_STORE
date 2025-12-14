# EXPECTED DEFENSE QUESTIONS

## TECHNICAL QUESTIONS:
1. Q: Why Django and not other frameworks?
   A: Django provides built-in admin, ORM, authentication, and security features that accelerated development.

2. Q: How does your stock management prevent overselling?
   A: The system checks stock before completing sales and shows real-time inventory levels.

3. Q: How do you handle concurrent sales?
   A: Django's database transactions ensure data integrity, though for high traffic we'd implement row locking.

## BUSINESS LOGIC QUESTIONS:
1. Q: How do you calculate low stock alerts?
   A: Products below 10 units trigger alerts, with visual indicators and automated restock suggestions.

2. Q: Can you explain the pricing logic?
   A: Base price with optional percentage discounts, automatically calculated in the model.

## SECURITY QUESTIONS:
1. Q: What security measures did you implement?
   A: CSRF protection, SQL injection prevention via ORM, password hashing, role-based permissions.

2. Q: How do you prevent unauthorized access?
   A: Login required for all pages, with role-based permissions (Admin, Manager, Cashier).

## SCALABILITY QUESTIONS:
1. Q: How would you scale this for multiple stores?
   A: Add store_id foreign key, implement API for central management, add caching for performance.

2. Q: What about performance with large inventories?
   A: Optimized queries with select_related and prefetch_related, pagination for lists.