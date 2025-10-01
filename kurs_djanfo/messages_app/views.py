from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Message


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "messages_app/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ["subject", "body"]
    template_name = "messages_app/message_form.html"
    success_url = reverse_lazy("messages_app:list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    fields = ["subject", "body"]
    template_name = "messages_app/message_form.html"
    success_url = reverse_lazy("messages_app:list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "messages_app/message_confirm_delete.html"
    success_url = reverse_lazy("messages_app:list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)
