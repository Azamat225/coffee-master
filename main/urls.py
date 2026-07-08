from django.urls import path

from . import panel_views, views

urlpatterns = [
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('', views.home, name='home'),
    path('menu/', views.menu_page, name='menu'),
    path('promotions/', views.promotions_page, name='promotions'),
    path('gallery/', views.gallery_page, name='gallery'),
    path('contacts/', views.contacts_page, name='contacts'),
    path('panel/login/', panel_views.panel_login, name='panel_login'),
    path('panel/logout/', panel_views.panel_logout, name='panel_logout'),
    path('panel/', panel_views.panel_dashboard, name='panel_dashboard'),
    path('panel/menu/', panel_views.panel_menu_list, name='panel_menu_list'),
    path('panel/menu/add/', panel_views.panel_menu_edit, name='panel_menu_add'),
    path('panel/menu/<int:pk>/', panel_views.panel_menu_edit, name='panel_menu_edit'),
    path('panel/menu/<int:pk>/toggle/', panel_views.panel_menu_toggle, name='panel_menu_toggle'),
    path('panel/promotions/', panel_views.panel_promotions, name='panel_promotions'),
    path('panel/promotions/add/', panel_views.panel_promotion_edit, name='panel_promotion_add'),
    path('panel/promotions/<int:pk>/', panel_views.panel_promotion_edit, name='panel_promotion_edit'),
    path('panel/images/', panel_views.panel_images, name='panel_images'),
    path('panel/settings/', panel_views.panel_settings, name='panel_settings'),
    path('panel/tags/', panel_views.panel_tags, name='panel_tags'),
    path('panel/bulk-prices/', panel_views.panel_bulk_prices, name='panel_bulk_prices'),
]
