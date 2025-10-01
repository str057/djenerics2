from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Client(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Владелец", default=1
    )
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.TextField(verbose_name="Адрес", blank=True)
    comment = models.TextField(
        verbose_name="Комментарий", blank=True
    )  # ← Добавьте это поле
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        permissions = [
            ("can_view_all_clients", "Может просматривать всех клиентов"),
            ("can_disable_client", "Может отключать клиентов"),
            ("can_edit_any_client", "Может редактировать любого клиента"),
            ("can_delete_any_client", "Может удалять любого клиента"),
        ]