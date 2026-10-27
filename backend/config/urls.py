from django.urls import path
from trips import views

urlpatterns = [
    path("api/health/", views.health),
    path("api/locations/search/", views.locations),
    path("api/routes/analyze/", views.analyze),
]
