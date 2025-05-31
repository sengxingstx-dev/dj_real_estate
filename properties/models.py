from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class PropertyType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Property Types"

    def __str__(self):
        return f"{self.name}"


class Location(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.name}, {self.city}"


class Feature(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="FlowBite icon name")

    def __str__(self):
        return f"{self.name}"


class Property(models.Model):
    STATUS_CHOICES = (
        ("for_sale", "For Sale"),
        ("for_rent", "For Rent"),
        ("sold", "Sold"),
        ("rented", "Rented"),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    property_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="for_sale")
    area = models.PositiveIntegerField(help_text="Area in square feet/meters")
    bedrooms = models.PositiveIntegerField(null=True, blank=True)
    bathrooms = models.PositiveIntegerField(null=True, blank=True)
    garages = models.PositiveIntegerField(null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    features = models.ManyToManyField(Feature, blank=True)

    # Media
    main_image = models.ImageField(upload_to="properties")

    # Metadata
    agent = models.ForeignKey(User, related_name="properties", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Properties"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("property_detail", kwargs={"pk": self.pk, "slug": self.slug})


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="properties")
    caption = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Image for {self.property.title}"


class Inquiry(models.Model):
    STATUS_CHOICES = (
        ("new", "New"),
        ("in_progress", "In Progress"),
        ("closed", "Closed"),
    )

    property = models.ForeignKey(Property, related_name="inquiries", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Inquiries"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Inquiry from {self.name} for {self.property.title}"
