from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView
from django_filters.views import FilterView

from .forms import InquiryForm, PropertyFilterForm
from .models import Inquiry, Location, Property, PropertyType


class PropertyListView(FilterView):
    model = Property
    template_name = "properties/property_list.html"
    context_object_name = "properties"
    filterset_class = PropertyFilterForm
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["property_types"] = PropertyType.objects.all()
        context["locations"] = Location.objects.all()
        context["filter_form"] = self.filterset.form
        return context


class PropertyDetailView(DetailView):
    model = Property
    template_name = "properties/property_detail.html"
    context_object_name = "property"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inquiry_form"] = InquiryForm()
        context["related_properties"] = Property.objects.filter(
            property_type=self.object.property_type
        ).exclude(id=self.object.id)[:3]
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = InquiryForm(request.POST)

        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.property = self.object
            if request.user.is_authenticated:
                inquiry.user = request.user
            inquiry.save()
            messages.success(
                request, "Your inquiry has been submitted. We'll get back to you soon!"
            )
            return redirect("property_detail", pk=self.object.pk, slug=self.object.slug)

        context = self.get_context_data(object=self.object)
        context["inquiry_form"] = form
        return self.render_to_response(context)


class PropertySearchView(ListView):
    model = Property
    template_name = "properties/property_search.html"
    context_object_name = "properties"
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q")

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(location__name__icontains=query)
                | Q(location__city__icontains=query)
                | Q(address__icontains=query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        return context
