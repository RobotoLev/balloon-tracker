from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from . import models

# Register your models here.


# TODO: orderings?


class UserAdmin(DjangoUserAdmin):
    model = models.User

    list_display = ("username", "rooms_layout", "first_name", "last_name", "is_staff")
    fieldsets = (
        (None, {'fields': ('rooms_layout',)}),
    ) + DjangoUserAdmin.fieldsets


admin.site.register(models.User, UserAdmin)


@admin.register(models.Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'test_system', 'admin')


@admin.register(models.Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'contest', 'problem_index', 'author', 'time_from_start', 'verdict')


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('submission', 'balloon_color', 'room', 'place', 'author_name', 'volunteer', 'done')
