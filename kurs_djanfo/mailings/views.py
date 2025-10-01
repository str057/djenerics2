from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Mailing, MailingAttempt
from .forms import MailingForm
from clients.models import Client
from .services import send_mailing, send_test_mailing  # Импортируем сервисные функции


def index(request):
    """
    Главная страница приложения
    """
    now = timezone.now()

    active_mailings = Mailing.objects.filter(
        status="started", start_time__lte=now, end_time__gte=now
    )

    context = {
        "total_mailings": Mailing.objects.count(),
        "active_mailings": active_mailings.count(),
        "unique_clients": Client.objects.values("email").distinct().count(),
    }
    return render(request, "index.html", context)


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailings/mailing_list_new.html"
    context_object_name = "mailings"

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailings/mailing_detail.html"

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attempts"] = MailingAttempt.objects.filter(mailing=self.object)
        return context


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailings/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form_simple.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["clients"].queryset = Client.objects.filter(owner=self.request.user)
        return form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Рассылка создана успешно!")
        return response


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form_simple.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = 'mailings/mailing_attempt_list.html'
    context_object_name = 'attempts'
    paginate_by = 20

    def get_queryset(self):
        # Для администраторов показываем все попытки
        if self.request.user.is_staff:
            return MailingAttempt.objects.all().order_by('-attempt_time')
        # Для обычных пользователей - только их рассылки
        return MailingAttempt.objects.filter(
            mailing__owner=self.request.user
        ).order_by('-attempt_time')


def send_mailing_now(request, pk):
    """Функция для ручной отправки рассылки"""
    try:
        mailing = Mailing.objects.get(id=pk, owner=request.user)

        # Проверяем права доступа
        if mailing.owner != request.user:
            messages.error(request, "У вас нет прав для отправки этой рассылки")
            return redirect("mailings:mailing_list")

        # Отправляем рассылку
        mailing.send_mailing()
        messages.success(request, "Рассылка отправлена успешно!")

    except Mailing.DoesNotExist:
        messages.error(request, "Рассылка не найдена")
    except Exception as e:
        messages.error(request, f"Ошибка при отправке: {e}")

    return redirect("mailings:mailing_detail", pk=pk)


# ДОБАВЛЕННЫЕ ПРЕДСТАВЛЕНИЯ ДЛЯ УПРАВЛЕНИЯ РАССЫЛКАМИ

@require_POST
@login_required
def mailing_start(request, pk):
    """Запуск рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)

    # Проверяем права доступа
    if mailing.owner != request.user and not request.user.has_perm('mailings.can_start_mailing'):
        messages.error(request, 'У вас нет прав для запуска этой рассылки')
        return redirect('mailings:mailing_list')

    try:
        successful, failed = send_mailing(mailing)
        messages.success(request, f'Рассылка "{mailing.name}" запущена. Успешно: {successful}, Ошибок: {failed}')
    except Exception as e:
        messages.error(request, f'Ошибка запуска рассылки: {str(e)}')

    return redirect('mailings:mailing_list')


@require_POST
@login_required
def mailing_stop(request, pk):
    """Остановка рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)

    # Проверяем права доступа
    if mailing.owner != request.user and not request.user.has_perm('mailings.can_stop_mailing'):
        messages.error(request, 'У вас нет прав для остановки этой рассылки')
        return redirect('mailings:mailing_list')

    try:
        mailing.status = Mailing.Status.STOPPED
        mailing.save()
        messages.success(request, f'Рассылка "{mailing.name}" остановлена')
    except Exception as e:
        messages.error(request, f'Ошибка остановки рассылки: {str(e)}')

    return redirect('mailings:mailing_list')


@require_POST
@login_required
def mailing_test_send(request, pk):
    """Тестовая отправка рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
    test_email = request.POST.get('test_email')

    # Проверяем права доступа
    if mailing.owner != request.user and not request.user.has_perm('mailings.can_start_mailing'):
        messages.error(request, 'У вас нет прав для тестовой отправки этой рассылки')
        return redirect('mailings:mailing_list')

    if not test_email:
        messages.error(request, 'Введите email для тестовой отправки')
        return redirect('mailings:mailing_list')

    try:
        success, message = send_test_mailing(mailing, test_email)

        if success:
            messages.success(request, f'Тестовая рассылка отправлена на {test_email}')
        else:
            messages.error(request, f'Ошибка тестовой отправки: {message}')

    except Exception as e:
        messages.error(request, f'Ошибка тестовой отправки: {str(e)}')

    return redirect('mailings:mailing_list')


@login_required
def mailing_stats(request, pk):
    """Статистика по рассылке"""
    mailing = get_object_or_404(Mailing, pk=pk)

    # Проверяем права доступа
    if mailing.owner != request.user and not request.user.is_staff:
        messages.error(request, 'У вас нет прав для просмотра статистики этой рассылки')
        return redirect('mailings:mailing_list')

    attempts = MailingAttempt.objects.filter(mailing=mailing)
    total_attempts = attempts.count()
    successful_attempts = attempts.filter(status=MailingAttempt.Status.SUCCESS).count()
    failed_attempts = attempts.filter(status=MailingAttempt.Status.FAILED).count()

    context = {
        'mailing': mailing,
        'attempts': attempts,
        'total_attempts': total_attempts,
        'successful_attempts': successful_attempts,
        'failed_attempts': failed_attempts,
        'success_rate': (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0,
    }

    return render(request, 'mailings/mailing_stats.html', context)


@login_required
def mailing_logs(request, pk):
    """Логи рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk)

    # Проверяем права доступа
    if mailing.owner != request.user and not request.user.is_staff:
        messages.error(request, 'У вас нет прав для просмотра логов этой рассылки')
        return redirect('mailings:mailing_list')

    attempts = MailingAttempt.objects.filter(mailing=mailing).order_by('-attempt_time')

    context = {
        'mailing': mailing,
        'attempts': attempts,
    }

    return render(request, 'mailings/mailing_logs.html', context)