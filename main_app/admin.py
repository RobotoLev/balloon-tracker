from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models

# Register your models here.


admin.site.register(models.User, UserAdmin)


@admin.register(models.Contest)
class ContestAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Submission)
class SubmissionAdmin(admin.ModelAdmin):
    pass
