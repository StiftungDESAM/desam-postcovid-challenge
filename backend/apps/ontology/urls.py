from django.urls import path
from . import views

app_name = 'ontology'

urlpatterns = [
    path('hello-world/', views.HelloWorldView.as_view(), name = 'hello-world'),
]