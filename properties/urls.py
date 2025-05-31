from django.urls import path

from . import views

urlpatterns = [
    path("", views.PropertyListView.as_view(), name="property_list"),
    path("<int:pk>/<slug:slug>/", views.PropertyDetailView.as_view(), name="property_detail"),
    path("search/", views.PropertySearchView.as_view(), name="property_search"),
]
