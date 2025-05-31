from django import forms
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q

from accounts.models import UserProfile
from properties.models import (
    Feature,
    Inquiry,
    Location,
    Property,
    PropertyImage,
    PropertyType,
)


class CustomUserCreationFormAdmin(DjangoUserCreationForm):
    email = forms.EmailField(required=True, label="ອີເມວ")
    first_name = forms.CharField(
        max_length=150, required=False, label="ຊື່"
    )  # Match User model max_length
    last_name = forms.CharField(
        max_length=150, required=False, label="ນາມສະກຸນ"
    )  # Match User model max_length
    user_type = forms.ChoiceField(choices=UserProfile.USER_TYPES, required=True, label="ປະເພດຜູ້ໃຊ້")
    is_staff = forms.BooleanField(
        required=False,
        label="ສະຖານະພະນັກງານ",
        help_text="Designates whether the user can log into this admin site.",
    )

    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name", "is_staff")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "input"})  # Assuming 'input' is your CSS class
        self.fields["password1"].widget.attrs.update({"class": "input"})
        self.fields["password2"].widget.attrs.update({"class": "input"})
        self.fields["username"].label = "ຊື່ຜູ້ໃຊ້"
        self.fields["password1"].label = "ລະຫັດຜ່ານ"
        self.fields["password2"].label = "ຢືນຢັນລະຫັດຜ່ານ"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.is_staff = self.cleaned_data.get("is_staff", False)

        if commit:
            user.save()
            # UserProfile is created by a signal in accounts/models.py
            # Now, set the user_type for the newly created profile
            if hasattr(user, "profile"):
                user.profile.user_type = self.cleaned_data["user_type"]
                user.profile.save()
        return user


class UserFormAdmin(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "is_active", "is_staff")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["readonly"] = True
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "input"})

        self.fields["username"].label = "ຊື່ຜູ້ໃຊ້"
        self.fields["email"].label = "ອີເມວ"
        self.fields["first_name"].label = "ຊື່"
        self.fields["last_name"].label = "ນາມສະກຸນ"
        self.fields["is_active"].label = "ເປີດໃຊ້ງານ"
        self.fields["is_staff"].label = "ສະຖານະພະນັກງານ"


class UserProfileFormAdmin(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = (
            "avatar",
            "phone",
            "address",
            "bio",
            "user_type",
            "facebook",
            "twitter",
            "instagram",
            "linkedin",
        )
        widgets = {
            "bio": forms.Textarea(
                attrs={"rows": 3, "class": "textarea"}
            ),  # Assuming 'textarea' is your CSS class
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Apply 'input' class, but 'bio' already has 'textarea' from widget
            if field_name != "bio":
                field.widget.attrs.update({"class": "input"})
            # Ensure avatar field also gets the class if it's a ClearableFileInput
            if isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.update({"class": "input"})

        self.fields["avatar"].label = "ຮູບໂປຣໄຟລ໌"
        self.fields["phone"].label = "ເບີໂທລະສັບ"
        self.fields["address"].label = "ທີ່ຢູ່"
        # self.fields["bio"].label = "ກ່ຽວກັບຂ້ອຍ"
        self.fields["user_type"].label = "ປະເພດຜູ້ໃຊ້"
        # self.fields["facebook"].label = "ເຟສບຸກ"
        # self.fields["twitter"].label = "ທະວິດເຕີ"
        # self.fields["instagram"].label = "ອິນສະຕາແກຣມ"
        # self.fields["linkedin"].label = "ລິ້ງອິນ"


class PropertyTypeFormAdmin(forms.ModelForm):
    class Meta:
        model = PropertyType
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3, "class": "textarea"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "input"})
        self.fields["name"].label = "ຊື່ປະເພດ"
        self.fields["description"].label = "ຄຳອະທິບາຍ"


class LocationFormAdmin(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["name", "city", "state", "zip_code", "latitude", "longitude"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.NumberInput) or isinstance(
                field.widget, forms.TextInput
            ):
                field.widget.attrs.update({"class": "input"})
        # Specific styling for potentially smaller number inputs if needed
        # self.fields['latitude'].widget.attrs.update({"class": "input input-sm"})
        # self.fields['longitude'].widget.attrs.update({"class": "input input-sm"})
        self.fields["name"].label = "ຊື່ສະຖານທີ່"
        self.fields["city"].label = "ເມືອງ"
        self.fields["state"].label = "ແຂວງ"
        self.fields["zip_code"].label = "ລະຫັດໄປສະນີ"
        self.fields["latitude"].label = "ເສັ້ນແວງທີ"
        self.fields["longitude"].label = "ເສັ້ນຂະໜານທີ"


class FeatureFormAdmin(forms.ModelForm):
    class Meta:
        model = Feature
        fields = ["name", "icon"]
        help_texts = {
            "icon": 'Enter a valid FlowBite icon name (e.g., "home-outline", "check-circle"). Refer to FlowBite documentation for icon names.'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "input"})
        self.fields["icon"].widget.attrs.update({"class": "input"})
        self.fields["name"].label = "ຊື່ຄຸນສົມບັດ"
        self.fields["icon"].label = "ໄອຄອນ"


class PropertyFormAdmin(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            "title",
            "property_type",
            "description",
            "price",
            "status",
            "area",
            "bedrooms",
            "bathrooms",
            "garages",
            "location",
            "address",
            "features",
            "main_image",
            "agent",  # Admins can assign agents
            "is_featured",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5, "class": "textarea"}),
            "features": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)  # Get user from view
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field_name not in [
                "features",
                "is_featured",
            ]:  # CheckboxSelectMultiple and BooleanField don't need 'input'
                if (
                    not isinstance(field.widget, forms.Textarea)
                    and not isinstance(field.widget, forms.CheckboxSelectMultiple)
                    and not isinstance(field.widget, forms.ClearableFileInput)
                ):
                    field.widget.attrs.update({"class": "input"})
                elif isinstance(field.widget, forms.ClearableFileInput):  # For main_image
                    field.widget.attrs.update({"class": "input"})

        # If the user is an agent and not staff, pre-select and disable the agent field
        if self.user and self.user.profile.user_type == "agent" and not self.user.is_staff:
            self.fields["agent"].queryset = User.objects.filter(pk=self.user.pk)
            self.fields["agent"].initial = self.user
            self.fields["agent"].disabled = True
        elif self.user and self.user.is_staff:  # Staff/Admin can choose any agent
            self.fields["agent"].queryset = User.objects.filter(
                Q(profile__user_type="agent") | Q(is_staff=True)  # Allow staff or agents
            ).distinct()
        else:  # Should not happen if views are protected, but as a fallback
            self.fields["agent"].queryset = User.objects.none()

        self.fields["title"].label = "ຫົວຂໍ້"
        self.fields["property_type"].label = "ປະເພດອະສັງຫາ"
        self.fields["description"].label = "ຄຳອະທິບາຍ"
        self.fields["price"].label = "ລາຄາ"
        self.fields["status"].label = "ສະຖານະ"
        self.fields["area"].label = "ເນື້ອທີ່ (ຕາແມັດ)"
        self.fields["bedrooms"].label = "ຈຳນວນຫ້ອງນອນ"
        self.fields["bathrooms"].label = "ຈຳນວນຫ້ອງນ້ຳ"
        self.fields["garages"].label = "ຈຳນວນບ່ອນຈອດລົດ"
        self.fields["location"].label = "ສະຖານທີ່"
        self.fields["address"].label = "ທີ່ຢູ່ລະອຽດ"
        self.fields["features"].label = "ຄຸນສົມບັດເພີ່ມເຕີມ"
        self.fields["main_image"].label = "ຮູບໜ້າປົກ"
        self.fields["agent"].label = "ຕົວແທນ"
        self.fields["is_featured"].label = "ສະແດງເປັນລາຍການແນະນຳ"


class PropertyImageFormAdmin(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ["image", "caption", "is_primary", "order"]
        # 'property' field will be set in the view

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].widget.attrs.update(
            {"class": "input"}
        )  # Assuming 'input' is your CSS class for file inputs
        self.fields["caption"].widget.attrs.update({"class": "input"})
        # BooleanField (is_primary) and NumberInput (order) might not need 'input' class or have specific ones
        self.fields["order"].widget.attrs.update(
            {"class": "input w-20"}
        )  # Example: smaller width for order
        # is_primary is a checkbox, usually styled by Tailwind directly
        self.fields["image"].label = "ຮູບພາບ"
        self.fields["caption"].label = "ຄຳບັນຍາຍຮູບ"
        self.fields["is_primary"].label = "ຕັ້ງເປັນຮູບຫຼັກ"
        self.fields["order"].label = "ລຳດັບການສະແດງ"


class InquiryFormAdmin(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ["property", "name", "email", "phone", "message", "status", "user"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4, "class": "textarea"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != "message":  # message already has textarea class
                field.widget.attrs.update({"class": "input"})

        # Make property and user fields read-only if instance exists, as they are usually set contextually
        if self.instance and self.instance.pk:
            # self.fields["property"].widget.attrs[
            #     "disabled"
            # ] = True  # Or readonly, but disabled is clearer for select
            # self.fields["user"].widget.attrs["disabled"] = True
            self.fields["property"].disabled = True  # Set the field itself as disabled
            self.fields["user"].disabled = True  # Set the field itself as disabled

        self.fields["property"].label = "ອະສັງຫາ"
        self.fields["name"].label = "ຊື່ຜູ້ສອບຖາມ"
        self.fields["email"].label = "ອີເມວ"
        self.fields["phone"].label = "ເບີໂທລະສັບ"
        self.fields["message"].label = "ຂໍ້ຄວາມ"
        self.fields["status"].label = "ສະຖານະການສອບຖາມ"
        self.fields["user"].label = "ຜູ້ໃຊ້ (ຖ້າມີ)"
