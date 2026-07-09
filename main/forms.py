from decimal import Decimal

from django import forms
from django.forms import inlineformset_factory

from .models import Category, MenuItem, MenuItemVariant, MenuTag, MosaicPhoto, Promotion, SiteImage, SiteSettings


class PanelLoginForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Логин', 'autocomplete': 'username'}),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Пароль', 'autocomplete': 'current-password', 'autofocus': 'autofocus'}
        ),
    )


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


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Например: Выпечка'}),
            'order': forms.NumberInput(attrs={'min': 0, 'step': 1}),
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


class MenuItemForm(forms.ModelForm):
    PRICING_SINGLE = 'single'
    PRICING_VOLUMES = 'volumes'
    PRICING_MODE_CHOICES = [
        (PRICING_SINGLE, 'Одна цена — десерт, выпечка, блюдо'),
        (PRICING_VOLUMES, 'По объёмам — напиток в разных размерах'),
    ]

    pricing_mode = forms.ChoiceField(
        label='Тип цены',
        choices=PRICING_MODE_CHOICES,
        widget=forms.RadioSelect,
        initial=PRICING_SINGLE,
    )

    class Meta:
        model = MenuItem
        fields = [
            'category', 'name', 'description', 'price', 'sale_price',
            'image', 'order', 'is_popular', 'is_available', 'tags',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'tags': forms.CheckboxSelectMultiple,
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
            'price': forms.NumberInput(attrs={'min': 0, 'step': 1, 'placeholder': '350'}),
            'sale_price': forms.NumberInput(attrs={'min': 0, 'step': 1, 'placeholder': 'Необязательно'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price'].required = False
        self.fields['sale_price'].required = False
        self.fields['image'].required = False
        self.fields['price'].help_text = 'Одна фиксированная цена для всей позиции.'
        self.fields['sale_price'].help_text = 'Необязательно. Показывается вместо обычной цены.'
        self.fields['image'].help_text = 'Необязательно. Позиции без фото показываются в меню отдельным списком.'
        if self.instance and self.instance.pk and self.instance.has_variants:
            self.fields['pricing_mode'].initial = self.PRICING_VOLUMES

    def clean(self):
        cleaned = super().clean()
        mode = cleaned.get('pricing_mode', self.PRICING_SINGLE)
        if mode == self.PRICING_VOLUMES:
            cleaned['price'] = None
            cleaned['sale_price'] = None
        elif cleaned.get('price') in (None, ''):
            self.add_error('price', 'Укажите цену или выберите «По объёмам».')
        return cleaned


class MenuItemVariantForm(forms.ModelForm):
    class Meta:
        model = MenuItemVariant
        fields = ['volume_ml', 'price', 'sale_price', 'order']
        widgets = {
            'volume_ml': forms.NumberInput(attrs={'min': 1, 'step': 1, 'placeholder': '250'}),
            'price': forms.NumberInput(attrs={'min': 0, 'step': 1, 'placeholder': '290'}),
            'order': forms.NumberInput(attrs={'min': 0, 'step': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['volume_ml'].required = False
        self.fields['price'].required = False

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('DELETE'):
            return cleaned
        volume = cleaned.get('volume_ml')
        price = cleaned.get('price')
        if not volume and price in (None, '') and not self.instance.pk:
            return cleaned
        if not volume:
            self.add_error('volume_ml', 'Укажите объём в мл')
        if price in (None, ''):
            self.add_error('price', 'Укажите цену')
        return cleaned


class _MenuItemVariantFormSetBase(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                continue
            if not form.cleaned_data.get('volume_ml') and form.cleaned_data.get('price') in (None, ''):
                continue
            if not form.cleaned_data.get('volume_ml') or form.cleaned_data.get('price') in (None, ''):
                raise forms.ValidationError('В каждой строке объёма укажите мл и цену.')


MenuItemVariantFormSet = inlineformset_factory(
    MenuItem,
    MenuItemVariant,
    form=MenuItemVariantForm,
    formset=_MenuItemVariantFormSetBase,
    extra=0,
    can_delete=True,
    min_num=0,
    validate_min=False,
)


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
