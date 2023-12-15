from django.urls import path

from . import views

urlpatterns = [
    path('test/<int:contest_id>', views.test),
]
