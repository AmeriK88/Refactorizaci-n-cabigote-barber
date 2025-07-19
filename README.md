# ✂️ **Cabigote Barber Shop** 🌟

## 📝 **Description**

Cabigote Barber Shop is an all-in-one web application designed to manage appointment bookings, reviews, and services for a barber shop. Users can schedule personalized services, view upcoming and past appointments, and leave detailed feedback on their experience—enhancing customer-business interaction. The application features separate profiles for clients and administrators, automatic notifications for confirmations and reminders, and a responsive, user-friendly interface. It’s built using Django as the backend framework, Bootstrap for modern and attractive styling, and a scalable database to efficiently handle multiple users and transactions.

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

This project, Cabigote Barber Shop by José Félix Gordo Castaño, is licensed for educational and learning purposes only. Commercial use, resale, or any profit-driven distribution is prohibited without explicit author permission.






