from django.urls import path
from .views import home
urlpatterns = [path("", home, name="sms_tool_home")]
