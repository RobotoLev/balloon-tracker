from django.urls import path

from . import views

urlpatterns = [
    path('test/cf/<int:contest_id>', views.test_codeforces),
    path('test/yc/<int:contest_id>', views.test_yandex_contest),
    path('', views.index),
    path('profile/', views.volunteer_profile, name="volunteer_profile"),
]
