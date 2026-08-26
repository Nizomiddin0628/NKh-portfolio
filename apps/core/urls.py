from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("cv/", views.cv, name="cv"),
    path("contact/", views.contact, name="contact"),
]
