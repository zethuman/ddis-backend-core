from django.urls import path

from .views import pull_an_image_by_name, pull_an_image_by_hash, push_an_image

urlpatterns = [
    path('images/pull/hash/', pull_an_image_by_hash),
    path('images/pull/name/', pull_an_image_by_name),
    path('images/push/', push_an_image),

    path('public/get/', pull_an_image_by_hash),
    path('public/post/', pull_an_image_by_hash),
    path('private/get/', pull_an_image_by_name),
    path('private/post/', push_an_image),
]
