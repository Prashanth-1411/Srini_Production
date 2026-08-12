from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from audit.services import log_action

from .forms import LoginForm


class AppLoginView(LoginView):
    authentication_form = LoginForm
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(
            self.request,
            "LOGIN",
            "auth",
            self.request.user.username,
            old=None,
            new={"session": self.request.session.session_key},
        )
        return response


@login_required
def logout_view(request):
    user = request.user
    logout(request)
    return redirect("accounts:login")
