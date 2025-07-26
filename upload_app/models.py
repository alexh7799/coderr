from django.db import models

class FileUpload(models.Model):
    file = models.FileField(upload_to='uploads/', blank=True, null=True, default="")
    uploaded_at = models.DateTimeField(auto_now_add=True)
