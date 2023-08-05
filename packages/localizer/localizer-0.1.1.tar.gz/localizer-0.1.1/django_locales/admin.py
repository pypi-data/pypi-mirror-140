from django.contrib import admin

# Register your models here.

from .models import Group, GroupItem


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(GroupItem)
class GroupItemAdmin(admin.ModelAdmin):
    list_display = ("id", "language", "key", "translate")
    list_filter = ("group",)
