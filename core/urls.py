from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("bolsista/frequencia/", views.bolsista_frequencia, name="bolsista_frequencia"),
    path("bolsista/qr-code/", views.qr_code, name="qr_code"),
    path("bolsista/geolocalizacao/", views.geolocation, name="geolocation"),
    path("coordenador/perfil/", views.coordenador_perfil, name="coordenador_perfil"),
    path("api/bolsista/", views.bolsista_api, name="bolsista_api"),
    path("api/acoes/", views.acoes_api, name="acoes_api"),
    path("api/registrar/", views.registrar_presenca, name="registrar_presenca"),
    path("api/confirmar/<int:pk>/", views.confirmar_presenca, name="confirmar_presenca"),
    path("api/suap-sync/", views.suap_sync, name="suap_sync"),
    path("api/suap/auth/", views.suap_auth, name="suap_auth"),
    path("api/dashboard/", views.dashboard_api, name="dashboard_api"),
    path("api/orientador-summary/", views.orientador_summary, name="orientador_summary"),
    path("api/audit-logs/", views.audit_logs, name="audit_logs"),
    path("api/tasks/", views.tasks_list, name="tasks_list"),
    path("api/tasks/<int:pk>/move/", views.task_move, name="task_move"),
    path("api/tasks/<int:pk>/associate/", views.task_associate, name="task_associate"),
]
