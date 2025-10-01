from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from .models import Client


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10

    def get_queryset(self):
        # Если пользователь имеет право видеть всех клиентов
        if self.request.user.has_perm('clients.can_view_all_clients'):
            return Client.objects.all().select_related('owner').order_by('-created_at')
        else:
            # Иначе только своих клиентов
            return Client.objects.filter(owner=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем информацию о правах в контекст
        context['user_can_view_all'] = self.request.user.has_perm('clients.can_view_all_clients')
        context['user_can_edit_any'] = self.request.user.has_perm('clients.can_edit_any_client')
        context['user_can_delete_any'] = self.request.user.has_perm('clients.can_delete_any_client')
        return context


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'

    def get_queryset(self):
        if self.request.user.has_perm('clients.can_view_all_clients'):
            return Client.objects.all().select_related('owner')
        return Client.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем информацию о правах в контекст
        context['user_can_edit_any'] = self.request.user.has_perm('clients.can_edit_any_client')
        context['user_can_delete_any'] = self.request.user.has_perm('clients.can_delete_any_client')
        return context


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    template_name = 'clients/client_form.html'
    fields = ['name', 'email', 'phone', 'address', 'comment']
    success_url = reverse_lazy('clients:list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Client
    template_name = 'clients/client_form.html'
    fields = ['name', 'email', 'phone', 'address', 'comment']
    success_url = reverse_lazy('clients:list')

    def get_permission_required(self):
        client = self.get_object()
        # Если пользователь владелец клиента - разрешаем без дополнительных прав
        if client.owner == self.request.user:
            return []
        # Если не владелец - требуем право на редактирование любых клиентов
        return ['clients.can_edit_any_client']

    def get_queryset(self):
        # Базовый queryset
        qs = super().get_queryset()
        return qs.select_related('owner')


class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:list')

    def get_permission_required(self):
        client = self.get_object()
        # Если пользователь владелец клиента - разрешаем без дополнительных прав
        if client.owner == self.request.user:
            return []
        # Если не владелец - требуем право на удаление любых клиентов
        return ['clients.can_delete_any_client']

    def get_queryset(self):
        # Базовый queryset
        qs = super().get_queryset()
        return qs.select_related('owner')


@login_required
@permission_required('clients.can_disable_client', raise_exception=True)
def disable_client(request, pk):
    """Отключение клиента - только для менеджеров"""
    client = get_object_or_404(Client, pk=pk)

    # Логика отключения клиента
    client.is_active = False
    client.save()

    return redirect('clients:list')


@login_required
def toggle_client_status(request, pk):
    """Переключение статуса клиента (активен/неактивен)"""
    client = get_object_or_404(Client, pk=pk)

    # Проверяем права: либо владелец, либо есть право на редактирование любых клиентов
    if client.owner == request.user or request.user.has_perm('clients.can_edit_any_client'):
        client.is_active = not client.is_active
        client.save()

    return redirect('clients:list')