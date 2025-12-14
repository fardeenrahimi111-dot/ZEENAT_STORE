from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    # Extra field for adding a new category (not in Product model)
    new_category = forms.CharField(
        required=False,
        label="New Category",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
  
 # ✅ ADD THESE VALIDATION METHODS:
    def clean_price(self):
        """Ensure price is positive"""
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be greater than 0.00")
        return price
    
    def clean_quantity(self):
        """Ensure quantity is not negative"""
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 0:
            raise forms.ValidationError("Quantity cannot be negative")
        return quantity
    
    def clean_discount_percent(self):
        """Ensure discount is between 0 and 100"""
        discount = self.cleaned_data.get('discount_percent')
        if discount is not None:
            if discount < 0:
                raise forms.ValidationError("Discount cannot be negative")
            if discount > 100:
                raise forms.ValidationError("Discount cannot exceed 100%")
        return discount
    
    class Meta:
        model = Product
        fields = [
            "name", "category", "size", "color",
            "price", "quantity", "barcode", "discount_percent"
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "size": forms.TextInput(attrs={"class": "form-control"}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "barcode": forms.TextInput(attrs={"class": "form-control"}),
            "discount_percent": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        # Handle new category creation if provided
        new_category = self.cleaned_data.get("new_category")
        if new_category:
            category, created = Category.objects.get_or_create(name=new_category)
            self.instance.category = category
        return super().save(commit)


class SaleAddItemForm(forms.Form):
    barcode = forms.CharField(
        max_length=50,
        required=False,
        label="Barcode",
        widget=forms.TextInput(attrs={
            "placeholder": "Scan or enter barcode",
            "class": "form-control"
        })
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        label="Product",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    quantity = forms.IntegerField(
        min_value=1, 
        initial=1,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "min": "1"
        })
    )

    # ✅ ADD THIS CLEAN METHOD (after fields, before closing class):
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        barcode = cleaned_data.get('barcode')
        
        # If barcode is provided, find product
        if barcode and not product:
            try:
                product = Product.objects.get(barcode=barcode)
                cleaned_data['product'] = product
            except Product.DoesNotExist:
                self.add_error('barcode', 'No product found with this barcode')
        
        # Check if product is selected
        if not product:
            self.add_error('product', 'Please select a product or scan barcode')
        
        # Check stock availability
        if product and quantity:
            if quantity > product.quantity:
                self.add_error('quantity', 
                    f'Only {product.quantity} units available in stock')
        
        return cleaned_data
    
    # ✅ ADD THIS METHOD TOO:
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1")
        return quantity
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 0:
            raise forms.ValidationError("Quantity cannot be negative")
        return quantity
    

    def clean_discount_percent(self):
        """Ensure discount is between 0 and 100"""
        discount = self.cleaned_data.get('discount_percent')
        if discount is not None:
            if discount < 0:
                raise forms.ValidationError("Discount cannot be negative")
            if discount > 100:
                raise forms.ValidationError("Discount cannot exceed 100%")
        return discount