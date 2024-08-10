from django.contrib import admin
from .models import Habit, HabitInstance, Tag

admin.site.register(Habit)
admin.site.register(HabitInstance)
admin.site.register(Tag)
