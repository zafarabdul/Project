from django.db import models

class UserEntry(models.Model):
    custom_id = models.CharField(max_length=10, unique=True)
    gmail = models.EmailField()

    def __str__(self):
        return self.custom_id

class EntryData(models.Model):
    user_entry = models.ForeignKey(UserEntry, on_delete=models.CASCADE, related_name='data_entries')
    key = models.CharField(max_length=15)
    message = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='', blank=True, null=True)
    algoId = models.TextField()

    def __str__(self):
        return f"{self.user_entry.custom_id} - {self.key}"
