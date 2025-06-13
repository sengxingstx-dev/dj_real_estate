from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView
from django_filters.views import FilterView

from .forms import BookingForm, InquiryForm, PropertyFilterForm
from .models import Location, Property, PropertyType


class PropertyListView(FilterView):
    model = Property
    template_name = "properties/property_list.html"
    context_object_name = "properties"
    filterset_class = PropertyFilterForm
    paginate_by = 9

    def get_queryset(self):
        # Start with the default queryset from FilterView
        queryset = super().get_queryset()
        # Exclude properties that are sold or rented
        return queryset.exclude(status__in=["sold", "rented"])

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
        # Initialize forms if not already in context (e.g., from a failed POST)
        if "inquiry_form" not in context:
            context["inquiry_form"] = InquiryForm()
        if "booking_form" not in context:
            initial_booking_data = {}
            if self.request.user.is_authenticated:
                initial_booking_data = {
                    "name": self.request.user.get_full_name() or self.request.user.username,
                    "email": self.request.user.email,
                    "phone": (
                        self.request.user.profile.phone
                        if hasattr(self.request.user, "profile")
                        else ""
                    ),
                }
            context["booking_form"] = BookingForm(initial=initial_booking_data)

        context["related_properties"] = Property.objects.filter(
            property_type=self.object.property_type
        ).exclude(id=self.object.id)[:3]
        context["qr_code_image_url"] = "img/qr_payment.jpg"  # Placeholder for your QR code image
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # form = InquiryForm(request.POST)
        context = {}
        form_type = request.POST.get("form_type")

        # if form.is_valid():
        #     inquiry = form.save(commit=False)
        #     inquiry.property = self.object
        #     if request.user.is_authenticated:
        #         inquiry.user = request.user
        #     inquiry.save()
        #     messages.success(
        #         request, "Your inquiry has been submitted. We'll get back to you soon!"
        #     )
        #     return redirect("property_detail", pk=self.object.pk, slug=self.object.slug)

        if form_type == "inquiry":
            inquiry_form = InquiryForm(request.POST)
            if inquiry_form.is_valid():
                inquiry = inquiry_form.save(commit=False)
                inquiry.property = self.object
                if request.user.is_authenticated:
                    inquiry.user = request.user
                inquiry.save()
                messages.success(
                    request, "Your inquiry has been submitted. We'll get back to you soon!"
                )
                return redirect("property_detail", pk=self.object.pk, slug=self.object.slug)
            else:
                context["inquiry_form"] = inquiry_form  # Pass failing form back

        elif form_type == "booking":
            if not request.user.is_authenticated:
                messages.error(request, "You must be logged in to make a booking.")
                # Optionally redirect to login: return redirect(f"{reverse_lazy('login')}?next={request.path}")
                return self.render_to_response(self.get_context_data())

            booking_form = BookingForm(request.POST, request.FILES)
            if booking_form.is_valid():
                booking = booking_form.save(commit=False)
                booking.property = self.object
                booking.user = request.user  # User must be logged in
                booking.save()
                messages.success(
                    request, "Your booking request and payment slip have been submitted for review!"
                )
                return redirect("property_detail", pk=self.object.pk, slug=self.object.slug)
            else:
                context["booking_form"] = booking_form  # Pass failing form back

        # context = self.get_context_data(object=self.object)
        # context["inquiry_form"] = form
        # return self.render_to_response(context)

        return self.render_to_response(self.get_context_data(**context))


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
