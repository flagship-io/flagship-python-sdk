from django.contrib import admin

# Register your models here.
from .models import Visitor

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    pass
