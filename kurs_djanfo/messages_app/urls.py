from django.urls import path
from . import views

app_name = "messages"

urlpatterns = [
    path("", views.MessageListView.as_view(), name="list"),
    path("create/", views.MessageCreateView.as_view(), name="message_create"),
    path("<int:pk>/edit/", views.MessageUpdateView.as_view(), name="message_update"),
    path("<int:pk>/delete/", views.MessageDeleteView.as_view(), name="message_delete"),
]
