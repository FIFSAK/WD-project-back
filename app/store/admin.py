from django.contrib import admin
from django.apps import apps
from .models import Clothes, ClothesAdmin  # Ensure you import ClothesAdmin

store_models = apps.get_app_config('store').get_models()

for model in store_models:
    if issubclass(model, Clothes):
        admin.site.register(model, ClothesAdmin)  # Use ClothesAdmin for Clothes subclasses
    else:
        try:
            admin.site.register(model)  # Register other models normally
        except admin.sites.AlreadyRegistered:
            pass
