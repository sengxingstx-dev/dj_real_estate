from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "ຊື່ຜູ້ໃຊ້"
        self.fields["username"].widget.attrs.update(
            {"class": "input", "placeholder": "ປ້ອນຊື່ຜູ້ໃຊ້ຂອງທ່ານ"}
        )
        self.fields["password"].label = "ລະຫັດຜ່ານ"
        self.fields["password"].widget.attrs.update({"class": "input", "placeholder": "ປ້ອນລະຫັດຜ່ານ"})


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="ອີເມວ")
    first_name = forms.CharField(max_length=30, required=True, label="ຊື່")
    last_name = forms.CharField(max_length=30, required=True, label="ນາມສະກຸນ")

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "input"})

        self.fields["username"].label = "ຊື່ຜູ້ໃຊ້"
        self.fields["password1"].label = "ລະຫັດຜ່ານ"
        self.fields["password2"].label = "ຢືນຢັນລະຫັດຜ່ານ"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, label="ເບີໂທລະສັບ")

    class Meta:
        model = UserProfile
        fields = (
            "avatar",
            "phone",
            "address",
            "bio",
            "facebook",
            "twitter",
            "instagram",
            "linkedin",
        )
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "address": forms.TextInput(attrs={"placeholder": "ຕົວຢ່າງ: ບ້ານ, ເມືອງ"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "input"})

        if self.instance and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["email"].initial = self.instance.user.email

        self.fields["first_name"].label = "ຊື່"
        self.fields["last_name"].label = "ນາມສະກຸນ"
        self.fields["email"].label = "ອີເມວ"
        self.fields["address"].label = "ທີ່ຢູ່ປັດຈຸບັນ"
        self.fields["bio"].label = "ກ່ຽວກັບຂ້ອຍ"
