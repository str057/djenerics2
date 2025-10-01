from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.models import Group
from .models import User
from .forms import UserRegisterForm, UserProfileForm


class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Регистрация прошла успешно!")
        return redirect("index")


class UserLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("index")

    def form_valid(self, form):
        messages.success(self.request, "Вы успешно вошли в систему!")
        return super().form_valid(form)


def logout_view(request):
    logout(request)
    messages.success(request, "Вы успешно вышли из системы!")
    return redirect("index")


class UserProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "registration/profile.html"

    def get_success_url(self):
        return reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Профиль успешно обновлен!")
        return super().form_valid(form)


# ДОБАВЛЕНО: View для управления пользователями (для менеджеров)
class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = "users/user_list.html"
    permission_required = 'users.can_view_all_users'
    context_object_name = 'users'

    def get_queryset(self):
        if self.request.user.has_perm('users.can_view_all_users'):
            return User.objects.all()
        return User.objects.filter(pk=self.request.user.pk)


# ДОБАВЛЕНО: View для блокировки/разблокировки пользователей
class UserToggleActiveView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = User
    permission_required = 'users.can_disable_user'
    fields = []  # Не нужны поля формы, меняем только is_active

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        if user != request.user:  # Нельзя заблокировать себя
            user.is_active = not user.is_active
            user.save()

            action = "разблокирован" if user.is_active else "заблокирован"
            messages.success(request, f"Пользователь {user.email} {action}")
        else:
            messages.error(request, "Нельзя заблокировать себя")

        return redirect('user_list')

    def get_success_url(self):
        return reverse_lazy('user_list')


# ДОБАВЛЕНО: View для назначения менеджеров
class UserToggleManagerView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = User
    permission_required = 'users.can_disable_user'
    fields = []  # Не нужны поля формы

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        managers_group, created = Group.objects.get_or_create(name='Managers')

        if managers_group in user.groups.all():
            user.groups.remove(managers_group)
            action = "удален из группы Менеджеры"
        else:
            user.groups.add(managers_group)
            action = "добавлен в группу Менеджеры"

        messages.success(request, f"Пользователь {user.email} {action}")
        return redirect('user_list')

    def get_success_url(self):
        return reverse_lazy('user_list')