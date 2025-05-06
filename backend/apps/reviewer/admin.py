from django.contrib import admin
from reviewer.models import Review, ReviewDetails, Feedback

# Register your models here.
admin.site.register(Review)
admin.site.register(ReviewDetails)
admin.site.register(Feedback)