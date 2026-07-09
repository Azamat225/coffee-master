from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Avg, Count, Max
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from .forms import (
    BulkPriceForm,
    CategoryForm,
    MenuItemForm,
    MenuItemVariantFormSet,
    MenuTagForm,
    MosaicPhotoForm,
    PanelLoginForm,
    PromotionForm,
    SiteImageForm,
    SiteSettingsForm,
)
from .models import (
    BulkPriceAdjustment,
    BulkPriceSnapshot,
    Category,
    GallerySlide,
    MenuItem,
    MenuItemVariant,
    MenuTag,
    MosaicPhoto,
    Promotion,
    SiteImage,
    SiteSettings,
)


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
    avg_price = items.aggregate(avg=Avg('price'))['avg']
    menu_count = items.count()

    return render(request, 'panel/dashboard.html', {
        'menu_count': menu_count,
        'promo_count': Promotion.objects.filter(is_active=True).count(),
        'tag_count': MenuTag.objects.count(),
        'unavailable_count': unavailable,
        'on_sale': on_sale[:6],
        'avg_price': avg_price,
        'popular_items': items.filter(is_popular=True)[:4],
    })


@login_required(login_url='panel_login')
@staff_required
def panel_menu_list(request):
    items = (
        MenuItem.objects.select_related('category')
        .prefetch_related('tags', 'promotions', 'variants')
    )
    categories = Category.objects.annotate(item_count=Count('items')).order_by('order', 'name')
    category_slug = request.GET.get('category', '').strip()
    current_category = None
    if category_slug:
        current_category = Category.objects.filter(slug=category_slug).first()
        if current_category:
            items = items.filter(category=current_category)

    return render(request, 'panel/menu_list.html', {
        'items': items,
        'categories': categories,
        'current_category': current_category,
    })


def _save_menu_item_with_variants(request, item=None):
    form = MenuItemForm(request.POST, request.FILES, instance=item)
    pricing_mode = request.POST.get('pricing_mode', MenuItemForm.PRICING_SINGLE)
    use_volumes = pricing_mode == MenuItemForm.PRICING_VOLUMES

    if not form.is_valid():
        formset = MenuItemVariantFormSet(request.POST, instance=item) if use_volumes else MenuItemVariantFormSet(instance=item)
        return None, form, formset

    try:
        with transaction.atomic():
            saved_item = form.save(commit=False)
            saved_item.save()
            form.save_m2m()

            if use_volumes:
                formset = MenuItemVariantFormSet(request.POST, instance=saved_item)
                if not formset.is_valid():
                    raise _MenuItemSaveAbort(form, formset)

                formset.save()
                saved_item.refresh_from_db()
                if not saved_item.variants.exists():
                    form.add_error(
                        'pricing_mode',
                        'Добавьте хотя бы одну строку: объём в мл и цена.',
                    )
                    raise _MenuItemSaveAbort(form, formset)

                saved_item.sync_base_price_from_variants()
                saved_item.save(update_fields=['price'])
            else:
                saved_item.variants.all().delete()

            formset = MenuItemVariantFormSet(instance=saved_item)
    except _MenuItemSaveAbort as exc:
        return None, exc.form, exc.formset

    return saved_item, form, formset


class _MenuItemSaveAbort(Exception):
    def __init__(self, form, formset):
        self.form = form
        self.formset = formset


@login_required(login_url='panel_login')
@staff_required
def panel_menu_edit(request, pk=None):
    item = get_object_or_404(MenuItem, pk=pk) if pk else None

    if request.method == 'POST':
        if request.POST.get('delete') and item:
            item.delete()
            messages.success(request, 'Позиция удалена.')
            return redirect('panel_menu_list')

        saved_item, form, formset = _save_menu_item_with_variants(request, item)
        if saved_item:
            messages.success(request, 'Сохранено.')
            category_slug = request.GET.get('category', '').strip()
            if category_slug:
                return redirect(f"{reverse('panel_menu_list')}?category={category_slug}")
            return redirect('panel_menu_list')
        messages.error(request, 'Не удалось сохранить. Проверьте поля ниже.')
    else:
        form = MenuItemForm(instance=item)
        formset = MenuItemVariantFormSet(instance=item)

    return render(request, 'panel/menu_edit.html', {
        'form': form,
        'formset': formset,
        'item': item,
    })


@login_required(login_url='panel_login')
@staff_required
def panel_categories(request):
    categories = Category.objects.annotate(item_count=Count('items')).order_by('order', 'name')
    return render(request, 'panel/categories_list.html', {'categories': categories})


@login_required(login_url='panel_login')
@staff_required
def panel_category_edit(request, pk=None):
    category = get_object_or_404(Category, pk=pk) if pk else None

    if request.method == 'POST':
        if request.POST.get('delete') and category:
            if category.items.exists():
                messages.error(request, 'Нельзя удалить категорию с позициями меню.')
            else:
                category.delete()
                messages.success(request, 'Категория удалена.')
            return redirect('panel_categories')

        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            cat = form.save(commit=False)
            if not category:
                base_slug = slugify(cat.name, allow_unicode=True) or 'category'
                slug = base_slug
                n = 1
                while Category.objects.filter(slug=slug).exists():
                    slug = f'{base_slug}-{n}'
                    n += 1
                cat.slug = slug
            cat.save()
            messages.success(request, 'Категория сохранена.')
            return redirect('panel_categories')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'panel/category_edit.html', {
        'form': form,
        'category': category,
    })


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

        mosaic_action = request.POST.get('mosaic_action')
        if mosaic_action == 'add':
            image = request.FILES.get('image')
            if not image:
                messages.error(request, 'Выберите файл для коллажа.')
            else:
                alt_text = request.POST.get('alt_text', '').strip()
                ratio = request.POST.get('aspect_ratio') or 'auto'
                is_active = bool(request.POST.get('is_active'))
                max_order = MosaicPhoto.objects.aggregate(max_order=Max('order'))['max_order'] or 0
                MosaicPhoto.objects.create(
                    image=image,
                    alt_text=alt_text,
                    aspect_ratio=ratio,
                    order=int(max_order) + 1,
                    is_active=is_active,
                )
                messages.success(request, 'Фото добавлено в коллаж.')
                return redirect('panel_images')

        if mosaic_action == 'update':
            photo_id = request.POST.get('mosaic_id')
            if not photo_id:
                messages.error(request, 'Не указано фото коллажа.')
            else:
                obj = get_object_or_404(MosaicPhoto, pk=photo_id)
                obj.alt_text = request.POST.get('alt_text', '').strip()
                obj.aspect_ratio = request.POST.get('aspect_ratio') or 'auto'
                obj.is_active = bool(request.POST.get('is_active'))
                try:
                    obj.order = int(request.POST.get('order', obj.order))
                except (TypeError, ValueError):
                    pass
                if request.FILES.get('image'):
                    obj.image = request.FILES.get('image')
                obj.save()
                messages.success(request, 'Фото коллажа обновлено.')
                return redirect('panel_images')

        if mosaic_action == 'delete':
            photo_id = request.POST.get('mosaic_id')
            if photo_id:
                photo = MosaicPhoto.objects.filter(pk=photo_id).first()
                if photo:
                    photo.delete()
                    messages.success(request, 'Фото удалено из коллажа.')
                    return redirect('panel_images')

        gallery_action = request.POST.get('gallery_action')
        if gallery_action == 'add':
            image = request.FILES.get('image')
            if not image:
                messages.error(request, 'Выберите файл для загрузки в галерею.')
            else:
                title = request.POST.get('title', '').strip()
                ratio = request.POST.get('aspect_ratio') or 'auto'
                is_active = bool(request.POST.get('is_active'))

                max_order = GallerySlide.objects.aggregate(max_order=Max('order'))['max_order'] or 0
                GallerySlide.objects.create(
                    image=image,
                    title=title,
                    aspect_ratio=ratio,
                    order=int(max_order) + 1,
                    is_active=is_active,
                )
                messages.success(request, 'Фото добавлено в галерею.')
                return redirect('panel_images')

        if gallery_action == 'update':
            slide_id = request.POST.get('slide_id')
            if slide_id:
                slide = get_object_or_404(GallerySlide, id=slide_id)
                slide.title = request.POST.get('title', '').strip()
                slide.aspect_ratio = request.POST.get('aspect_ratio') or 'auto'
                # order обновляем только если валидное число
                try:
                    slide.order = int(request.POST.get('order', slide.order))
                except (TypeError, ValueError):
                    pass
                slide.is_active = bool(request.POST.get('is_active'))
                if request.FILES.get('image'):
                    slide.image = request.FILES.get('image')
                slide.save()
                messages.success(request, 'Фото галереи обновлено.')
                return redirect('panel_images')

        if gallery_action == 'delete':
            slide_id = request.POST.get('slide_id')
            if slide_id:
                slide = GallerySlide.objects.filter(id=slide_id).first()
                if slide:
                    slide.delete()
                    messages.success(request, 'Фото удалено из галереи.')
                    return redirect('panel_images')

    return render(request, 'panel/images.html', {
        'hero': site_images.get('hero'),
        'about': site_images.get('about'),
        'mosaic_photos': MosaicPhoto.objects.order_by('order', 'pk'),
        'gallery_slides': GallerySlide.objects.order_by('order', '-created_at'),
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


def _bulk_price_factor(action, percent):
    if action == BulkPriceAdjustment.ACTION_INCREASE:
        return Decimal('1') + percent / Decimal('100')
    return Decimal('1') - percent / Decimal('100')


def _quantize_price(value):
    return value.quantize(Decimal('1'), rounding=ROUND_HALF_UP)


def _apply_bulk_price_adjustment(adjustment, queryset):
    factor = _bulk_price_factor(adjustment.action, adjustment.percent)
    updated = 0

    for item in queryset:
        changed = False

        if item.price is not None or item.sale_price is not None:
            BulkPriceSnapshot.objects.create(
                adjustment=adjustment,
                menu_item=item,
                old_price=item.price,
                old_sale_price=item.sale_price,
            )
            if item.price is not None:
                item.price = _quantize_price(item.price * factor)
            if item.sale_price is not None:
                item.sale_price = _quantize_price(item.sale_price * factor)
            item.save(update_fields=['price', 'sale_price'])
            changed = True

        for variant in item.variants.all():
            BulkPriceSnapshot.objects.create(
                adjustment=adjustment,
                menu_item=item,
                variant=variant,
                old_price=variant.price,
                old_sale_price=variant.sale_price,
            )
            variant.price = _quantize_price(variant.price * factor)
            if variant.sale_price is not None:
                variant.sale_price = _quantize_price(variant.sale_price * factor)
            variant.save(update_fields=['price', 'sale_price'])
            changed = True

        if item.variants.exists():
            item.sync_base_price_from_variants()
            item.save(update_fields=['price'])

        if changed:
            updated += 1

    adjustment.items_count = updated
    adjustment.save(update_fields=['items_count'])
    return updated


def _revert_bulk_price_adjustment(adjustment):
    items_to_sync = set()
    for snap in adjustment.snapshots.select_related('menu_item', 'variant'):
        if snap.variant_id:
            snap.variant.price = snap.old_price
            snap.variant.sale_price = snap.old_sale_price
            snap.variant.save(update_fields=['price', 'sale_price'])
            items_to_sync.add(snap.menu_item_id)
        else:
            snap.menu_item.price = snap.old_price
            snap.menu_item.sale_price = snap.old_sale_price
            snap.menu_item.save(update_fields=['price', 'sale_price'])

    for item in MenuItem.objects.filter(pk__in=items_to_sync).prefetch_related('variants'):
        if item.variants.exists():
            item.sync_base_price_from_variants()
            item.save(update_fields=['price'])


@login_required(login_url='panel_login')
@staff_required
def panel_bulk_prices(request):
    if request.method == 'POST':
        delete_id = request.POST.get('delete_adjustment')
        if delete_id:
            adjustment = get_object_or_404(BulkPriceAdjustment, pk=delete_id)
            summary = adjustment.summary
            with transaction.atomic():
                _revert_bulk_price_adjustment(adjustment)
                adjustment.delete()
            messages.success(request, f'Отменено: {summary}. Цены восстановлены.')
            return redirect('panel_bulk_prices')

        form = BulkPriceForm(request.POST)
        if form.is_valid():
            qs = MenuItem.objects.prefetch_related('variants')
            category = form.cleaned_data['category']
            if category:
                qs = qs.filter(category=category)

            adjustment = BulkPriceAdjustment.objects.create(
                action=form.cleaned_data['action'],
                percent=form.cleaned_data['percent'],
                category=category,
                created_by=request.user,
            )
            updated = _apply_bulk_price_adjustment(adjustment, qs)
            if updated:
                messages.success(request, f'Цены обновлены у {updated} позиций. Изменение сохранено в истории.')
            else:
                adjustment.delete()
                messages.warning(request, 'Не найдено позиций с ценами для изменения.')
            return redirect('panel_bulk_prices')
    else:
        form = BulkPriceForm()

    adjustments = BulkPriceAdjustment.objects.select_related('category', 'created_by')
    return render(request, 'panel/bulk_prices.html', {
        'form': form,
        'adjustments': adjustments,
    })

