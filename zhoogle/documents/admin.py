from django.contrib import admin
from .models import Document, Word, Occurrence

# Register your models here.
admin.site.register(Document)
admin.site.register(Word)
admin.site.register(Occurrence)