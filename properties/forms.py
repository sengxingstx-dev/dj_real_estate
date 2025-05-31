import django_filters
from django import forms

from .models import Inquiry, Location, Property, PropertyType


class PropertyFilterForm(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte", label="ລາຄາຕ່ຳສຸດ")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte", label="ລາຄາສູງສຸດ")
    property_type = django_filters.ModelChoiceFilter(
        queryset=PropertyType.objects.all(),
        widget=forms.Select(attrs={"class": "input"}),
        label="ປະເພດອະສັງຫາ",
    )
    location = django_filters.ModelChoiceFilter(
        queryset=Location.objects.all(),
        widget=forms.Select(attrs={"class": "input"}),
        label="ສະຖານທີ່",
    )
    bedrooms_min = django_filters.NumberFilter(
        field_name="bedrooms", lookup_expr="gte", label="ຈຳນວນຫ້ອງນອນ (ຕ່ຳສຸດ)"
    )
    bathrooms_min = django_filters.NumberFilter(
        field_name="bathrooms", lookup_expr="gte", label="ຈຳນວນຫ້ອງນ້ຳ (ຕ່ຳສຸດ)"
    )
    status = django_filters.ChoiceFilter(
        choices=Property.STATUS_CHOICES, widget=forms.Select(attrs={"class": "input"})
    )

    class Meta:
        model = Property
        fields = [
            "property_type",
            "location",
            "status",
            "price_min",
            "price_max",
            "bedrooms_min",
            "bathrooms_min",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set labels for fields that don't have them set directly at declaration
        self.filters["status"].label = "ສະຖານະ"

        # Apply 'input' class to NumberInput widgets if not already applied by widget declaration
        for field_name, field in self.filters.items():
            if isinstance(field.field.widget, forms.NumberInput):
                field.field.widget.attrs.update({"class": "input"})
        # Make fields not required for filtering
        for field_name in self.Meta.fields:
            if field_name in self.filters:
                self.filters[field_name].field.required = False


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ["name", "email", "phone", "message"]
        labels = {
            "name": "ຊື່ ແລະ ນາມສະກຸນ",
            "email": "ອີເມວ",
            "phone": "ເບີໂທລະສັບ",
            "message": "ຂໍ້ຄວາມ",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "input", "placeholder": "ປ້ອນຊື່ ແລະ ນາມສະກຸນ"}),
            "email": forms.EmailInput(attrs={"class": "input", "placeholder": "ປ້ອນອີເມວຂອງທ່ານ"}),
            "phone": forms.TextInput(attrs={"class": "input", "placeholder": "ປ້ອນເບີໂທລະສັບ"}),
            "message": forms.Textarea(
                attrs={"class": "input", "rows": 4, "placeholder": "ຂຽນຂໍ້ຄວາມຂອງທ່ານທີ່ນີ້..."}
            ),
        }
