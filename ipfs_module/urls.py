from django.urls import path

from .views import all_images, pull_an_image_by_hash, push_an_image

urlpatterns = [
    path('images/', all_images),
    path('images/pull/hash/', pull_an_image_by_hash),
    path('images/push/', push_an_image),
]
