from django.contrib import admin

# Register your models here.
from .models import Target, Database, File

admin.site.register(Target)
admin.site.register(Database)
admin.site.register(File)
