from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from .forms import (
    BulkPriceForm,
    MenuItemForm,
    MenuTagForm,
    MosaicPhotoForm,
    PanelLoginForm,
    PromotionForm,
    SiteImageForm,
    SiteSettingsForm,
)
from .models import Booking, Category, MenuItem, MenuTag, MosaicPhoto, Promotion, SiteImage, SiteSettings


def staff_required(view):
    return user_passes_test(lambda u: u.is_active and u.is_staff)(view)


def panel_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('panel_dashboard')

    if request.method == 'POST':
        form = PanelLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('panel_dashboard')
            messages.error(request, 'Неверный логин или пароль.')
    else:
        form = PanelLoginForm()

    return render(request, 'panel/login.html', {'form': form})


@login_required(login_url='panel_login')
@staff_required
def panel_logout(request):
    logout(request)
    return redirect('panel_login')


@login_required(login_url='panel_login')
@staff_required
def panel_dashboard(request):
    items = MenuItem.objects.prefetch_related('promotions')
    on_sale = [i for i in items if i.has_discount]
    unavailable = items.filter(is_available=False).count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    avg_price = items.aggregate(avg=Avg('price'))['avg']
    menu_count = items.count()

    return render(request, 'panel/dashboard.html', {
        'menu_count': menu_count,
        'promo_count': Promotion.objects.filter(is_active=True).count(),
        'tag_count': MenuTag.objects.count(),
        'unavailable_count': unavailable,
        'pending_bookings': pending_bookings,
        'on_sale': on_sale[:6],
        'avg_price': avg_price,
        'recent_bookings': Booking.objects.order_by('-created_at')[:5],
        'popular_items': items.filter(is_popular=True)[:4],
    })


@login_required(login_url='panel_login')
@staff_required
def panel_menu_list(request):
    items = MenuItem.objects.select_related('category').prefetch_related('tags', 'promotions')
    return render(request, 'panel/menu_list.html', {'items': items})


@login_required(login_url='panel_login')
@staff_required
@require_POST
def panel_menu_toggle(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    field = request.POST.get('field')
    if field in ('is_available', 'is_popular'):
        setattr(item, field, not getattr(item, field))
        item.save()
        label = 'в наличии' if field == 'is_available' else 'хит'
        state = 'включено' if getattr(item, field) else 'выключено'
        messages.success(request, f'«{item.name}»: {label} {state}.')
    return redirect('panel_menu_list')


@login_required(login_url='panel_login')
@staff_required
def panel_menu_edit(request, pk=None):
    item = get_object_or_404(MenuItem, pk=pk) if pk else None

    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if request.POST.get('delete') and item:
            item.delete()
            messages.success(request, 'Позиция удалена.')
            return redirect('panel_menu_list')
        if form.is_valid():
            form.save()
            messages.success(request, 'Сохранено.')
            return redirect('panel_menu_list')
    else:
        form = MenuItemForm(instance=item)

    return render(request, 'panel/menu_edit.html', {
        'form': form,
        'item': item,
    })


@login_required(login_url='panel_login')
@staff_required
def panel_promotions(request):
    promos = Promotion.objects.prefetch_related('menu_items')
    return render(request, 'panel/promotions_list.html', {'promos': promos})


@login_required(login_url='panel_login')
@staff_required
def panel_promotion_edit(request, pk=None):
    promo = get_object_or_404(Promotion, pk=pk) if pk else None

    if request.method == 'POST':
        form = PromotionForm(request.POST, request.FILES, instance=promo)
        if request.POST.get('delete') and promo:
            promo.delete()
            messages.success(request, 'Акция удалена.')
            return redirect('panel_promotions')
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            form.save_m2m()
            messages.success(request, 'Акция сохранена.')
            return redirect('panel_promotions')
    else:
        form = PromotionForm(instance=promo)

    return render(request, 'panel/promotion_edit.html', {'form': form, 'promo': promo})


@login_required(login_url='panel_login')
@staff_required
def panel_images(request):
    site_images = {img.key: img for img in SiteImage.objects.all()}

    if request.method == 'POST':
        key = request.POST.get('site_key')
        if key:
            obj = SiteImage.objects.filter(key=key).first()
            if obj is None and not request.FILES.get('image'):
                messages.error(request, 'Выберите файл изображения.')
            else:
                if obj is None:
                    obj = SiteImage(key=key)
                form = SiteImageForm(request.POST, request.FILES, instance=obj)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Изображение обновлено.')
                    return redirect('panel_images')

        slot = request.POST.get('mosaic_slot')
        if slot:
            obj = MosaicPhoto.objects.filter(slot=int(slot)).first()
            if obj is None and not request.FILES.get('image'):
                messages.error(request, f'Ячейка {slot}: выберите файл.')
            else:
                if obj is None:
                    obj = MosaicPhoto(slot=int(slot))
                form = MosaicPhotoForm(request.POST, request.FILES, instance=obj)
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Коллаж — ячейка {slot} обновлена.')
                    return redirect('panel_images')

    return render(request, 'panel/images.html', {
        'hero': site_images.get('hero'),
        'about': site_images.get('about'),
        'mosaic': MosaicPhoto.objects.order_by('slot'),
    })


@login_required(login_url='panel_login')
@staff_required
def panel_settings(request):
    settings_obj = SiteSettings.get_solo()
    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Настройки сайта сохранены.')
            return redirect('panel_settings')
    else:
        form = SiteSettingsForm(instance=settings_obj)
    return render(request, 'panel/settings.html', {'form': form})


@login_required(login_url='panel_login')
@staff_required
def panel_tags(request):
    if request.method == 'POST':
        if request.POST.get('delete'):
            tag = get_object_or_404(MenuTag, pk=request.POST.get('delete'))
            name = tag.name
            tag.delete()
            messages.success(request, f'Тег «{name}» удалён.')
            return redirect('panel_tags')
        form = MenuTagForm(request.POST)
        if form.is_valid():
            tag = form.save(commit=False)
            base_slug = slugify(tag.name, allow_unicode=True) or 'tag'
            slug = base_slug
            n = 1
            while MenuTag.objects.filter(slug=slug).exclude(pk=tag.pk).exists():
                slug = f'{base_slug}-{n}'
                n += 1
            tag.slug = slug
            tag.save()
            messages.success(request, f'Тег «{tag.name}» добавлен.')
            return redirect('panel_tags')
    else:
        form = MenuTagForm()

    tags = MenuTag.objects.annotate(item_count=Count('items')).order_by('name')
    return render(request, 'panel/tags.html', {'form': form, 'tags': tags})


@login_required(login_url='panel_login')
@staff_required
def panel_bulk_prices(request):
    if request.method == 'POST':
        form = BulkPriceForm(request.POST)
        if form.is_valid():
            qs = MenuItem.objects.all()
            category = form.cleaned_data['category']
            if category:
                qs = qs.filter(category=category)
            percent = form.cleaned_data['percent']
            if form.cleaned_data['action'] == 'increase':
                factor = Decimal('1') + percent / Decimal('100')
            else:
                factor = Decimal('1') - percent / Decimal('100')
            updated = 0
            for item in qs:
                item.price = (item.price * factor).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
                if item.sale_price is not None:
                    item.sale_price = (
                        item.sale_price * factor
                    ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
                item.save(update_fields=['price', 'sale_price'])
                updated += 1
            messages.success(request, f'Цены обновлены у {updated} позиций.')
            return redirect('panel_bulk_prices')
    else:
        form = BulkPriceForm()

    return render(request, 'panel/bulk_prices.html', {'form': form})


@login_required(login_url='panel_login')
@staff_required
def panel_bookings(request):
    status_filter = request.GET.get('status', '')
    bookings = Booking.objects.order_by('-date', '-time')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    if request.method == 'POST':
        booking = get_object_or_404(Booking, pk=request.POST.get('booking_id'))
        new_status = request.POST.get('status')
        valid = dict(Booking.STATUS_CHOICES)
        if new_status in valid:
            booking.status = new_status
            booking.save(update_fields=['status'])
            messages.success(request, f'Запись {booking.name}: {valid[new_status]}.')
        return redirect('panel_bookings')

    return render(request, 'panel/bookings.html', {
        'bookings': bookings[:50],
        'status_filter': status_filter,
        'status_choices': Booking.STATUS_CHOICES,
        'pending_count': Booking.objects.filter(status='pending').count(),
    })
