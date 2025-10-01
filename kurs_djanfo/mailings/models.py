from django.db import models
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class MailingAttempt(models.Model):
    """Модель для хранения попыток отправки рассылки"""

    mailing = models.ForeignKey(
        "Mailing", on_delete=models.CASCADE, related_name="attempts"
    )
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Время попытки")
    status = models.CharField(max_length=20, verbose_name="Статус")
    server_response = models.TextField(
        blank=True, null=True, verbose_name="Ответ сервера"
    )
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Клиент",
    )

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"
        ordering = ["-attempt_time"]

    def __str__(self):
        return f"Попытка {self.id} - {self.status}"


class Mailing(models.Model):
    STATUS_CHOICES = [
        ("created", "Создана"),
        ("started", "Запущена"),
        ("completed", "Завершена"),
    ]

    start_time = models.DateTimeField(verbose_name="Время начала")
    end_time = models.DateTimeField(verbose_name="Время окончания")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="created", verbose_name="Статус"
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец")
    clients = models.ManyToManyField("clients.Client", verbose_name="Клиенты")
    message = models.ForeignKey(
        "messages_app.Message", on_delete=models.CASCADE, verbose_name="Сообщение"
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def send_mailing(self):
        """Метод для отправки рассылки"""
        now = timezone.now()

        # Проверяем время рассылки
        if now < self.start_time:
            raise Exception("Время рассылки еще не наступило")

        if now > self.end_time:
            raise Exception("Время рассылки уже прошло")

        success_count = 0
        error_count = 0

        main_attempt = MailingAttempt.objects.create(
            mailing=self, status="started", server_response="Начало рассылки"
        )

        for client in self.clients.all():
            try:
                send_mail(
                    subject=self.message.subject,
                    message=self.message.body,
                    from_email=None,
                    recipient_list=[client.email],
                    fail_silently=False,
                )

                MailingAttempt.objects.create(
                    mailing=self,
                    status="success",
                    server_response="Email отправлен успешно",
                    client=client,
                )
                success_count += 1

            except Exception as e:
                # Создаем запись об ошибке для клиента
                MailingAttempt.objects.create(
                    mailing=self, status="failed", server_response=str(e), client=client
                )
                error_count += 1

        main_attempt.status = "completed"
        main_attempt.server_response = (
            f"Успешно: {success_count}, Ошибок: {error_count}"
        )
        main_attempt.save()

        if success_count > 0:
            self.status = "completed"
            self.save()

        return success_count, error_count

    def __str__(self):
        return f"Рассылка {self.id} - {self.get_status_display()}"
