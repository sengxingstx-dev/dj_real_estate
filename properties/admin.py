from django.contrib import admin

from .models import Feature, Inquiry, Location, Property, PropertyImage, PropertyType


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 3


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "property_type",
        "price",
        "status",
        "location",
        "agent",
        "is_featured",
        "created_at",
    )
    list_filter = ("status", "property_type", "is_featured", "agent")
    search_fields = ("title", "description", "address")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PropertyImageInline]
    list_editable = ("status", "is_featured")
    date_hierarchy = "created_at"


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "state", "zip_code")
    search_fields = ("name", "city", "state", "zip_code")


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("name", "icon")
    search_fields = ("name",)


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "property", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "message")
    list_editable = ("status",)
