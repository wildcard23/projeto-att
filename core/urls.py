from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("bolsista/frequencia/", views.bolsista_frequencia, name="bolsista_frequencia"),
    path("bolsista/qr-code/", views.qr_code, name="qr_code"),
    path("bolsista/geolocalizacao/", views.geolocation, name="geolocation"),
    path("coordenador/perfil/", views.coordenador_perfil, name="coordenador_perfil"),
]
