from rest_framework import serializers
from .models import UserEntry, EntryData

class EntryDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryData
        fields = ['key', 'message', 'image']

class UserEntrySerializer(serializers.ModelSerializer):
    # We can include nested data if needed, but for listing/creation, user info is key.
    # We might want to handle creation of nested data here or separate views.
    # For now, let's keep it simple.
    class Meta:
        model = UserEntry
        fields = ['custom_id', 'gmail']

    def validate_custom_id(self, value):
        if len(value) != 10:
            raise serializers.ValidationError("ID must be exactly 10 characters long.")
        return value
