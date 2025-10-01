from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "email", "phone"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "owner",
                    "name",
                    "email",
                    "phone",
                    "address",
                    "comment",
                )  # Добавлено comment
            },
        ),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
