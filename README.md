# Projeto ATT — Setup rápido

Instruções para rodar o projeto localmente.

Pré-requisitos
- Python 3.12+
- Node.js + npm

Rodando localmente (scripts automáticos)

1. Tornar os scripts executáveis (uma vez):

```bash
chmod +x start.sh stop.sh
```

2. Iniciar backend + frontend:

```bash
./start.sh
```

3. Parar serviços:

```bash
./stop.sh
```

Logs:
- Backend: `logs/django.log`
- Frontend: `logs/frontend.log`

Alternativa manual

Backend:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Frontend:
```bash
cd frontend
npm ci
npm start
```
