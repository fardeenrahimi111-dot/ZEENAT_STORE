# ZEENAT STORE - DEFENSE DEMONSTRATION SCRIPT

## 1. INTRODUCTION (2 minutes)
- Open application: http://127.0.0.1:8000/
- Show login page with demo credentials
- Explain the system purpose: Clothing store inventory management

## 2. ADMINISTRATOR DEMO (5 minutes)
- Login as Admin (admin/admin123)
- Show dashboard with all statistics
- Demonstrate adding a new product
- Show product validation (negative price/quantity)
- Create a sale with multiple items
- Show stock reduction after sale
- Generate and print invoice

## 3. ROLE-BASED ACCESS DEMO (3 minutes)
- Logout and login as Cashier (cashier/cashier123)
- Show Cashier can create sales but not edit products
- Show permission denied when trying to access reports
- Login as Manager (manager/manager123)
- Show Manager can edit products but not delete

## 4. REPORTS & ANALYTICS (3 minutes)
- Show inventory report with export to Excel
- Show sales report with date filtering
- Demonstrate low stock alerts
- Show restock suggestion modal

## 5. TECHNICAL FEATURES (2 minutes)
- Run tests: python manage.py test core.final_tests
- Show test results (13 passing tests)
- Demonstrate error pages (404, 500)
- Show responsive design on mobile

## 6. Q&A PREPARATION
- Be ready to explain database schema
- Discuss security measures (CSRF, authentication)
- Explain business logic (stock management, pricing)
- Show code organization and structure