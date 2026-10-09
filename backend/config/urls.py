from django.urls import path
from api.views import plan
urlpatterns = [path("api/plan", plan)]
