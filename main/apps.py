from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        from .image_cleanup import register_image_cleanup
        from .models import GallerySlide, MenuItem, MosaicPhoto, Promotion, SiteImage

        register_image_cleanup(
            MenuItem,
            Promotion,
            GallerySlide,
            SiteImage,
            MosaicPhoto,
        )
