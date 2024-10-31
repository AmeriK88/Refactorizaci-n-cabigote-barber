# Cabigote Barber Shop

Este es un proyecto de gestión de citas y reseñas desarrollado con Django. La aplicación permite a los usuarios registrar, iniciar sesión, reservar citas, ver y gestionar sus citas (editar y eliminar), recibir confirmación vía email de la cita generada, y agregar reseñas. También incluye la edición del perfil y datos del usuario como contraseña, email y teléfono, así como una sección de productos con vista detallada del producto seleccionado. La aplicación maneja errores y excepciones, así como vistas personalizadas de plantillas de error. Además, proporciona un panel de administración mejorado mediante el uso de la biblioteca Grappelli.

# Estructura del Proyecto

## Models
- **Servicio**: Modela los servicios disponibles con nombre, descripción, precio e imagen.
- **Resena**: Permite a los usuarios dejar reseñas sobre los servicios.
- **Imagen**: Almacena imágenes relacionadas con los productos.
- **Cita**: Modela las citas que los usuarios pueden reservar.
- **UserProfile**: Almacena información adicional del usuario como correo electrónico y teléfono.

## Forms
- **CitaForm**: Formulario para reservar o editar citas con validación de fecha y hora.
- **ResenaForm**: Formulario para agregar reseñas.
- **CustomUserCreationForm**: Formulario de registro personalizado que incluye correo electrónico y teléfono.
- **UserProfileForm**: Formulario para editar el perfil del usuario.
- **UserForm**: Formulario para actualizar el correo electrónico del usuario.

## Views
- **home**: Página de inicio.
- **servicios**: Muestra todos los servicios y las citas del usuario si está autenticado.
- **register**: Registro de nuevos usuarios.
- **login_view**: Inicio de sesión de usuarios.
- **reservar_cita**: Reserva de una cita.
- **ver_citas**: Visualización de las citas del usuario.
- **editar_cita**: Edición de una cita.
- **eliminar_cita**: Eliminación de una cita.
- **logout_view**: Cierre de sesión.
- **ver_resenas**: Visualización y adición de reseñas.
- **agregar_resena**: Adición de una nueva reseña.
- **ver_imagenes**: Visualización de imágenes.
- **detalle_producto**: Detalle de un producto.
- **perfil_usuario**: Perfil del usuario con citas asociadas.
- **editar_perfil_usuario**: Edición del perfil del usuario.

## Contribución
Las contribuciones son bienvenidas. Si deseas contribuir a este proyecto, por favor sigue estos pasos:

1. **Haz un fork** del repositorio.
2. **Crea una nueva rama** para tu funcionalidad o corrección de errores.
3. **Realiza tus cambios** y haz commit.
4. **Envía un pull request** con una descripción clara de tus cambios.

## Características

- **Registro y Autenticación de Usuarios**: Los usuarios pueden registrarse, iniciar sesión y actualizar su perfil.
- **Gestión de Citas**: Permite a los usuarios reservar, ver, editar y cancelar citas.
- **Reseñas de Servicios**: Los usuarios pueden agregar reseñas a los servicios y ver las reseñas existentes.
- **Galería de Imágenes**: Los usuarios pueden ver detalles de productos a través de imágenes.
- **Panel de Administración Mejorado**: Utiliza Grappelli para una interfaz de administración más intuitiva y atractiva.

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


## Instalación

1. **Clona el Repositorio**

   ```bash
   git clone https://github.com/<username>/<repo-name>.git
   cd <repo-name>
