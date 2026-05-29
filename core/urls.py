from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("bolsista/frequencia/", views.bolsista_frequencia, name="bolsista_frequencia"),
    path("coordenador/perfil/", views.coordenador_perfil, name="coordenador_perfil"),
]
