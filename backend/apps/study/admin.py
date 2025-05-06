from django.contrib import admin
from .models import *

admin.site.register(Study)
admin.site.register(CodeBook)
admin.site.register(CodeBookColumn)
admin.site.register(CodeBookRow)
