from django.contrib import admin
from .models import UserEntry, EntryData

@admin.register(UserEntry)
class UserEntryAdmin(admin.ModelAdmin):
    list_display = ('custom_id', 'gmail')
    search_fields = ('custom_id', 'gmail')

@admin.register(EntryData)
class EntryDataAdmin(admin.ModelAdmin):
    list_display = ('user_entry', 'key', 'algoId', 'message')
    search_fields = ('key', 'algoId', 'user_entry__custom_id')
