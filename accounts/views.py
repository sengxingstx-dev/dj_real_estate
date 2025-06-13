from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from properties.models import Booking, Inquiry, Property

from .forms import CustomAuthenticationForm, CustomUserCreationForm, UserProfileForm
from .models import UserProfile


@login_required
def user_profile(request):
    profile = request.user.profile
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("dashboard_user_list")
    else:
        form = UserProfileForm(instance=profile)
    return render(request, "accounts/profile.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        # Check if the logged-in user is a superuser
        if self.request.user.is_superuser:
            return reverse_lazy("dashboard_home")
        return super().get_success_url()


def custom_logout(request):
    logout(request)
    return redirect("home")


class CustomLogoutView(LogoutView):
    next_page = "home"


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Account created successfully! Please log in.")
        return response


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = "accounts/profile_detail.html"
    context_object_name = "profile"

    def get_object(self):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["properties"] = Property.objects.filter(agent=user)[:5]
        context["inquiries"] = Inquiry.objects.filter(user=user)[:5]
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = "accounts/profile_update.html"
    success_url = reverse_lazy("profile")

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        user = self.request.user
        user.first_name = self.request.POST.get("first_name")
        user.last_name = self.request.POST.get("last_name")
        user.email = self.request.POST.get("email")
        user.save()

        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)


class AgentListView(ListView):
    model = UserProfile
    template_name = "accounts/agent_list.html"
    context_object_name = "agents"

    def get_queryset(self):
        return UserProfile.objects.filter(user_type="agent")


class AgentDetailView(DetailView):
    model = UserProfile
    template_name = "accounts/agent_detail.html"
    context_object_name = "agent"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agent = self.get_object().user
        context["properties"] = Property.objects.filter(agent=agent)
        return context


class UserBookingHistoryView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "accounts/booking_history.html"
    context_object_name = "bookings"
    paginate_by = 10

    def get_queryset(self):
        return (
            Booking.objects.filter(user=self.request.user)
            .select_related("property", "property__location")
            .order_by("-created_at")
        )
