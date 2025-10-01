from django.urls import path
from . import views

app_name = 'mailings'

urlpatterns = [
    path('', views.MailingListView.as_view(), name='mailing_list'),
    path('create/', views.MailingCreateView.as_view(), name='mailing_create'),
    path('<int:pk>/', views.MailingDetailView.as_view(), name='mailing_detail'),
    path('<int:pk>/edit/', views.MailingUpdateView.as_view(), name='mailing_update'),
    path('<int:pk>/delete/', views.MailingDeleteView.as_view(), name='mailing_delete'),

    # Добавленные URLs для управления рассылками
    path('<int:pk>/start/', views.mailing_start, name='mailing_start'),
    path('<int:pk>/stop/', views.mailing_stop, name='mailing_stop'),
    path('<int:pk>/test-send/', views.mailing_test_send, name='mailing_test_send'),
    path('<int:pk>/stats/', views.mailing_stats, name='mailing_stats'),
    path('<int:pk>/logs/', views.mailing_logs, name='mailing_logs'),
    path('<int:pk>/send-now/', views.send_mailing_now, name='send_mailing_now'),

    # Логи попыток отправки
    path('attempts/', views.MailingAttemptListView.as_view(), name='mailing_attempt_list'),
]