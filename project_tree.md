# Estructura del proyecto: `cabigote/` ✅

> Nota: Se han excluido los archivos y directorios listados en `.gitignore` (por ejemplo: `env.txt`, `client_cabigote_secret.json`, `logs/`, `media/`, `staticfiles/`, `venv/`, `__pycache__/`, `.env`).

```
cabigote/
├─ .dockerignore
├─ .gitignore
├─ LICENSE.TXT
├─ README.md
├─ Dockerfile
├─ Procfile
├─ manage.py
├─ configurar_loger.py
├─ generate_qr.py
├─ requirements.txt
│
├─ appointments/
│   ├─ __init__.py
│   ├─ admin.py
│   ├─ apps.py
│   ├─ forms.py
│   ├─ models.py
│   ├─ tests.py
│   ├─ urls.py
│   ├─ views.py
│   ├─ migrations/
│   │   ├─ __init__.py
│   │   └─ 0001_initial.py
│   └─ templates/
│       ├─ admin/
│       │   └─ grafico_citas.html
│       └─ appointments/
│           ├─ ver_citas.html
│           ├─ reservar_cita.html
│           ├─ eliminar_cita.html
│           └─ editar_cita.html
│
├─ cabigote/  (project package)
│   ├─ __init__.py
│   ├─ asgi.py
│   ├─ settings.py
│   ├─ urls.py
│   └─ wsgi.py
│
├─ core/
│   ├─ __init__.py
│   ├─ adapters.py
│   ├─ admin.py
│   ├─ apps.py
│   ├─ context_processors.py
│   ├─ decorators.py
│   ├─ models.py
│   ├─ urls.py
│   ├─ utils.py
│   ├─ views.py
│   ├─ whitenoise_headers.py
│   ├─ management/
│   │   └─ commands/
│   │       └─ enviar_recordatorios.py
│   ├─ middlewares/
│   │   ├─ block_probes.py
│   │   └─ redirection.py
│   ├─ migrations/
│   │   ├─ __init__.py
│   │   └─ 0001_initial.py
│   └─ templates/
│       ├─ base.html
│       ├─ home.html
│       ├─ errors/
│       │   ├─ 403.html
│       │   ├─ 404.html
│       │   ├─ 500.html
│       │   └─ locked_out.html
│       ├─ legal/
│       │   ├─ cookies.html
│       │   └─ privacidad.html
│       └─ socialaccount/
│           ├─ signup.html
│           ├─ login.html
│           ├─ connections.html
│           └─ social_error.html
│
├─ products/
│   ├─ __init__.py
│   ├─ admin.py
│   ├─ apps.py
│   ├─ forms.py
│   ├─ models.py
│   ├─ tests.py
│   ├─ urls.py
│   ├─ views.py
│   ├─ migrations/
│   │   ├─ __init__.py
│   │   └─ 0001_initial.py
│   └─ templates/
│       └─ products/
│           ├─ ver_imagenes.html
│           └─ detalle_producto.html
│
├─ reports/
│   ├─ __init__.py
│   ├─ admin.py
│   ├─ apps.py
│   ├─ models.py
│   ├─ signals.py
│   ├─ tests.py
│   ├─ urls.py
│   ├─ utils.py
│   └─ templates/
│       └─ admin/
│           ├─ custom_report.html
│           └─ custom_report_diario.html
│
├─ reviews/
│   ├─ __init__.py
│   ├─ admin.py
│   ├─ apps.py
│   ├─ forms.py
│   ├─ models.py
│   ├─ tests.py
│   ├─ urls.py
│   ├─ views.py
│   └─ templates/
│       └─ reviews/
│           └─ ver_resenas.html
│
├─ services/
│   ├─ __init__.py
│   ├─ admin.py
│   ├─ apps.py
│   ├─ forms.py
│   ├─ models.py
│   ├─ tests.py
│   ├─ urls.py
│   ├─ views.py
│   ├─ migrations/
│   │   ├─ __init__.py
│   │   └─ 0001_initial.py
│   └─ templates/
│       └─ services/
│           └─ servicios.html
│
├─ static/
│   ├─ manifest.json
│   ├─ admin/
│   │   └─ css/
│   │       └─ adminCSS.css
│   ├─ css/
│   │   └─ styles.css
│   ├─ icons/
│   │   ├─ icon-192.webp
│   │   ├─ icon-512.webp
│   │   ├─ icon-512-maskable.webp
│   │   └─ logo-updated.png
│   ├─ imagenes/
│   │   ├─ favicon.ico
│   │   ├─ cabigote.webp
│   │   ├─ logo-cb.webp
│   │   ├─ logo-cb-nav.png
│   │   ├─ mockup-laptop.webp
│   │   ├─ mockup-phone.webp
│   │   └─ barber-pole.webp
│   └─ js/
│       ├─ Animations.js
│       ├─ Cookies_modal.js
│       ├─ Cookies consent and helper scripts
│       ├─ Loader.js
│       ├─ disableDates.js
│       ├─ historial-citas.js
│       ├─ passive-touch.js
│       ├─ pwa-install.js
│       ├─ special_message.js
│       ├─ togglePassword.js
│       └─ whatsappConsent.js
│
├─ templates/
│   ├─ offline.html
│   ├─ sw.js
│   ├─ account/
│   ├─ admin/
│   └─ (otras plantillas: p.ej. account/admin/ y vistas específicas)
│
├─ users/
│   ├─ __init__.py
│   ├─ admin.py
│   ├─ apps.py
│   ├─ forms.py
│   ├─ models.py
│   ├─ tests.py
│   ├─ urls.py
│   ├─ views.py
│   ├─ migrations/
│   │   ├─ __init__.py
│   │   └─ 0001_initial.py
│   └─ templates/
│       └─ users/
│           ├─ register.html
│           ├─ perfil_usuario.html
│           ├─ login.html
│           ├─ editar_perfil_usuario.html
│           └─ account_delete_confirm.html
│
├─ scripts/  (vacío)
└─ other top-level files omitted by .gitignore: (e.g. `client_cabigote_secret.json`, `env.txt`, `logs/`, `media/`, `staticfiles/`, `.env`, `venv/`)
```

---

**Archivo creado:** `project_tree.md` en la raíz del proyecto (excluyendo lo ignorado). ⚡️
