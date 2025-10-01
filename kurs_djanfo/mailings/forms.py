from django import forms
from .models import Mailing
from messages_app.models import Message


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ["start_time", "end_time", "status", "clients", "message"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            # Фильтруем сообщения по владельцу
            self.fields["message"].queryset = Message.objects.filter(owner=user)
            # Фильтруем клиентов по владельцу
            self.fields["clients"].queryset = self.fields["clients"].queryset.filter(
                owner=user
            )
