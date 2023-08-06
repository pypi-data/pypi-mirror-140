from django.urls import path, register_converter

from . import views

app_name = 'spa'


class SPAFilenameConverter:
    regex = r'[\w.]+\.(?:json|jpe?g|png|txt|ico)'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(SPAFilenameConverter, 'spa_filename')

urlpatterns = [
    path('static/<path:resource>', views.redirect_static),
    path('<spa_filename:filename>', views.serve_file),
    path('<path:resource>/', views.serve_file, {'filename': 'index.html'}, name='path'),
    path('', views.serve_file, {'filename': 'index.html'}, name='home'),
]
