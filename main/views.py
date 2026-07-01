from django.shortcuts import render

from .models import GallerySlide


def home(request):
    slides = GallerySlide.objects.filter(is_active=True)
    return render(request, 'main/home.html', {'slides': slides})
