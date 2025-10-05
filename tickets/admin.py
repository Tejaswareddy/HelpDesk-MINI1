from django.contrib import admin
from .models import Ticket, Comment, TimelineEntry, Profile

admin.site.register(Ticket)
admin.site.register(Comment)
admin.site.register(TimelineEntry)
admin.site.register(Profile)
