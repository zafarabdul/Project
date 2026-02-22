from django.urls import path
from .views import data_entry_message, data_entry_photo, register_gmail, data_entry_list_create
from .debug_views import debug_paths

urlpatterns = [
    path('data', data_entry_list_create, name='data-list-create'),
    path('data/register/<str:custom_id>/<str:gmail>/', register_gmail, name='register-gmail'),
    path('data/<str:custom_id>/<str:key>/<str:algoId>/message/', data_entry_message, name='data-message'),
    path('data/<str:custom_id>/<str:key>/photo/', data_entry_photo, name='data-photo'),
    path('debug/paths/', debug_paths, name='debug-paths'),
]
