from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from accounts.models import UserProfile
from dashboard.forms import (
    CustomUserCreationFormAdmin,
    FeatureFormAdmin,
    InquiryFormAdmin,
    LocationFormAdmin,
    PropertyFormAdmin,
    PropertyImageFormAdmin,
    PropertyTypeFormAdmin,
    UserFormAdmin,
    UserProfileFormAdmin,
)
from properties.models import (
    Feature,
    Inquiry,
    Location,
    Property,
    PropertyImage,
    PropertyType,
)


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.profile.user_type == "admin"


class AgentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.profile.user_type in [
            "admin",
            "agent",
        ]


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # For admin/staff, show all properties and inquiries
        if user.is_staff or user.profile.user_type in ["admin", "agent"]:
            if user.profile.user_type == "agent" and not user.is_staff:
                properties = Property.objects.filter(agent=user)
                inquiries = Inquiry.objects.filter(property__agent=user)
            else:
                properties = Property.objects.all()
                inquiries = Inquiry.objects.all()

            # Statistics
            context["total_properties"] = properties.count()
            context["total_inquiries"] = inquiries.count()
            context["recent_properties"] = properties.order_by("-created_at")[:5]
            context["recent_inquiries"] = inquiries.order_by("-created_at")[:5]

            # Property status counts
            context["properties_for_sale"] = properties.filter(status="for_sale").count()
            context["properties_for_rent"] = properties.filter(status="for_rent").count()
            context["properties_sold"] = properties.filter(status="sold").count()
            context["properties_rented"] = properties.filter(status="rented").count()

            # Property types distribution
            property_types = PropertyType.objects.annotate(count=Count("property")).order_by(
                "-count"
            )
            context["property_types"] = property_types

            # Recent activity
            last_month = timezone.now() - timedelta(days=30)
            context["monthly_new_properties"] = properties.filter(
                created_at__gte=last_month
            ).count()
            context["monthly_new_inquiries"] = inquiries.filter(created_at__gte=last_month).count()

        # For regular users, show their inquiries
        else:
            inquiries = Inquiry.objects.filter(user=user)
            context["user_inquiries"] = inquiries.order_by("-created_at")
            context["total_inquiries"] = inquiries.count()

        return context


# User Management Views
class UserListView(AdminRequiredMixin, ListView):
    model = UserProfile
    template_name = "dashboard/users/user_list.html"
    context_object_name = "profiles"
    paginate_by = 10

    def get_queryset(self):
        return UserProfile.objects.select_related("user").all().order_by("-user__date_joined")


class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationFormAdmin
    template_name = "dashboard/users/user_form.html"
    success_url = reverse_lazy("dashboard_users")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Create New User"
        return context

    def form_valid(self, form):
        # The form's save method now handles creating User and setting UserProfile.user_type
        user = form.save()
        messages.success(self.request, f"User '{user.username}' created successfully.")
        return redirect(self.success_url)


class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User  # We are updating the User object
    template_name = "dashboard/users/user_form.html"
    form_class = UserFormAdmin
    success_url = reverse_lazy("dashboard_users")
    # No single form_class, as we handle two forms

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Update User"
        user_instance = self.get_object()
        profile_instance, _ = UserProfile.objects.get_or_create(user=user_instance)

        if self.request.POST:
            context["user_form"] = UserFormAdmin(self.request.POST, instance=user_instance)
            context["profile_form"] = UserProfileFormAdmin(
                self.request.POST, self.request.FILES, instance=profile_instance
            )
        else:
            context["user_form"] = UserFormAdmin(instance=user_instance)
            context["profile_form"] = UserProfileFormAdmin(instance=profile_instance)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # self.object is the User instance
        profile, _ = UserProfile.objects.get_or_create(user=self.object)

        user_form = UserFormAdmin(request.POST, instance=self.object)
        profile_form = UserProfileFormAdmin(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f"User '{self.object.username}' updated successfully.")
            return redirect(self.get_success_url())
        else:
            # Re-populate context with forms containing errors for rendering
            return self.render_to_response(
                self.get_context_data(user_form=user_form, profile_form=profile_form)
            )


class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User  # Deleting User will cascade to UserProfile due to on_delete=models.CASCADE
    template_name = "dashboard/users/user_confirm_delete.html"
    success_url = reverse_lazy("dashboard_users")
    context_object_name = "user_to_delete"

    def form_valid(self, form):
        messages.success(self.request, f"User '{self.object.username}' deleted successfully.")
        return super().form_valid(form)


class UserDetailView(AdminRequiredMixin, DetailView):
    model = User
    template_name = "dashboard/users/user_detail.html"
    context_object_name = "user_obj"  # To avoid conflict with 'user' in template context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # UserProfile can be accessed in the template via user_obj.profile
        # Ensure profile exists, though signals should handle creation.
        # get_or_create is a good safety measure if needed, but user_obj.profile should work.
        context["profile"], _ = UserProfile.objects.get_or_create(user=self.object)
        return context


# PropertyType Management Views
class PropertyTypeListView(AdminRequiredMixin, ListView):
    model = PropertyType
    template_name = "dashboard/property_types/property_type_list.html"
    context_object_name = "property_types"
    paginate_by = 10

    def get_queryset(self):
        return PropertyType.objects.all().order_by("name")


class PropertyTypeCreateView(AdminRequiredMixin, CreateView):
    model = PropertyType
    form_class = PropertyTypeFormAdmin
    template_name = "dashboard/property_types/property_type_form.html"
    success_url = reverse_lazy("dashboard_property_types")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Add New Property Type"
        return context

    def form_valid(self, form):
        messages.success(
            self.request, f"Property Type '{form.instance.name}' created successfully."
        )
        return super().form_valid(form)


class PropertyTypeUpdateView(AdminRequiredMixin, UpdateView):
    model = PropertyType
    form_class = PropertyTypeFormAdmin
    template_name = "dashboard/property_types/property_type_form.html"
    success_url = reverse_lazy("dashboard_property_types")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = f"Update Property Type: {self.object.name}"
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Property Type '{self.object.name}' updated successfully.")
        return super().form_valid(form)


class PropertyTypeDeleteView(AdminRequiredMixin, DeleteView):
    model = PropertyType
    template_name = "dashboard/property_types/property_type_confirm_delete.html"
    success_url = reverse_lazy("dashboard_property_types")
    context_object_name = "property_type_to_delete"

    def form_valid(self, form):
        messages.success(self.request, f"Property Type '{self.object.name}' deleted successfully.")
        return super().form_valid(form)


# Location Management Views
class LocationListView(AdminRequiredMixin, ListView):
    model = Location
    template_name = "dashboard/locations/location_list.html"
    context_object_name = "locations"
    paginate_by = 10

    def get_queryset(self):
        return Location.objects.all().order_by("name")


class LocationCreateView(AdminRequiredMixin, CreateView):
    model = Location
    form_class = LocationFormAdmin
    template_name = "dashboard/locations/location_form.html"
    success_url = reverse_lazy("dashboard_locations")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Add New Location"
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Location '{form.instance.name}' created successfully.")
        return super().form_valid(form)


class LocationUpdateView(AdminRequiredMixin, UpdateView):
    model = Location
    form_class = LocationFormAdmin
    template_name = "dashboard/locations/location_form.html"
    success_url = reverse_lazy("dashboard_locations")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = f"Update Location: {self.object.name}"
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Location '{self.object.name}' updated successfully.")
        return super().form_valid(form)


class LocationDeleteView(AdminRequiredMixin, DeleteView):
    model = Location
    template_name = "dashboard/locations/location_confirm_delete.html"
    success_url = reverse_lazy("dashboard_locations")
    context_object_name = "location_to_delete"

    def form_valid(self, form):
        messages.success(self.request, f"Location '{self.object.name}' deleted successfully.")
        return super().form_valid(form)


# Feature Management Views
class FeatureListView(AdminRequiredMixin, ListView):
    model = Feature
    template_name = "dashboard/features/feature_list.html"
    context_object_name = "features"
    paginate_by = 10

    def get_queryset(self):
        return Feature.objects.all().order_by("name")


class FeatureCreateView(AdminRequiredMixin, CreateView):
    model = Feature
    form_class = FeatureFormAdmin
    template_name = "dashboard/features/feature_form.html"
    success_url = reverse_lazy("dashboard_features")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Add New Feature"
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Feature '{form.instance.name}' created successfully.")
        return super().form_valid(form)


class FeatureUpdateView(AdminRequiredMixin, UpdateView):
    model = Feature
    form_class = FeatureFormAdmin
    template_name = "dashboard/features/feature_form.html"
    success_url = reverse_lazy("dashboard_features")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = f"Update Feature: {self.object.name}"
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Feature '{self.object.name}' updated successfully.")
        return super().form_valid(form)


class FeatureDeleteView(AdminRequiredMixin, DeleteView):
    model = Feature
    template_name = "dashboard/features/feature_confirm_delete.html"
    success_url = reverse_lazy("dashboard_features")
    context_object_name = "feature_to_delete"

    def form_valid(self, form):
        messages.success(self.request, f"Feature '{self.object.name}' deleted successfully.")
        return super().form_valid(form)


# Property Management Views
class PropertyListAdminView(AgentRequiredMixin, ListView):
    model = Property
    template_name = "dashboard/properties/property_list.html"
    context_object_name = "properties"
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.profile.user_type == "admin":
            return Property.objects.all().order_by("-created_at")
        else:
            return Property.objects.filter(agent=user).order_by("-created_at")


class PropertyCreateAdminView(AgentRequiredMixin, CreateView):
    model = Property
    form_class = PropertyFormAdmin
    template_name = "dashboard/properties/property_form.html"
    success_url = reverse_lazy("dashboard_properties")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Add New Property"
        return context

    def form_valid(self, form):
        property_instance = form.save(commit=False)
        # If user is agent and not staff, ensure agent is set to current user
        if self.request.user.profile.user_type == "agent" and not self.request.user.is_staff:
            property_instance.agent = self.request.user
        property_instance.save()
        form.save_m2m()  # Important for ManyToMany fields like 'features'
        messages.success(
            self.request, f"Property '{property_instance.title}' created successfully."
        )
        return redirect(self.success_url)


class PropertyUpdateAdminView(AgentRequiredMixin, UpdateView):
    model = Property
    form_class = PropertyFormAdmin
    template_name = "dashboard/properties/property_form.html"
    success_url = reverse_lazy("dashboard_properties")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # self.object is the Property instance
        context["form_title"] = f"Update Property: {self.object.title}"
        context["property_images"] = self.object.images.all()  # Get related images
        # Form for adding a new image, not bound to an instance
        context["new_image_form"] = PropertyImageFormAdmin()
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Property '{self.object.title}' updated successfully.")
        return super().form_valid(form)


class PropertyDeleteAdminView(AgentRequiredMixin, DeleteView):
    model = Property
    template_name = "dashboard/properties/property_confirm_delete.html"
    success_url = reverse_lazy("dashboard_properties")
    context_object_name = "property_to_delete"

    def form_valid(self, form):
        messages.success(self.request, f"Property '{self.object.title}' deleted successfully.")
        return super().form_valid(form)


# PropertyImage Management Views (Nested under Property Update)
class PropertyImageCreateAdminView(AgentRequiredMixin, CreateView):
    model = PropertyImage
    form_class = PropertyImageFormAdmin
    template_name = "dashboard/properties/property_image_form.html"
    # Success URL will redirect back to the property edit page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Add New Gallery Image"
        context["property_pk"] = self.kwargs.get("property_pk")  # Pass property_pk for cancel link
        return context

    def form_valid(self, form):
        property_pk = self.kwargs.get("property_pk")
        property_instance = get_object_or_404(Property, pk=property_pk)
        form.instance.property = property_instance
        messages.success(self.request, "Gallery image added successfully.")
        return super().form_valid(form)  # Call super after setting property

    def get_success_url(self):
        # self.object is the newly created PropertyImage instance, set by super().form_valid()
        return reverse_lazy("dashboard_property_update", kwargs={"pk": self.object.property.pk})


class PropertyImageUpdateAdminView(AgentRequiredMixin, UpdateView):
    model = PropertyImage
    form_class = PropertyImageFormAdmin
    template_name = "dashboard/properties/property_image_form.html"
    context_object_name = "image_obj"  # To avoid conflict with 'image' if used elsewhere

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Update Gallery Image"
        context["property_pk"] = self.object.property.pk  # For cancel link
        return context

    def get_success_url(self):
        messages.success(self.request, "Gallery image updated successfully.")
        return reverse_lazy("dashboard_property_update", kwargs={"pk": self.object.property.pk})


class PropertyImageDeleteAdminView(AgentRequiredMixin, DeleteView):
    model = PropertyImage
    template_name = "dashboard/properties/property_image_confirm_delete.html"
    context_object_name = "image_to_delete"

    def get_success_url(self):
        property_pk = self.object.property.pk
        messages.success(self.request, "Gallery image deleted successfully.")
        return reverse_lazy("dashboard_property_update", kwargs={"pk": property_pk})


# Inquiry Management Views
class InquiryListView(LoginRequiredMixin, ListView):
    model = Inquiry
    template_name = "dashboard/inquiries/inquiry_list.html"
    context_object_name = "inquiries"
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.profile.user_type == "admin":
            return Inquiry.objects.all().order_by("-created_at")
        elif user.profile.user_type == "agent":
            return Inquiry.objects.filter(property__agent=user).order_by("-created_at")
        else:
            return Inquiry.objects.filter(user=user).order_by("-created_at")


class InquiryCreateAdminView(
    AdminRequiredMixin, CreateView
):  # Renamed to avoid conflict if you have other InquiryCreateView
    model = Inquiry
    form_class = InquiryFormAdmin
    template_name = "dashboard/inquiries/inquiry_form.html"  # Generic form template
    success_url = reverse_lazy("dashboard_inquiries")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Create New Inquiry"
        return context

    def form_valid(self, form):
        messages.success(
            self.request, f"Inquiry for '{form.instance.property.title}' created successfully."
        )
        return super().form_valid(form)


class InquiryDetailView(AdminRequiredMixin, DetailView):
    model = Inquiry
    template_name = "dashboard/inquiries/inquiry_detail.html"
    context_object_name = "inquiry"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Inquiry from {self.object.name}"
        return context


class InquiryUpdateView(AgentRequiredMixin, UpdateView):
    model = Inquiry
    form_class = InquiryFormAdmin
    template_name = "dashboard/inquiries/inquiry_update.html"
    success_url = reverse_lazy("dashboard_inquiries")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = (
            f"Update Inquiry for: {self.object.property.title} (from {self.object.name})"
        )
        return context

    def form_valid(self, form):
        messages.success(self.request, "Inquiry status updated successfully!")
        return super().form_valid(form)


class InquiryDeleteView(AdminRequiredMixin, DeleteView):
    model = Inquiry
    template_name = "dashboard/inquiries/inquiry_confirm_delete.html"
    success_url = reverse_lazy("dashboard_inquiries")
    context_object_name = "inquiry_to_delete"


# Reports Views
class ReportsView(AdminRequiredMixin, TemplateView):
    template_name = "dashboard/reports.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Time periods
        last_month = timezone.now() - timedelta(days=30)
        last_quarter = timezone.now() - timedelta(days=90)
        last_year = timezone.now() - timedelta(days=365)

        # Property stats
        properties = Property.objects.all()
        context["total_properties"] = properties.count()
        context["properties_last_month"] = properties.filter(created_at__gte=last_month).count()
        context["properties_last_quarter"] = properties.filter(created_at__gte=last_quarter).count()
        context["properties_last_year"] = properties.filter(created_at__gte=last_year).count()

        # Inquiry stats
        inquiries = Inquiry.objects.all()
        context["total_inquiries"] = inquiries.count()
        context["inquiries_last_month"] = inquiries.filter(created_at__gte=last_month).count()
        context["inquiries_last_quarter"] = inquiries.filter(created_at__gte=last_quarter).count()
        context["inquiries_last_year"] = inquiries.filter(created_at__gte=last_year).count()

        # User stats
        users = User.objects.all()
        context["total_users"] = users.count()
        context["users_last_month"] = users.filter(date_joined__gte=last_month).count()
        context["users_last_quarter"] = users.filter(date_joined__gte=last_quarter).count()
        context["users_last_year"] = users.filter(date_joined__gte=last_year).count()

        # Property type distribution
        context["property_types"] = PropertyType.objects.annotate(count=Count("property")).order_by(
            "-count"
        )

        # Status distribution
        context["status_distribution"] = {
            "for_sale": properties.filter(status="for_sale").count(),
            "for_rent": properties.filter(status="for_rent").count(),
            "sold": properties.filter(status="sold").count(),
            "rented": properties.filter(status="rented").count(),
        }

        return context
