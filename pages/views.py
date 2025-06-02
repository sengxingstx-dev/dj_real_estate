from django.views.generic import TemplateView

from accounts.models import UserProfile
from properties.models import Location, Property, PropertyType


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_properties"] = Property.objects.filter(is_featured=True)[:6]
        context["latest_properties"] = Property.objects.all().order_by("-created_at")[:8]
        context["property_types"] = PropertyType.objects.all()[:6]
        context["locations"] = Location.objects.all()[:6]
        context["agents"] = UserProfile.objects.filter(user_type="agent")[:4]
        return context


class AboutView(TemplateView):
    template_name = "pages/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["agents"] = UserProfile.objects.filter(user_type="agent")
        return context


class ContactView(TemplateView):
    template_name = "pages/contact.html"
