from decimal import Decimal

from django import forms

from .models import Booking, Category, MenuItem, MenuTag, MosaicPhoto, Promotion, SiteImage, SiteSettings


class PanelLoginForm(forms.Form):
    username = forms.CharField(label='Логин', max_length=150)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            'site_name', 'topbar_text', 'phone',
            'address_name', 'address_street',
            'hours_weekday', 'hours_weekend',
            'footer_tagline', 'hero_tagline',
            'hero_title_line1', 'hero_title_line2',
        ]
        widgets = {
            'topbar_text': forms.TextInput(attrs={'size': 60}),
        }


class MenuTagForm(forms.ModelForm):
    class Meta:
        model = MenuTag
        fields = ['name']


class BulkPriceForm(forms.Form):
    ACTION_CHOICES = [
        ('increase', 'Поднять'),
        ('decrease', 'Снизить'),
    ]
    percent = forms.DecimalField(
        label='На сколько %',
        min_value=Decimal('0.01'),
        max_value=Decimal('100'),
        decimal_places=2,
        initial=Decimal('10'),
    )
    action = forms.ChoiceField(label='Действие', choices=ACTION_CHOICES, initial='increase')
    category = forms.ModelChoiceField(
        label='Категория',
        queryset=Category.objects.none(),
        required=False,
        empty_label='Все позиции',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()


class BookingStatusForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['status']


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = [
            'category', 'name', 'description', 'price', 'sale_price',
            'image', 'order', 'is_popular', 'is_available', 'tags',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'tags': forms.CheckboxSelectMultiple,
        }


class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = [
            'title', 'text', 'image', 'discount_percent',
            'menu_items', 'order', 'is_active',
        ]
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
            'menu_items': forms.CheckboxSelectMultiple,
        }


class SiteImageForm(forms.ModelForm):
    class Meta:
        model = SiteImage
        fields = ['image', 'alt_text']


class MosaicPhotoForm(forms.ModelForm):
    class Meta:
        model = MosaicPhoto
        fields = ['image', 'alt_text', 'aspect_ratio', 'is_active']
