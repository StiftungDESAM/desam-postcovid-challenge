from django.views.generic import TemplateView
class HelloWorldView(TemplateView):
    template_name = "ontology/hello_world.html"
