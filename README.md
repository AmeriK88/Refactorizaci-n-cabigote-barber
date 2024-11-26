# ✂️ **Cabigote Barber Shop** 🌟

## 📝 **Descripción**

Cabigote Barber Shop es una aplicación web integral diseñada para gestionar reservas de citas, reseñas y servicios en un Barber-Shop. Los usuarios pueden reservar servicios personalizados, visualizar citas activas y pasadas, y dejar comentarios detallados sobre su experiencia, mejorando así la interacción cliente-negocio. La aplicación incluye características como la separación de perfiles para clientes y administradores, notificaciones automáticas para confirmaciones y recordatorios, y una interfaz de usuario responsiva y amigable. Está construida utilizando Django como framework backend, Bootstrap para un diseño moderno y atractivo, y se complementa con una base de datos escalable para manejar eficientemente múltiples usuarios y transacciones.

## 🛠️ **Tecnologías Utilizadas**

| **Tecnología**    | **Descripción**                                |
|--------------------|-----------------------------------------------|
| 🐍 **Django**      | Framework backend para una gestión robusta.  |
| 🎨 **Bootstrap**   | Diseño moderno, responsivo y estilizado.     |
| 🗄️ **MySQL**        | Base de datos escalable para múltiples usuarios. |
| 🖼️ **Pillow**      | Gestión de imágenes y galería de productos.  |
| 🖋️ **QRCode**      | Generación de códigos QR para enlaces.       |
| 🔐 **reCAPTCHA**   | Seguridad adicional contra bots.             |

---

## 📂 **Estructura del Proyecto**

El proyecto está compuesto por varias aplicaciones que manejan diferentes funcionalidades:

### 1. Appointments

- **Modelos**: 
  - `Cita`: Modelo que representa una cita, incluyendo campos como usuario, servicio, fecha, hora y comentario.
- **Formularios**: 
  - `CitaForm`: Formulario para crear y editar citas, con validación de fecha y hora.
- **Vistas**: 
  - `reservar_cita`: Permite a los usuarios reservar citas.
  - `ver_citas`: Muestra las citas activas y pasadas del usuario.

### 2. Users

- **Modelos**: 
  - `UserProfile`: Modelo que almacena información adicional del usuario.
- **Formularios**: 
  - `CustomUserCreationForm`: Formulario de registro personalizado.
- **Vistas**: 
  - `login_view`: Vista para iniciar sesión.
  - `register`: Vista para registrar nuevos usuarios.
  - `perfil_usuario`: Vista que muestra el perfil del usuario.

### 3. Reviews

- **Modelos**: 
  - `Resena`: Modelo que permite a los usuarios dejar reseñas sobre los servicios.
- **Formularios**: 
  - `ResenaForm`: Formulario para agregar reseñas.
- **Vistas**: 
  - `ver_resenas`: Vista que muestra todas las reseñas y permite agregar nuevas.

### 4. Services

- **Modelos**: 
  - `Servicio`: Modelo que representa los servicios ofrecidos en la barbería.
- **Formularios**: 
  - `ServicioForm`: Formulario para crear y editar servicios.
- **Vistas**: 
  - `ver_servicios`: Muestra todos los servicios disponibles.

### 5. Media

- **Modelos**: 
  - `Imagen`: Modelo que almacena imágenes de los productos.
- **Vistas**: 
  - `ver_imagenes`: Vista que muestra todas las imágenes de productos.
  - `detalle_producto`: Muestra detalles de un producto específico.

## Instalación

### Requisitos Previos

- Python 3.8 o superior
- Django 3.2 o superior

## 🚀 **Características Principales**

✅ **Gestión de Usuarios:**
- Registro, inicio de sesión y personalización de perfil.

✅ **Reservas de Citas:**
- Crear, editar, cancelar y gestionar el historial de citas.

✅ **Reseñas de Servicios:**
- Los usuarios pueden agregar y consultar reseñas con puntuaciones.

✅ **Galería de Servicios y Productos:**
- Información detallada con imágenes y descripciones.

✅ **Notificaciones Automáticas:**
- Recordatorios y confirmaciones vía correo electrónico.

✅ **Panel de Administración Personalizado:**
- Integración con Django Grappelli para una interfaz moderna.

---

## Requisitos

- asgiref==3.8.1
- colorama==0.4.6
- Django==5.1.1
- django-admin-interface==0.28.8
- django-colorfield==0.11.0
- django-environ==0.11.2
- django-jet==1.0.8
- django-model-utils==5.0.0
- django-notifications-hq==1.8.3
- django-recaptcha==4.0.0
- jsonfield==3.1.0
- mysqlclient==2.2.4
- pillow==10.4.0
- pypng==0.20220715.0
- python-dateutil==2.9.0
- python-dotenv==1.0.1
- python-slugify==8.0.4
- pytz==2024.2
- qrcode==7.4.2
- setuptools==75.2.0
- six==1.16.0
- sqlparse==0.5.1
- swapper==1.4.0
- text-unidecode==1.3
- typing_extensions==4.12.2
- tzdata==2024.1


## Generador Código QR

Ejecuta generate_qr.py - asegúrate de incluir la URL de tu sitio.


## Instala las depencias

pip install -r requirements.txt

## ⚙️ **Instalación**

### **1. Requisitos Previos**
- Python 3.8 o superior.
- Django 3.2 o superior.


## 🔒 Licencia

Este proyecto, Cabigote Barber Shop, desarrollado por José Félix Gordo Castaño, está licenciado para uso exclusivo con fines educativos y de aprendizaje. No se permite su venta, redistribución comercial o cualquier uso con fines de lucro sin autorización expresa del autor.




