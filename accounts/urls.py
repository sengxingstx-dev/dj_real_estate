from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    # path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("logout/", views.custom_logout, name="logout"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("profile/new-v/", views.user_profile, name="user_profile"),
    path("profile/", views.ProfileDetailView.as_view(), name="profile"),
    path("profile/update/", views.ProfileUpdateView.as_view(), name="profile_update"),
    path("agents/", views.AgentListView.as_view(), name="agent_list"),
    path("agents/<int:pk>/", views.AgentDetailView.as_view(), name="agent_detail"),
    path("booking-history/", views.UserBookingHistoryView.as_view(), name="booking_history"),
]
