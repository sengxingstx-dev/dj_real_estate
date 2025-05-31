from django.urls import path

from . import views

urlpatterns = [
    path("", views.DashboardHomeView.as_view(), name="dashboard_home"),
    # User Management URLs
    path("users/", views.UserListView.as_view(), name="dashboard_users"),
    path("users/create/", views.UserCreateView.as_view(), name="dashboard_user_create"),
    path("users/<int:pk>/", views.UserDetailView.as_view(), name="dashboard_user_detail"),
    path("users/<int:pk>/update/", views.UserUpdateView.as_view(), name="dashboard_user_update"),
    path("users/<int:pk>/delete/", views.UserDeleteView.as_view(), name="dashboard_user_delete"),
    # Property Type Management URLs
    path("property-types/", views.PropertyTypeListView.as_view(), name="dashboard_property_types"),
    path(
        "property-types/create/",
        views.PropertyTypeCreateView.as_view(),
        name="dashboard_property_type_create",
    ),
    path(
        "property-types/<int:pk>/update/",
        views.PropertyTypeUpdateView.as_view(),
        name="dashboard_property_type_update",
    ),
    path(
        "property-types/<int:pk>/delete/",
        views.PropertyTypeDeleteView.as_view(),
        name="dashboard_property_type_delete",
    ),
    # Location Management URLs
    path("locations/", views.LocationListView.as_view(), name="dashboard_locations"),
    path("locations/create/", views.LocationCreateView.as_view(), name="dashboard_location_create"),
    path(
        "locations/<int:pk>/update/",
        views.LocationUpdateView.as_view(),
        name="dashboard_location_update",
    ),
    path(
        "locations/<int:pk>/delete/",
        views.LocationDeleteView.as_view(),
        name="dashboard_location_delete",
    ),
    # Feature Management URLs
    path("features/", views.FeatureListView.as_view(), name="dashboard_features"),
    path("features/create/", views.FeatureCreateView.as_view(), name="dashboard_feature_create"),
    path(
        "inquiries/<int:pk>/",
        views.InquiryDetailView.as_view(),
        name="dashboard_inquiry_detail",
    ),
    path(
        "features/<int:pk>/update/",
        views.FeatureUpdateView.as_view(),
        name="dashboard_feature_update",
    ),
    path(
        "features/<int:pk>/delete/",
        views.FeatureDeleteView.as_view(),
        name="dashboard_feature_delete",
    ),
    # Property Management URLs
    path("properties/", views.PropertyListAdminView.as_view(), name="dashboard_properties"),
    path(
        "properties/create/",
        views.PropertyCreateAdminView.as_view(),
        name="dashboard_property_create",
    ),
    path(
        "properties/<int:pk>/update/",
        views.PropertyUpdateAdminView.as_view(),
        name="dashboard_property_update",
    ),
    path(
        "properties/<int:pk>/delete/",
        views.PropertyDeleteAdminView.as_view(),
        name="dashboard_property_delete",
    ),
    # Property Image Management URLs (nested conceptually, but flat for simplicity here)
    path(
        "properties/<int:property_pk>/images/add/",
        views.PropertyImageCreateAdminView.as_view(),
        name="dashboard_property_image_add",
    ),
    path(
        "property-images/<int:pk>/update/",
        views.PropertyImageUpdateAdminView.as_view(),
        name="dashboard_property_image_update",
    ),
    path(
        "property-images/<int:pk>/delete/",
        views.PropertyImageDeleteAdminView.as_view(),
        name="dashboard_property_image_delete",
    ),
    # Inquiry Management URLs
    path("inquiries/", views.InquiryListView.as_view(), name="dashboard_inquiries"),
    path(
        "inquiries/create/", views.InquiryCreateAdminView.as_view(), name="dashboard_inquiry_create"
    ),
    path(
        "inquiries/<int:pk>/update/",
        views.InquiryUpdateView.as_view(),
        name="dashboard_inquiry_update",
    ),
    path(
        "inquiries/<int:pk>/delete/",
        views.InquiryDeleteView.as_view(),
        name="dashboard_inquiry_delete",
    ),
    # Reports
    path("reports/", views.ReportsView.as_view(), name="dashboard_reports"),
]
