# 🎬 Videoflix Backend

Django REST API Backend für die Videoflix Streaming-Plattform mit HLS-Video-Streaming, Benutzerauthentifizierung und asynchroner Video-Konvertierung.

![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![Django](https://img.shields.io/badge/django-5.2.4-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

## 📋 Inhaltsverzeichnis

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Voraussetzungen](#voraussetzungen)
- [Installation](#installation)
- [Konfiguration](#konfiguration)
- [API-Dokumentation](#api-dokumentation)
- [Deployment](#deployment)
- [Projekt-Struktur](#projekt-struktur)

## ✨ Features

### Authentication
- ✅ JWT-basierte Authentifizierung mit HTTP-only Cookies
- ✅ Benutzerregistrierung mit E-Mail-Verifikation
- ✅ Passwort-Zurücksetzen via E-Mail
- ✅ Token Refresh Mechanismus
- ✅ Responsive HTML-E-Mail-Templates

### Video Management
- ✅ HLS (HTTP Live Streaming) mit adaptiver Bitrate
- ✅ Automatische Video-Konvertierung in 4 Auflösungen (120p, 360p, 720p, 1080p)
- ✅ Asynchrone Verarbeitung mit Django RQ
- ✅ FFmpeg-basierte Konvertierung
- ✅ Genre-Kategorisierung
- ✅ Featured Video Unterstützung

### Technische Features
- ✅ RESTful API mit Django REST Framework
- ✅ PostgreSQL Datenbank
- ✅ Redis als Cache und Message Queue
- ✅ Docker & Docker Compose Setup
- ✅ CORS-Konfiguration für Frontend
- ✅ Media-File-Handling mit optimierten Pfaden

## 🛠️ Tech Stack

- **Framework:** Django 5.2.4
- **API:** Django REST Framework 3.16.0
- **Authentication:** Django Simple JWT 5.5.0
- **Task Queue:** Django RQ 3.1 + RQ Scheduler
- **Database:** PostgreSQL 13
- **Cache/Queue:** Redis 7
- **Video Processing:** FFmpeg
- **WSGI Server:** Gunicorn 23.0.0
- **Email:** SMTP (konfigurierbar)

## 📦 Voraussetzungen

- **Docker:** >= 20.10
- **Docker Compose:** >= 2.0

Oder für lokale Entwicklung ohne Docker:
- **Python:** 3.13
- **PostgreSQL:** >= 13
- **Redis:** >= 7
- **FFmpeg:** Latest

## 🚀 Installation

### Mit Docker (Empfohlen)

1. **Repository klonen:**
```bash
git clone https://github.com/yourusername/videoflix-backend.git
cd videoflix-backend
```

2. **Umgebungsvariablen konfigurieren:**

Erstelle eine `.env` Datei im Root-Verzeichnis (siehe `.env.template`):

```bash
# Django Settings
SECRET_KEY=your-secret-key-here-min-50-characters-long
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=videoflix_db
POSTGRES_USER=videoflix_user
POSTGRES_PASSWORD=your-secure-db-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Email Configuration (Strato Example)
EMAIL_HOST=smtp.strato.de
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=your-email@domain.com

# Frontend URL (for email links)
FRONTEND_URL=http://localhost:4200

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:4200
```

3. **Docker Container starten:**
```bash
docker-compose up --build
```

Im Hintergrund starten:
```bash
docker-compose up -d
```

4. **Datenbank initialisieren:**
```bash
# Migrationen ausführen
docker-compose exec web python manage.py migrate

# Superuser erstellen
docker-compose exec web python manage.py createsuperuser

# Statische Dateien sammeln
docker-compose exec web python manage.py collectstatic --no-input
```

5. **Services erreichen:**
- **API:** http://localhost:8000/api
- **Admin Panel:** http://localhost:8000/admin
- **Media Files:** http://localhost:8000/media

### Lokale Installation (ohne Docker)

1. **Virtual Environment erstellen:**
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
# oder
.\env\Scripts\activate  # Windows
```

2. **Dependencies installieren:**
```bash
pip install -r requirements.txt
```

3. **PostgreSQL & Redis starten:**
```bash
# PostgreSQL
sudo service postgresql start

# Redis
sudo service redis-server start
```

4. **.env Datei anpassen:**
```bash
DB_HOST=localhost
REDIS_HOST=localhost
```

5. **Migrationen und Server:**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

6. **RQ Worker starten (separates Terminal):**
```bash
python manage.py rqworker default
```

## ⚙️ Konfiguration

### Video-Upload und Konvertierung

1. **Admin-Panel öffnen:** http://localhost:8000/admin

2. **Genre erstellen:**
   - Navigiere zu "Genres"
   - Erstelle z.B. "Action", "Comedy", "Drama"

3. **Video hochladen:**
   - Navigiere zu "Videos"
   - Erstelle neues Video
   - Felder ausfüllen (Titel, Beschreibung, Genre)
   - Thumbnail hochladen (optional)
   - Featured-Status setzen (optional)
   - Speichern

4. **Original-Video hinzufügen:**
   - Navigiere zu "Video files"
   - Erstelle neuen Eintrag
   - Video auswählen
   - Resolution: `original`
   - Video-Datei hochladen
   - Speichern

5. **Automatische Konvertierung:**
   - Django RQ Task startet automatisch
   - Konvertiert in: 1080p, 720p, 360p, 120p
   - Erstellt HLS-Playlists (.m3u8)
   - Progress im RQ Dashboard sichtbar

### Video-Qualitäten anpassen

In `videos/constants.py`:

```python
RESOLUTION_CONFIGS = [
    # (Name, Höhe, Video-Bitrate, Audio-Bitrate)
    ('1080p', 1080, '5000k', '192k'),
    ('720p', 720, '2500k', '128k'),
    ('360p', 360, '800k', '96k'),
    ('120p', 120, '300k', '64k'),
]

HLS_SEGMENT_DURATION = 6  # Sekunden
FFMPEG_PRESET = 'fast'  # ultrafast, fast, medium, slow
```

### E-Mail-Templates anpassen

Templates befinden sich in `templates/emails/`:

**activation.html** - Account-Aktivierung:
```html
<!-- Responsive HTML mit Aktivierungslink -->
{{ activation_link }}
```

**password_reset.html** - Passwort-Zurücksetzen:
```html
<!-- Responsive HTML mit Reset-Link -->
{{ reset_link }}
```

### CORS-Konfiguration

In `core/settings.py`:

```python
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:4200'
).split(',')

CORS_ALLOW_CREDENTIALS = True
```

## 🔌 API-Dokumentation

### Authentication Endpoints

#### Registrierung
```http
POST /api/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!"
}

Response: 201 Created
{
  "message": "Registration successful. Please check your email to activate your account.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe"
  }
}
```

#### Account-Aktivierung
```http
GET /api/activate/<uid>/<token>/

Response: 200 OK
{
  "message": "Account activated successfully"
}
```

#### Login
```http
POST /api/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response: 200 OK
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe"
  }
}
# + HTTP-only Cookies: access_token, refresh_token
```

#### Logout
```http
POST /api/logout/

Response: 200 OK
{
  "message": "Logout successful"
}
```

#### Token Refresh
```http
POST /api/token/refresh/

Response: 200 OK
# Neuer access_token in Cookie
```

#### Aktueller Benutzer
```http
GET /api/me/
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true
}
```

#### Passwort-Reset anfordern
```http
POST /api/reset-password/
Content-Type: application/json

{
  "email": "user@example.com"
}

Response: 200 OK
{
  "message": "Password reset email sent"
}
```

#### Passwort zurücksetzen
```http
POST /api/reset-password-confirm/
Content-Type: application/json

{
  "uid": "MQ",
  "token": "c6k5hn-abc123...",
  "new_password": "NewSecurePass123!",
  "confirm_password": "NewSecurePass123!"
}

Response: 200 OK
{
  "message": "Password reset successful"
}
```

### Video Endpoints

#### Alle Videos
```http
GET /api/videos/

Response: 200 OK
[
  {
    "id": 1,
    "title": "Action Movie",
    "description": "Exciting action film",
    "thumbnail": "/media/thumbnails/action.jpg",
    "genre": {
      "id": 1,
      "name": "Action"
    },
    "created_at": "2025-01-15T10:30:00Z",
    "is_featured": false,
    "video_files": [
      {
        "id": 1,
        "resolution": "1080p",
        "file": "/media/videos/1/hls_1080p/playlist.m3u8",
        "size": 524288000
      }
    ]
  }
]
```

#### Video-Details
```http
GET /api/videos/<id>/

Response: 200 OK
{
  "id": 1,
  "title": "Action Movie",
  "description": "Exciting action film",
  "thumbnail": "/media/thumbnails/action.jpg",
  "genre": {
    "id": 1,
    "name": "Action"
  },
  "video_files": [...]
}
```

#### Featured Video
```http
GET /api/videos/featured/

Response: 200 OK
{
  "id": 1,
  "title": "Featured Movie",
  ...
}
```

#### Videos nach Genre
```http
GET /api/videos/by_genre/

Response: 200 OK
{
  "Action": [...],
  "Comedy": [...],
  "Drama": [...]
}
```

#### Alle Genres
```http
GET /api/genres/

Response: 200 OK
[
  {
    "id": 1,
    "name": "Action"
  },
  {
    "id": 2,
    "name": "Comedy"
  }
]
```

## 🚢 Deployment

### Production Setup

1. **.env für Production:**
```bash
SECRET_KEY=<generiere-einen-sicheren-key-min-50-zeichen>
DEBUG=False
ALLOWED_HOSTS=api.yourdomain.com,yourdomain.com
FRONTEND_URL=https://yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

2. **SECRET_KEY generieren:**
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

3. **Docker Compose Production:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

4. **SSL/TLS mit Nginx:**
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /media/ {
        alias /var/www/videoflix/backend/media/;
    }

    location /static/ {
        alias /var/www/videoflix/backend/static/;
    }
}
```

5. **Migrationen & Static Files:**
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --no-input
```

### Wichtige Sicherheitshinweise

- ✅ `DEBUG=False` in Production
- ✅ Starken `SECRET_KEY` verwenden (min. 50 Zeichen)
- ✅ HTTPS erzwingen
- ✅ `ALLOWED_HOSTS` korrekt setzen
- ✅ Datenbank-Credentials sicher aufbewahren
- ✅ `.env` niemals committen (in `.gitignore`)
- ✅ CORS nur für vertrauenswürdige Origins
- ✅ Regelmäßige Backups der Datenbank
- ✅ Media-Files extern speichern (S3, etc.)

## 📂 Projekt-Struktur

```
backend/
├── core/                      # Django Projekt-Settings
│   ├── __init__.py
│   ├── settings.py           # Haupt-Konfiguration
│   ├── urls.py               # URL-Routing
│   ├── wsgi.py               # WSGI Entry Point
│   └── asgi.py               # ASGI Entry Point
│
├── users/                     # Benutzer-App
│   ├── api/
│   │   ├── serializers.py    # User-Serializers
│   │   └── urls.py           # Auth-Routes
│   ├── models.py             # CustomUser-Model
│   ├── views.py              # Auth-Views
│   └── utils.py              # Email-Hilfsfunktionen
│
├── videos/                    # Video-App
│   ├── models.py             # Video, Genre, VideoFile
│   ├── views.py              # Video-API-Views
│   ├── serializers.py        # Video-Serializers
│   ├── tasks.py              # Video-Konvertierung (RQ)
│   ├── urls.py               # Video-Routes
│   ├── signals.py            # Post-Save Signals
│   ├── utils.py              # FFmpeg-Funktionen
│   ├── constants.py          # Video-Konfiguration
│   └── admin.py              # Admin-Konfiguration
│
├── templates/
│   └── emails/               # E-Mail-Templates
│       ├── activation.html
│       └── password_reset.html
│
├── media/                     # Upload-Verzeichnis
│   ├── thumbnails/
│   └── videos/
│       └── <video_id>/
│           ├── original/
│           ├── hls_1080p/
│           ├── hls_720p/
│           ├── hls_360p/
│           └── hls_120p/
│
├── static/                    # Statische Dateien
├── manage.py                  # Django Management
├── requirements.txt           # Python Dependencies
├── docker-compose.yml         # Docker Configuration
├── backend.Dockerfile         # Backend Container
├── backend.entrypoint.sh      # Container Entry Point
├── .env                       # Umgebungsvariablen (nicht committen!)
├── .env.template              # Template für .env
├── .gitignore
└── README.md
```

## 🧪 Tests

```bash
# Alle Tests ausführen
docker-compose exec web python manage.py test

# Spezifische App testen
docker-compose exec web python manage.py test users
docker-compose exec web python manage.py test videos

# Mit Coverage
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
```

## 🛠️ Nützliche Commands

```bash
# Logs anzeigen
docker-compose logs -f web
docker-compose logs -f rqworker

# Shell öffnen
docker-compose exec web python manage.py shell

# Datenbank-Shell
docker-compose exec web python manage.py dbshell

# RQ-Dashboard
# Starte RQ Dashboard separat oder nutze Admin-Interface

# Container neu starten
docker-compose restart web

# Alle Container stoppen
docker-compose down

# Container mit Volumes löschen
docker-compose down -v
```

## 🔧 Troubleshooting

### Video-Konvertierung schlägt fehl
```bash
# RQ Worker Logs prüfen
docker-compose logs rqworker

# FFmpeg im Container testen
docker-compose exec web ffmpeg -version

# Manuell Task triggern
docker-compose exec web python manage.py shell
>>> from videos.tasks import convert_video
>>> convert_video(video_id=1)
```

### E-Mails werden nicht versendet
```bash
# SMTP-Settings prüfen
docker-compose exec web python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])
```

### Migrations-Probleme
```bash
# Alle Migrationen zurücksetzen
docker-compose exec web python manage.py migrate <app_name> zero

# Migrationen neu erstellen
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

## 👤 Autor

**Dein Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

## 📞 Support

Bei Fragen oder Problemen:
- Erstelle ein [Issue](https://github.com/yourusername/videoflix-backend/issues)
- Email: support@yourdomain.com

---

**Entwickelt mit ❤️ für Videoflix**
