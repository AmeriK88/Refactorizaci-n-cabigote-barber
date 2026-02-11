# ✂️ Cabigote Barber Shop

> **Sistema integral de gestión para barberías:** Agenda de citas, perfiles de clientes, reseñas, reportes financieros y notificaciones automáticas.

**[Demo](#demo) • [Características](#-características) • [Instalación](#instalación) • [Documentación Técnica](#documentación-técnica) • [Licencia](#licencia)**

---

## 🎯 ¿Por Qué Cabigote?

### El Problema
Las barberías tradicionales enfrentan desafíos operacionales:
- ❌ Gestión manual de citas (libreta, whatsapp)
- ❌ Clientes olvidados sin confirmaciones
- ❌ Imposible saber ingresos mensuales
- ❌ Sin catálogo formal de servicios
- ❌ Difícil recopilar feedback de clientes

### La Solución
**Cabigote** centraliza **todo** en una plataforma web moderna:
- ✅ Clientes reservan citas en tiempo real (sin llamadas)
- ✅ Confirmaciones y recordatorios automáticos por email
- ✅ Dashboard de ingresos diarios/mensuales con gráficos
- ✅ Catálogo de servicios con fotos
- ✅ Reseñas de clientes (5 estrellas)
- ✅ Gestión de disponibilidad (días cerrados, horas de almuerzo)
- ✅ Responsive: Funciona en computadora, tablet y teléfono

---

## 🌟 Características Principales

### Para Clientes
| Característica | Beneficio |
|---|---|
| 📅 **Reserva Fácil** | Ver disponibilidad, seleccionar fecha/hora y confirmar en 2 minutos |
| 📧 **Confirmaciones** | Email automático de confirmación (sin sorpresas) |
| ⏰ **Recordatorios** | Recordatorio 24h antes de la cita (reducir cancelaciones) |
| 👤 **Mi Perfil** | Ver mis citas pasadas y próximas en un lugar |
| ⭐ **Reseñas** | Dejar feedback (ayuda a mejorar) |
| 🔐 **Seguridad** | Contraseña encriptada, protección contra robots |

### Para Administrador (Barbería)
| Característica | Beneficio |
|---|---|
| 📊 **Reportes** | Ver ingresos día a día, mes a mes con gráficos |
| 📋 **Gestión de Citas** | Crear, editar, cancelar citas desde panel |
| 🚫 **Bloqueo de Fechas** | Marcar días de vacaciones/cierre (ej: domingos, festivos) |
| ⏱️ **Bloqueo Horario** | Bloquear rangos de horas (ej: almuerzo 1-2pm) |
| 🛎️ **Catálogo de Servicios** | Agregar/editar servicios con fotos y precios |
| 📸 **Galería de Productos** | Mostrar fotos de trabajos realizados o productos a vender |
| 👥 **Clientes** | Ver historial de cada cliente (citas, gastos) |
| 📨 **Notificaciones** | Envío automático de emails de confirmación/cambios |

---

## 📱 Demo

**Página Principal:** Muestra servicios, testimonios, contador de visitas

**Reserva de Cita:**
1. Cliente selecciona servicio (ej: "Corte regular - $15")
2. Sistema muestra fechas disponibles (excluye domingos, vacaciones)
3. Cliente elige fecha → sistema muestra horas libres
4. Confirma → recibe email de confirmación

**Mi Perfil:**
- Citas próximas (con opción editar/cancelar)
- Historial de citas pasadas
- Dinero gastado este año
- Botón para editar datos personales

**Panel Admin:**
- Dashboard: Citas hoy, ingresos hoy, total clientes
- Gráficos: Ingresos mensuales, citas por día
- Tabla: Todas las citas del mes
- Descargar reportes en .txt

---

## 🛠️ Stack Tecnológico

**Backend:** [Django 5.1.5](https://www.djangoproject.com/) - Framework Python robusto y seguro  
**Frontend:** [Bootstrap 5](https://getbootstrap.com/) - Interfaz responsive y moderna  
**Base de Datos:** [MySQL 8.0+](https://www.mysql.com/) - Escalable, confiable  
**Servidor:** [Gunicorn](https://gunicorn.org/) + [WhiteNoise](https://whitenoise.evans.io/) - Producción optimizada  
**Autenticación:** [Django-Allauth](https://django-allauth.readthedocs.io/) - Login tradicional + Google OAuth  
**Seguridad:** [Django-Axes](https://django-axes.readthedocs.io/) + [reCAPTCHA v3](https://www.google.com/recaptcha) - Anti-brute force, anti-bots  
**Reportes:** [Matplotlib](https://matplotlib.org/) + [Pandas](https://pandas.pydata.org/) - Gráficos y análisis  
**Multimedia:** [Pillow](https://pillow.readthedocs.io/) - Procesamiento de imágenes  

---

## 🚀 Inicio Rápido

### Requisitos Mínimos
- **Python 3.8+** (recomendado 3.11+)
- **MySQL 8.0+** (o MariaDB)
- **Git** (para clonar el repo)

### Instalación (5 minutos)

```bash
# 1. Clonar repositorio
git clone https://github.com/tuusuario/cabigote.git
cd cabigote

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear archivo .env
cat > .env << EOF
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
DATABASE_URL=mysql://usuario:contraseña@localhost/cabigote_db
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-app
RECAPTCHA_PUBLIC_KEY=tu-public-key
RECAPTCHA_PRIVATE_KEY=tu-private-key
EOF

# 5. Crear base de datos
mysql -u usuario -p
mysql> CREATE DATABASE cabigote_db;
mysql> EXIT;

# 6. Migraciones
python manage.py migrate

# 7. Crear admin
python manage.py createsuperuser

# 8. Ejecutar servidor
python manage.py runserver
```

**Accede en:** http://localhost:8000

**Admin en:** http://localhost:8000/admin/

---

## 📖 Documentación Técnica

Para desarrolladores y equipo técnico:

- **[DOCUMENTACION_COMPLETA.md](DOCUMENTACION_COMPLETA.md)** - Guía técnica exhaustiva
  - Estructura de apps (Users, Appointments, Services, Products, Reviews, Reports)
  - Modelos y relaciones de BD
  - Flujos de autenticación y reservas
  - APIs y endpoints
  - Despliegue (Heroku, Railway, Docker)
  - Mejoras recomendadas

### Despliegue en Producción

**Heroku (Recomendado para empezar):**
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set SECRET_KEY="..."
git push heroku main
heroku run python manage.py migrate
```

**Railway.app:**
Conecta tu repo GitHub → deploy automático

**Docker:**
```bash
docker build -t cabigote .
docker run -p 8000:8000 -e SECRET_KEY="..." cabigote
```

---

## ❓ FAQ

### ¿Cuánto cuesta?
Depende del modelo:
- **SaaS (cloud):** $29-99/mes por barbería
- **Licencia única (on-premise):** $2,000-5,000 (único pago)
- **Customización:** Presupuesto según necesidades

### ¿Se puede customizar?
Sí. El código es abierto y modular. Puedes:
- Cambiar colores / logo
- Agregar nuevos servicios
- Integrar con otros sistemas
- Agregar funcionalidades

### ¿Qué soporte incluye?
- Documentación técnica completa
- Soporte por email
- Actualizaciones de seguridad
- Acceso a roadmap de features

### ¿Es seguro? ¿Mis datos están protegidos?
**Sí.** Implementa:
- ✅ HTTPS (encriptación en tránsito)
- ✅ Contraseñas hashed (PBKDF2)
- ✅ reCAPTCHA (anti-bots)
- ✅ CSRF protection
- ✅ Content Security Policy
- ✅ Backups diarios

### ¿Se integra con WhatsApp/SMS?
No en la versión actual, pero se puede agregar:
- Twilio (sms/whatsapp)
- Firebase (push notifications)

Contacta para presupuesto.

### ¿Qué pasa si tengo muchos clientes?
Cabigote escala sin problemas:
- MySQL maneja 100k+ registros
- Índices optimizados en BD
- Caché Redis (opcional)
- CDN para imágenes (opcional)

### ¿Puedo tener múltiples sucursales?
Con customización sí. Por defecto es para 1 barbería.

---

## 🔒 Seguridad y Privacidad

### Buenas Prácticas Implementadas
- ✅ **Autenticación segura:** PBKDF2 password hashing
- ✅ **Prevención de ataques:** CSRF tokens, CSP headers
- ✅ **Anti-bot:** reCAPTCHA v3 + rate limiting
- ✅ **Anti-fuerza bruta:** Bloqueo después de 5 intentos fallidos
- ✅ **Cookies seguras:** HttpOnly, Secure, SameSite
- ✅ **SQL Injection:** ORM Django (parametrized queries)
- ✅ **XSS Protection:** Template escaping automático

### Cumplimiento Legal
- ✅ GDPR compatible (droit à l'oubli, consentimiento)
- ✅ Política de privacidad incluida
- ✅ Términos de servicio (template)
- ✅ Derecho a eliminar cuenta

---

## 🤝 Contribución y Soporte

### Reportar Bugs
Abre un [Issue en GitHub](https://github.com/tuusuario/cabigote/issues)

### Solicitar Funcionalidades
[Discusiones en GitHub](https://github.com/tuusuario/cabigote/discussions)

### Contacto Comercial
📧 **Email:** josefe59@hotmail.com   
🌐 **Web:** [www.portfolioweb.com](https://web-production-jfgc.up.railway.app/)

---

## 📋 Hoja de Ruta (Roadmap)

**v1.0** (Actual)
- ✅ Reserva de citas
- ✅ Perfil de usuario
- ✅ Reportes básicos
- ✅ Notificaciones por email

**v1.5** (Próximo)
- 🔄 App móvil (iOS/Android)
- 🔄 Notificaciones SMS/WhatsApp
- 🔄 Integración pagos (Stripe, PayPal)
- 🔄 Multi-idioma (ES/EN/PT)

**v2.0**
- 🔄 Multi-sucursales
- 🔄 Horarios rotativos (staff)
- 🔄 Dashboard para barberos
- 🔄 Export reportes (PDF, Excel)

---

## 📄 Licencia

**© 2026 José Félix Gordo Castaño**

Este proyecto está protegido bajo licencia **Elastic License 2.0**.

**Permitido:**
- ✅ Uso comercial (bajo acuerdo de licencia)
- ✅ Modificación
- ✅ Redistribución (con permiso)

**Prohibido:**
- ❌ Venta sin autorización
- ❌ Remoción de créditos de autor
- ❌ Uso para competencia directa

Ver [LICENSE.TXT](LICENSE.TXT) para detalles completos.

---

## 👨‍💻 Autor

**José Félix Gordo Castaño**  
Senior Developer | Django Specialist  
📧 [contacto@josefelix.dev](mailto:contacto@josefelix.dev)  
🐙 [GitHub](https://github.com/tuusuario)  
💼 [LinkedIn](https://linkedin.com/in/tuusuario)

---

## ⭐ Si Te Resulta Útil

Danos una estrella en GitHub ⭐ y comparte con otros desarrolladores y barberías.

---

**Última actualización:** Febrero 2026  
**Versión:** 1.0.0

## 🛠️ **Used Techs**

| **Tech**    | **Description**                                |
|--------------------|-------------------------------------------------|
| 🐍 **Django**      | Robust backend framework.  |
| 🎨 **Bootstrap**   | Modern, responsive, and stylish frontend design.|
| 🗄️ **MySQL**       | Scalable database for multiple users.|
| 🖼️ **Pillow**      | Image handling and product gallery management.     |
| 🖋️ **QRCode**      | QR code generation for direct links.          |
| 🔐 **reCAPTCHA**   | Additional security against bots.                |
| 📊 **Matplotlib**  | Graph generation for reports.           |
| 📦 **Django Suit** | Advanced customization of the admin pane. |
| 🔔 **Email notifications** | Automatic confirmations, modifications, and reminders.. |

---

## 📂 **Project Structure**

The project comprises multiple Django apps, each handling specific functionality:

### 1. Appointments

- **Models**: 
  - `Cita`:Represents an appointment, including user, service, date, time, and notes.Represents an appointment, including user, service, date, time, and notes.
- **Forms**: 
  - `CitaForm`: Form to create and edit appointments, with date and time validation.
- **Views**: 
  - `reservar_cita`: Allows users to book appointments.
  - `ver_citas`: : Displays upcoming and past appointments.

### 2. Users

- **Models**: 
  - `UserProfile`:  Stores additional user information.
- **Forms**: 
  - `CustomUserCreationForm`: Custom registration form Custom registration form.
- **Views**: 
  - `login_view`: Login view.
  - `register`: Register view.
  - `perfil_usuario`: User profile view.

### 3. Reviews

- **Models**: 
  - `Resena`: Allows users to leave reviews about services.
- **Forms**: 
  - `ResenaForm`: Form to add reviews.
- **Views**: 
  - `ver_resenas`: Displays all reviews and allows new ones.

### 4. Services

- **Models**: 
  - `Servicio`: Represents services offered at the barbershop.
- **Forms**: 
  - `ServicioForm`: Form to create and edit services.
- **Views**: 
  - `ver_servicios`: Shows all available services.

### 5. Products

- **Modelos**: 
  - `Imagen`: Stores product images.
- **Views**: 
  - `ver_imagenes`: Displays all product image.
  - `detalle_producto`: Shows details of a specific product.

### 6. Reports

- **Models:** 
  - `ReporteMensual`: Monthly revenue and appointments reports.
  - `ReporteDiario`: Daily reports generated on demand.
- **Funcyionalities:**
  - Daily and monthly report generation with graphs.
  - Reports downloadable as .txt.
  - Option to generate daily reports from the admin panel by selecting a date.
  - Automatic cleanup of unnecessary reports.

## Installation

### Requisites

- Python 3.8 +
- Django 3.2 +

## 🚀 **Main Characteristics**

✅ **Users - Management:**  
- Registration/login template, user profile & edit profile.
- Custom register/login forms.

✅ **Appointments:**  
- Create, edit, cancel, and manage appointment history.
- Dynamically disabled blocked dates and occupied time slots.
- Templates for admin booking graph available in admin panel.

✅ **Core:**  
- Email reminders 24hrs before the service. Managment/commnads/.
- Templates home/base.html.
- Templates social login/register & social error validation.
- Context processors to inyect special messages in teh UI  & run the visitor count.
- Custom header to serve whitenoise

✅ **Reviews:**  
- Authenticated users can add and view star-rated reviews.

✅ **Producto & Service Gallery:**  
- Detailed information with images and descriptions.

✅ **Automated Notifications:**  
- Confirmations, reminders, and cancellations via email.

✅ **Custom Admin Panel:**  
- Django Suit integration for a modern interface.
- Visualization of appointment charts.
- Improved admin panil to a more modern design

✅ **Dynamic Reports:**  
- Generate daily/monthly reports by selected date.
- Downloadable text reports.

✅ **Date blocker:**  
- Blocksa a specific date or dates to prevent any new booking.
- Blocks a specific range of hours in a specific date to provent any new booking.

✅ **Security Features:**  

  - **Environment-based secrets**  
    • `SECRET_KEY` and all sensitive credentials are read from environment variables (via django-environ).  
    • `DEBUG` is disabled by default in production.  

  - **Allowed hosts enforcement**  
    Only your domains (`*.example.com`) are permitted in `ALLOWED_HOSTS`, preventing HTTP Host header attacks.

  - **HTTPS & secure cookies**  
    • `SESSION_COOKIE_SECURE = True` & `CSRF_COOKIE_SECURE = True` ensure cookies are only sent over HTTPS.  
    • `SECURE_PROXY_SSL_HEADER` trusts the proxy’s `X-Forwarded-Proto` header.

  - **Password hardening**  
    Django’s built-in `AUTH_PASSWORD_VALIDATORS` enforce minimum length, complexity and common-password checks.

  - **Content Security Policy (CSP)**  
    Using `django-csp` middleware to lock down permitted script, style, image and connect domains.

  - **Static file protection**  
    Whitenoise serves static assets with custom security headers (HSTS, cache-control) via `add_custom_headers`.

  - **Bot prevention**  
    Integrated Google reCAPTCHA on all public forms (login, signup, appointment booking) to block automated abuse.

  - **Strict CSRF & clickjacking defenses**  
    • `CsrfViewMiddleware` enabled site-wide.  
    • CSP’s `frame-ancestors 'self'` prevents embedding in other sites.

  - **Database constraints**  
    Unique constraints on key models (e.g. appointment `fecha`+`hora`) ensure data integrity even under race conditions.

---

## QR Code Generator

Run <code>generate_qr.py</code> – ensure you include your site URL.


## Instala las depencias

To install run: <code>pip install -r requirements.txt</code>

## ⚙️ **Installation**



## 🔒 License

This project is licensed under the Elastic License 2.0 (ELv2).

Commercial use, redistribution, or offering this software as a service
requires explicit permission from the author.

© 2026 José Félix Gordo Castaño







