from django.db import models
import uuid

# Create your models herclce.
class Visitor(models.Model) :
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    context = models.CharField(max_length=1024)
