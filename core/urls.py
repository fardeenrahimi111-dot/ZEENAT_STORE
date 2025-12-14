from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    # Product management
    path("products/", views.product_list, name="product_list"),
    path("products/add/", views.product_create, name="product_create"),
    path("products/<int:pk>/edit/", views.product_update, name="product_update"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),

    # Sales
    path("sales/new/", views.sale_create, name="sale_create"),
    path("sales/", views.sale_list, name="sale_list"),
    path("sales/<int:sale_id>/", views.sale_detail, name="sale_detail"),
    path("sales/<int:sale_id>/invoice/", views.sale_invoice_pdf, name="sale_invoice_pdf"),

    # Reports
    path("reports/inventory/", views.inventory_report, name="inventory_report"),
    path(
        "reports/inventory/export/excel/",
        views.inventory_report_excel,
        name="inventory_report_excel",
    ),
    path("reports/sales/", views.sales_report, name="sales_report"),
    path(
        "reports/sales/export/excel/",
        views.sales_report_excel,
        name="sales_report_excel",
    ),
    path("reports/low-stock/", views.low_stock_report, name="low_stock_report"),
]
