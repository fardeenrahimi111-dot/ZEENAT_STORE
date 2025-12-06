from django import forms
from core.models import Product, Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "size",
            "color",
            "price",
            "quantity",
            "barcode",
            "discount_percent",
        ]


class SaleAddItemForm(forms.Form):
    barcode = forms.CharField(
        max_length=50,
        required=False,
        label="Barcode",
        widget=forms.TextInput(attrs={"placeholder": "Scan or enter barcode"}),
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        label="Product",
    )
    quantity = forms.IntegerField(min_value=1, initial=1)

