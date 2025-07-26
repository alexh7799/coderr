from rest_framework import serializers
from upload_app.models import FileUpload

class FileUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for file uploads.
    Args:
        serializers (_type_): _description_
    """
    class Meta:
        model = FileUpload
        fields = ['file', 'uploaded_at']