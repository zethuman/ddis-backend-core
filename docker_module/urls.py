from django.urls import path
from .views import delete_an_image, get_an_image, list_of_images, clean_temp

urlpatterns = [
    path('images/list', list_of_images),
    path('images/get', get_an_image),
    path('images/delete', delete_an_image),

    path('settings/clean', clean_temp)
]
