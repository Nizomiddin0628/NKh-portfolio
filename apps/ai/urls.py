from django.urls import path

from . import views

app_name = "ai"

urlpatterns = [
    path("status/", views.status, name="status"),
    path("ask/", views.ask, name="ask"),
    path("transcribe/", views.transcribe, name="transcribe"),
    path("actions/", views.actions_list, name="actions"),
    path("actions/<int:pk>/confirm/", views.action_confirm, name="action_confirm"),
    path("actions/<int:pk>/cancel/", views.action_cancel, name="action_cancel"),
    path("tg/", views.tg_webhook, name="tg_webhook"),
]
