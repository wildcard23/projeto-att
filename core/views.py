from django.shortcuts import render


def home(request):
    return render(request, "core/home.html")


def bolsista_frequencia(request):
    context = {
        "bolsista": {
            "nome": "Ana Beatriz Silva",
            "curso": "Engenharia de Software",
            "programa": "Bolsa Iniciação Científica",
            "supervisor": "Prof. Dr. Carlos Pereira",
            "email": "ana.silva@ifrn.edu.br",
        },
        "frequencia": {
            "presente": 12,
            "faltas": 3,
            "carga_horaria": 15,
            "registros": 9,
            "percentual": 80,
            "status": "Em dia",
        },
        "registros": [
            {"data": "26/05/2026", "atividade": "Atendimento acadêmico", "metodo": "QR Code", "status": "Presente", "status_classe": "presente"},
            {"data": "24/05/2026", "atividade": "Preparação de relatório", "metodo": "Geofencing", "status": "Presente", "status_classe": "presente"},
            {"data": "22/05/2026", "atividade": "Reunião de orientação", "metodo": "QR Code", "status": "Pendente", "status_classe": "pendente"},
            {"data": "20/05/2026", "atividade": "Pesquisa de campo", "metodo": "Geofencing", "status": "Falta", "status_classe": "falta"},
        ],
    }
    return render(request, "core/bolsista_frequencia.html", context)


def coordenador_perfil(request):
    context = {
        "coordenador": {
            "nome": "Prof. Dr. Carlos Pereira",
            "cargo": "Coordenador de Bolsas",
            "departamento": "Engenharia de Software",
            "email": "carlos.pereira@ifrn.edu.br",
            "telefone": "(84) 99999-1234",
            "bolsistas_supervisionados": 18,
            "registros_pendentes": 3,
            "integracao_suap": "Ativa",
            "suap_status": "Online",
            "suap_status_texto": "Integração com SUAP está atualizada e funcionando.",
            "alertas": 2,
            "bolsistas_recentes": [
                {"nome": "Ana Beatriz Silva", "horas": "12h", "status": "Em dia", "status_classe": "presente"},
                {"nome": "Bruno Santos", "horas": "10h", "status": "Pendente", "status_classe": "pendente"},
                {"nome": "Carla Nunes", "horas": "14h", "status": "Em dia", "status_classe": "presente"},
            ],
        }
    }
    return render(request, "core/coordenador_perfil.html", context)
