from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('profile/', views.volunteer_profile, name="volunteer_profile"),
    path('order-done/<int:order_id>', views.order_done, name="order_done"),
]
