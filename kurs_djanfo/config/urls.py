from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from mailings.views import index
from django.contrib.auth import views as auth_views
from users.views import UserProfileView, UserLoginView, UserRegisterView  # Добавил UserRegisterView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),

    # Добавьте эти пути для аутентификации
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", UserRegisterView.as_view(), name="register"),  # ← ДОБАВИЛ РЕГИСТРАЦИЮ
    path("profile/", UserProfileView.as_view(), name="profile"),

    path("users/", include("users.urls", namespace="users")),
    path("clients/", include("clients.urls", namespace="clients")),
    path("messages/", include("messages_app.urls", namespace="messages_app")),
    path("mailings/", include("mailings.urls", namespace="mailings")),
    path('', include('main.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)