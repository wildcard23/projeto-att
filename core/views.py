import base64
from io import BytesIO

from django.http import JsonResponse
from django.shortcuts import render

import qrcode
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
import json

from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone as dj_timezone
from .models import Frequency, Location, Justification
from .models import Task, SuapToken, AuditLog
import math
import requests
from django.contrib.auth import authenticate
from functools import wraps


def ensure_suap_token():
    """Return a valid SuapToken or None. Try refresh, then client_credentials if available."""
    token = None
    try:
        token = SuapToken.objects.order_by('-created_at').first()
    except Exception:
        token = None

    # if token exists and valid -> return
    if token and token.is_valid():
        return token

    token_url = getattr(settings, 'SUAP_TOKEN_URL', None) or (getattr(settings, 'SUAP_API_URL', None).rstrip('/') + '/o/token/' if getattr(settings, 'SUAP_API_URL', None) else None)
    client_id = getattr(settings, 'SUAP_CLIENT_ID', None)
    client_secret = getattr(settings, 'SUAP_CLIENT_SECRET', None)

    # try refresh_token
    if token and token.refresh_token and token_url:
        try:
            resp = requests.post(token_url, data={
                'grant_type': 'refresh_token',
                'refresh_token': token.refresh_token,
            }, auth=(client_id, client_secret) if client_id and client_secret else None, timeout=8)
            if resp.status_code in (200, 201):
                data = resp.json()
                access = data.get('access') or data.get('access_token') or data.get('token')
                refresh = data.get('refresh') or data.get('refresh_token')
                token_type = data.get('token_type')
                scope = data.get('scope')
                expires_in = data.get('expires_in')
                expires_at = None
                if expires_in:
                    expires_at = dj_timezone.now() + dj_timezone.timedelta(seconds=int(expires_in))
                new = SuapToken.objects.create(
                    access_token=access or '', refresh_token=refresh or None,
                    token_type=token_type or None, scope=scope or None, expires_at=expires_at
                )
                return new
        except Exception:
            pass

    # try client_credentials
    if client_id and client_secret and token_url:
        try:
            resp = requests.post(token_url, data={'grant_type': 'client_credentials'}, auth=(client_id, client_secret), timeout=8)
            if resp.status_code in (200, 201):
                data = resp.json()
                access = data.get('access') or data.get('access_token') or data.get('token')
                refresh = data.get('refresh') or data.get('refresh_token')
                token_type = data.get('token_type')
                scope = data.get('scope')
                expires_in = data.get('expires_in')
                expires_at = None
                if expires_in:
                    expires_at = dj_timezone.now() + dj_timezone.timedelta(seconds=int(expires_in))
                new = SuapToken.objects.create(
                    access_token=access or '', refresh_token=refresh or None,
                    token_type=token_type or None, scope=scope or None, expires_at=expires_at
                )
                return new
        except Exception:
            pass

    return token


def get_remote_addr(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '') or ''


def log_audit(request, user, auth_type, detail=''):
    AuditLog.objects.create(
        path=request.path,
        method=request.method,
        user=user,
        auth_type=auth_type,
        remote_addr=get_remote_addr(request),
        detail=detail,
    )


def require_staff(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        # if already authenticated via session
        user = getattr(request, 'user', None)
        if user and getattr(user, 'is_authenticated', False) and getattr(user, 'is_staff', False):
            log_audit(request, user, 'session')
            return view_func(request, *args, **kwargs)

        # try HTTP Basic auth
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Basic '):
            try:
                payload = auth_header.split(' ', 1)[1].strip()
                decoded = base64.b64decode(payload).decode()
                username, password = decoded.split(':', 1)
                user = authenticate(username=username, password=password)
                if user and user.is_staff:
                    request.user = user
                    log_audit(request, user, 'basic_auth')
                    return view_func(request, *args, **kwargs)
            except Exception as exc:
                log_audit(request, None, 'basic_auth_failed', str(exc))

        # try API key
        from django.conf import settings as _settings
        api_key = _settings.SUAP_API_KEY
        if api_key:
            # header X-API-KEY
            provided = request.META.get('HTTP_X_API_KEY') or ''
            # or Authorization: ApiKey <key>
            if not provided and auth_header.startswith('ApiKey '):
                provided = auth_header.split(' ', 1)[1].strip()
            if provided and provided == api_key:
                log_audit(request, None, 'api_key')
                return view_func(request, *args, **kwargs)
            log_audit(request, None, 'api_key_failed', f'provided={provided}')

        log_audit(request, user if user and user.is_authenticated else None, 'unauthorized')
        return JsonResponse({'error': 'unauthorized'}, status=401)
    return _wrapped


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


def qr_code(request):
    qr_payload = "https://ifrn.edu.br/"
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(qr_payload)
    qr.make(fit=True)

    image = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    context = {
        "qr_code_data": qr_base64,
        "qr_payload": qr_payload,
    }
    return render(request, "core/qr_code.html", context)


def geolocation(request):
    if request.method == "POST":
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        accuracy = request.POST.get("accuracy")

        response_data = {
            "status": "success",
            "message": "Localização registrada com sucesso.",
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": accuracy,
        }
        return JsonResponse(response_data)

    return render(request, "core/geolocation.html")


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


def bolsista_api(request):
    data = {
        "bolsista": {
            "nome": "Ana Beatriz Silva",
            "curso": "Engenharia de Software",
            "programa": "Bolsa Iniciação Científica",
            "supervisor": "Prof. Dr. Carlos Pereira",
            "email": "ana.silva@ifrn.edu.br",
            "presente": 12,
            "faltas": 3,
            "carga_horaria": 15,
            "registros": 9,
            "percentual": 80,
            "status": "Em dia",
        }
    }
    return JsonResponse(data)


def acoes_api(request):
    data = {
        "acoes": [
            {
                "title": "Abrir perfil do coordenador",
                "description": "Visualize a página do coordenador no backend Django.",
                "url": "http://localhost:8000/coordenador/perfil/",
            },
            {
                "title": "Abrir frequência do bolsista",
                "description": "Veja a página de frequência com dados do bolsista.",
                "url": "http://localhost:8000/bolsista/frequencia/",
            },
            {
                "title": "Abrir QR Code",
                "description": "Veja o QR Code gerado pelo backend Django.",
                "url": "http://localhost:8000/bolsista/qr-code/",
            },
        ]
    }
    return JsonResponse(data)


def haversine(lat1, lon1, lat2, lon2):
    # distância em metros
    R = 6371000
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    dphi = math.radians(float(lat2) - float(lat1))
    dlambda = math.radians(float(lon2) - float(lon1))
    a = math.sin(dphi/2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@csrf_exempt
def registrar_presenca(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    payload = json.loads(request.body.decode())
    username = payload.get("username")
    method = payload.get("method")  # manual, qr, geofence
    lat = payload.get("latitude")
    lon = payload.get("longitude")
    task_id = payload.get("task_id")

    User = get_user_model()
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"error": "user not found"}, status=404)

    location = None
    if method == "geofence" and lat and lon:
        # verificar se dentro de alguma Location
        for loc in Location.objects.all():
            dist = haversine(lat, lon, loc.latitude, loc.longitude)
            if dist <= loc.radius_meters:
                location = loc
                break
        if location is None:
            return JsonResponse({"status": "outside_geofence"}, status=403)

    freq = Frequency.objects.create(
        user=user,
        method=method or "manual",
        location=location,
        latitude=lat if lat else None,
        longitude=lon if lon else None,
        present=True,
    )

    return JsonResponse({"status": "ok", "id": freq.id})


@csrf_exempt
def confirmar_presenca(request, pk):
    freq = get_object_or_404(Frequency, pk=pk)
    if request.method == "POST":
        freq.confirmed = True
        freq.save()
        return JsonResponse({"status": "confirmed", "id": freq.id})
    return JsonResponse({"error": "POST required"}, status=400)


@csrf_exempt
@require_staff
def suap_sync(request):
    # Endpoint para sincronizar uma frequência com SUAP (simulado)
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)
    payload = json.loads(request.body.decode())
    # if frequency_id provided, sync single; otherwise sync all unsynced
    freq_id = payload.get("frequency_id")

    # ensure we have a valid token (refresh or client_credentials)
    token = ensure_suap_token()
    headers = {}
    if token and token.access_token:
        headers['Authorization'] = f"Bearer {token.access_token}"

    def do_sync(freq: Frequency):
        url = getattr(settings, 'SUAP_API_URL', None)
        if not url:
            # simulation
            try:
                # pretend success
                freq.suap_synced = True
                freq.save()
                return True, None
            except Exception as exc:
                return False, str(exc)

        try:
            resp = requests.post(f"{url.rstrip('/')}/api/sync/", json={
                "username": freq.user.username,
                "timestamp": freq.timestamp.isoformat(),
                "present": freq.present,
            }, headers=headers, timeout=8)
            if resp.status_code in (200, 201):
                freq.suap_synced = True
                freq.save()
                return True, None
            return False, f"status:{resp.status_code} body:{resp.text}"
        except Exception as e:
            return False, str(e)

    results = []
    if freq_id:
        freq = get_object_or_404(Frequency, pk=freq_id)
        ok, detail = do_sync(freq)
        results.append({"id": freq.id, "ok": ok, "detail": detail})
    else:
        for freq in Frequency.objects.filter(suap_synced=False)[:200]:
            ok, detail = do_sync(freq)
            results.append({"id": freq.id, "ok": ok, "detail": detail})

    return JsonResponse({"results": results})


@csrf_exempt
@require_staff
def suap_auth(request):
    # Endpoint para obter token SUAP e salvar em banco
    if request.method != 'POST':
        return JsonResponse({"error": "POST required"}, status=400)
    payload = json.loads(request.body.decode())
    username = payload.get('username')
    password = payload.get('password')

    api_url = getattr(settings, 'SUAP_API_URL', None)
    token_url = getattr(settings, 'SUAP_TOKEN_URL', None) or (f"{api_url.rstrip('/')}/api/token/" if api_url else None)
    client_id = getattr(settings, 'SUAP_CLIENT_ID', None)
    client_secret = getattr(settings, 'SUAP_CLIENT_SECRET', None)

    if not token_url:
        # Simulate token creation
        token = SuapToken.objects.create(access_token='simulated-token')
        return JsonResponse({"status": "ok", "token": token.access_token})

    try:
        # Prefer client_credentials if client_id/secret provided and no username/password
        data = {}
        auth = None
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if client_id and client_secret and not (username and password):
            data['grant_type'] = 'client_credentials'
            # use HTTP Basic auth if token endpoint expects it
            auth = (client_id, client_secret)
        elif username and password:
            data['grant_type'] = 'password'
            data['username'] = username
            data['password'] = password
            if client_id and client_secret:
                data['client_id'] = client_id
                data['client_secret'] = client_secret
        else:
            return JsonResponse({"error": "missing_credentials"}, status=400)

        resp = requests.post(token_url, data=data, auth=auth, headers=headers, timeout=10)
        if resp.status_code in (200, 201):
            data = resp.json()
            access = data.get('access') or data.get('access_token') or data.get('token')
            refresh = data.get('refresh') or data.get('refresh_token')
            token_type = data.get('token_type')
            scope = data.get('scope')
            expires_in = data.get('expires_in')
            expires_at = None
            if expires_in:
                expires_at = dj_timezone.now() + dj_timezone.timedelta(seconds=int(expires_in))
            token = SuapToken.objects.create(
                access_token=access or '', refresh_token=refresh or None,
                token_type=token_type or None, scope=scope or None, expires_at=expires_at
            )
            return JsonResponse({"status": "ok", "token": token.access_token})
        return JsonResponse({"error": "auth_failed", "status": resp.status_code, "body": resp.text}, status=502)
    except Exception as exc:
        return JsonResponse({"error": "auth_error", "detail": str(exc)}, status=502)


@csrf_exempt
def dashboard_api(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=400)

    task_counts = {status: Task.objects.filter(status=status).count() for status, _ in Task.STATUS_CHOICES}
    total_tasks = Task.objects.count()
    total_frequencies = Frequency.objects.count()
    unconfirmed_frequencies = Frequency.objects.filter(confirmed=False).count()
    pending_sync = Frequency.objects.filter(suap_synced=False).count()
    top_contributors = list(
        get_user_model()
        .objects.annotate(total_frequencies=Count("frequency"))
        .filter(total_frequencies__gt=0)
        .order_by("-total_frequencies")
        .values("username", "total_frequencies")[:5]
    )

    return JsonResponse(
        {
            "tasks": {
                "total": total_tasks,
                "counts": task_counts,
            },
            "frequencies": {
                "total": total_frequencies,
                "unconfirmed": unconfirmed_frequencies,
                "pending_sync": pending_sync,
            },
            "top_contributors": top_contributors,
        }
    )


@csrf_exempt
def orientador_summary(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=400)

    student_summary = list(
        Frequency.objects.values("user__username")
        .annotate(
            total=Count("id"),
            confirmed=Count("id", filter=Q(confirmed=True)),
            pending_sync=Count("id", filter=Q(suap_synced=False)),
        )
        .order_by("-total")[:10]
    )

    return JsonResponse({"students": student_summary})


@require_staff
def audit_logs(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=400)

    logs = list(
        AuditLog.objects.order_by("-created_at")
        .values("created_at", "path", "method", "auth_type", "user__username", "remote_addr", "detail")[:50]
    )
    return JsonResponse({"logs": logs})


@csrf_exempt
def tasks_list(request):
    if request.method == "GET":
        tasks = Task.objects.all().values("id", "title", "description", "status")
        return JsonResponse({"tasks": list(tasks)})

    if request.method == "POST":
        data = json.loads(request.body.decode())
        title = data.get("title")
        description = data.get("description", "")
        task = Task.objects.create(title=title or "Untitled", description=description)
        return JsonResponse({"task": {"id": task.id, "title": task.title, "status": task.status}})


@csrf_exempt
def task_move(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)
    data = json.loads(request.body.decode())
    status = data.get("status")
    if status not in dict(Task.STATUS_CHOICES):
        return JsonResponse({"error": "invalid_status"}, status=400)
    task.status = status
    task.save()
    return JsonResponse({"status": "ok", "task": {"id": task.id, "status": task.status}})


@csrf_exempt
def task_associate(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)
    data = json.loads(request.body.decode())
    freq_id = data.get("frequency_id")
    if not freq_id:
        return JsonResponse({"error": "missing_frequency_id"}, status=400)
    freq = get_object_or_404(Frequency, pk=freq_id)
    freq.task = task
    freq.save()
    return JsonResponse({"status": "associated", "task_id": task.id, "frequency_id": freq.id})
