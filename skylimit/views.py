import random
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
from django.utils.timezone import now
from .forms import RegisterForm
from django.views.decorators.csrf import csrf_protect
from datetime import date, timedelta
from calendar import monthrange, day_name
from django.shortcuts import render
from django.utils.timezone import now
import calendar
from .forms import PerfilUsuarioForm,EntrenadorRegisterForm,GrupoForm,ActividadForm,ComentarioForm,PublicacionForm,CrearRetoForm
from django.core.mail import EmailMessage
from .models import Entrenador,Grupo, Notificacion, ParticipacionReto,PerfilUsuario,MensajeGrupo,Actividad, ChatActividad, MensajeActividad,MensajePrivado, Reto, SolicitudEntrenador, SolicitudEntrenamiento,User,GrupoVisitado,Publicacion,Comentario,Like
from django.db import models


# Create your views here.
def index(request):
    return render(request, 'index.html')  # Asegúrate de que la ruta es correcta

def cuerpo_humano(request):
    return render(request, 'cuerpo_humano.html')

def mapa(request):
    return render(request, 'mapa.html')  # Renderiza el mapa sin coordenadas

from django.shortcuts import render
import requests

def obtener_nombre_lugar(lat, lon, api_key):
    """Obtiene el nombre del lugar usando la API de geocodificación inversa de OpenWeatherMap."""
    url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            # Devuelve el nombre del lugar (ciudad) y el país si está disponible
            lugar = data[0].get('name', 'Ubicación desconocida')
            pais = data[0].get('country', '')
            return f"{lugar}, {pais}" if pais else lugar
    return "Ubicación desconocida"

def mostrar_clima(request, lat, lon):
    """Obtiene el clima y lo muestra en tiempo_mapa.html"""
    api_key = "cf73aee0161f1073289c644de95ce3f2"  # 🔥 Usa tu propia API Key

    # Obtener el clima
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=es"
    response = requests.get(weather_url)
    weather_data = response.json()

    if response.status_code != 200:
        weather_data = {"error": "No se pudo obtener el clima"}

    # Obtener el nombre del lugar
    lugar = obtener_nombre_lugar(lat, lon, api_key)

    return render(request, 'tiempo_mapa.html', {
        'lat': lat,
        'lon': lon,
        'lugar': lugar,  # Añadir el nombre del lugar al contexto
        'weather': weather_data
    })

def obtener_clima(request):
    try:
        lat = request.GET.get("lat")
        lon = request.GET.get("lon")
        API_KEY = "cf73aee0161f1073289c644de95ce3f2"

        if not lat or not lon:
            return JsonResponse({"error": "Faltan parámetros lat y lon"}, status=400)

        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=es"
        response = requests.get(url)
        data = response.json()

        # 📌 Agregar depuración en la consola
        print("🌍 OpenWeather API URL:", url)
        print("🔍 OpenWeather Response:", data)

        if response.status_code == 200:
            return JsonResponse(data)
        else:
            return JsonResponse({"error": f"Error en la API: {data}"}, status=response.status_code)

    except Exception as e:
        print("🚨 ERROR EN obtener_clima:", str(e))
        return JsonResponse({"error": f"Error interno del servidor: {str(e)}"}, status=500)

def mostrar_oleaje(request, lat, lon):
    """Obtiene la información del oleaje y la muestra en tiempo_mapa.html"""
    api_url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&hourly=wave_height,wave_direction&timezone=auto"

    response = requests.get(api_url)
    data = response.json()

    # Extraer datos de oleaje
    wave_height = data['hourly']['wave_height'][0]  # Altura de las olas en metros
    wave_direction = data['hourly']['wave_direction'][0]  # Dirección del oleaje en grados

    return render(request, 'oleaje_mapa.html', {
        'lat': lat,
        'lon': lon,
        'wave_height': wave_height,
        'wave_direction': wave_direction,
    })
# ---------------------------------------------------------
#            SECCION INICIO Y CIERRE DE SESIÓN
# ---------------------------------------------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, '¡Inicio de sesión exitoso! Bienvenido.', extra_tags='login_usuario')
            return redirect('home')  # Redirige a home si el login es correcto
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.', extra_tags='login_usuario')
            return render(request, 'index.html', {'show_login_modal': True})  # Renderiza con una variable
    return redirect('home')


@csrf_protect
def logout_view(request):
    logout(request)
    return redirect('/')

def login_entrenador(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user and hasattr(user, 'entrenador') and user.entrenador.aprobado_por_admin:
            login(request, user)
            messages.success(request, 'Inicio de sesión exitoso como entrenador.', extra_tags='login_entrenador_success')
            return redirect('home')
        elif user and hasattr(user, 'entrenador'):
            messages.error(request, 'Tu cuenta de entrenador aún no ha sido aprobada.', extra_tags='login_entrenador_error')
        else:
            messages.error(request, 'Credenciales incorrectas.', extra_tags='login_entrenador_error')
    return render(request, 'index.html', {'show_login_entrenador_modal': True})

# ---------------------------------------------------------
#                  SECCION REGISTRO
# ---------------------------------------------------------

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Guardar el usuario en la base de datos
            user = form.save()  # El método `save()` ya maneja la creación de `PerfilUsuario`
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, '¡Registro exitoso! Has iniciado sesión automáticamente.')
                return redirect('/')  # Redirigir al inicio tras un registro exitoso
        else:
            # Mostrar errores del formulario con etiqueta "register"
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error, extra_tags='register')
    else:
        form = RegisterForm()
    
    # Mostrar el formulario en el contexto de la página de inicio o modal
    return render(request, 'index.html', {'form': form, 'show_register_modal': True})



def registrar_entrenador(request):
    if request.method == 'POST':
        form = EntrenadorRegisterForm(request.POST)
        if form.is_valid():
            # Verificar duplicados
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')

            if User.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya está en uso.', extra_tags='trainer_error')
                return render(request, 'index.html', {'form': form, 'show_register_entrenador_modal': True})

            if User.objects.filter(email=email).exists():
                messages.error(request, 'El correo electrónico ya está registrado.', extra_tags='trainer_error')
                return render(request, 'index.html', {'form': form, 'show_register_entrenador_modal': True})

            # Guardar solicitud
            SolicitudEntrenador.objects.create(
                username=username,
                email=email,
                password=form.cleaned_data['password'],
                nombre=form.cleaned_data['nombre'],
                apellidos=form.cleaned_data['apellidos'],
                genero=form.cleaned_data['genero'],
                nivel_experiencia=form.cleaned_data['nivel_experiencia'],
                especialidades=form.cleaned_data['especialidades'],
                experiencia=form.cleaned_data['experiencia'],
                formacion=form.cleaned_data['formacion'],
            )

            messages.success(request, 'Solicitud enviada. Un administrador revisará tu solicitud.', extra_tags='trainer_success')
            return redirect('home')
    else:
        form = EntrenadorRegisterForm()
    return render(request, 'index.html', {'form': form, 'show_register_entrenador_modal': True})

# ---------------------------------------------------------
#                  SECCION CONTACTO
# ---------------------------------------------------------


def contacto(request):
    if not request.user.is_authenticated:
        # Usuario no autenticado, mostrar el modal de inicio de sesión
        messages.error(request, 'Debes iniciar sesión para enviar un mensaje.', extra_tags='contacto')
        return render(request, 'index.html', {'show_login_modal': True, 'scroll_to_contacto': True})

    if request.method == 'POST':
        email = request.POST.get('email')
        nombre = request.POST.get('nombre')
        mensaje = request.POST.get('mensaje')

        if not email or not nombre or not mensaje:
            # Validación de campos vacíos
            messages.error(request, 'Todos los campos son obligatorios.', extra_tags='contacto')
            return render(request, 'index.html', {'scroll_to_contacto': True})

        # Configuración del correo
        asunto = f"Mensaje de contacto de {nombre}"
        mensaje_completo = f"De: {nombre} <{email}>\n\n{mensaje}"

        try:
            correo = EmailMessage(
                subject=asunto,
                body=mensaje_completo,
                from_email=email,
                to=['desarrolloskylimit@gmail.com'],
            )
            correo.send(fail_silently=False)
            messages.success(request, 'Tu mensaje ha sido enviado con éxito.', extra_tags='contacto')
        except Exception as e:
            # Captura errores en el envío de correos
            messages.error(request, f'Ocurrió un error al enviar tu mensaje: {str(e)}', extra_tags='contacto')

        return render(request, 'index.html', {'scroll_to_contacto': True})
    return render(request, 'index.html', {'scroll_to_contacto': True})

# ---------------------------------------------------------
#                  SECCION PERFIL
# ---------------------------------------------------------

@login_required
def editar_perfil(request):
    perfil = request.user.perfilusuario  # Obtén el perfil del usuario actual
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('ver_perfil')  # Redirige al perfil
    else:
        form = PerfilUsuarioForm(instance=perfil)
    return render(request, 'editar_perfil.html', {'form': form},)


@login_required
def ver_perfil(request):
    """
    Muestra el perfil del usuario. Si el usuario es un entrenador,
    redirige a la vista del perfil del entrenador.
    """
    if hasattr(request.user, 'entrenador'):
        # Renderizar el perfil del entrenador si el usuario lo es
        entrenador = request.user.entrenador
        return render(request, 'ver_perfilEntrenador.html', {
            'entrenador': entrenador,
            'es_entrenador': True,  # Indicar que es un entrenador
        })

    # Renderizar el perfil de usuario regular si no es entrenador
    perfil = request.user.perfilusuario
  

    return render(request, 'ver_perfil.html', {
        'perfil': perfil,
        'es_entrenador': False,  # Indicar que no es un entrenador
        
    })

# ---------------------------------------------------------
#                  SECCION ENTRENADORES
# ---------------------------------------------------------
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def gestionar_entrenadores(request):
    solicitudes_pendientes = SolicitudEntrenador.objects.all()
    total_solicitudes = solicitudes_pendientes.count()  # Contar las solicitudes pendientes
    
    if request.method == 'POST':
        solicitud_id = request.POST.get('solicitud_id')
        accion = request.POST.get('accion')

        try:
            solicitud = SolicitudEntrenador.objects.get(id=solicitud_id)
            if accion == 'aprobar':
                # Crear el usuario y el entrenador
                user = User.objects.create_user(
                    username=solicitud.username,
                    email=solicitud.email,
                    password=solicitud.password
                )
                Entrenador.objects.create(
                    user=user,
                    nombre=solicitud.nombre,
                    apellidos=solicitud.apellidos,
                    genero=solicitud.genero,
                    nivel_experiencia=solicitud.nivel_experiencia,
                    especialidades=solicitud.especialidades,
                    experiencia=solicitud.experiencia,
                    formacion=solicitud.formacion,
                    aprobado_por_admin=True,
                )
                
                messages.success(request, f"Entrenador {solicitud.nombre} {solicitud.apellidos} aprobado y registrado.")
            elif accion == 'rechazar':
                messages.info(request, f"Solicitud de {solicitud.nombre} {solicitud.apellidos} rechazada.")
            solicitud.delete()  # Eliminar la solicitud tras procesarla
        except SolicitudEntrenador.DoesNotExist:
            messages.error(request, "Solicitud no encontrada.")
        return redirect('gestionar_entrenadores')

    return render(request, 'gestionar_entrenadores.html', {
    'solicitudes_pendientes': solicitudes_pendientes,
    'total_solicitudes': total_solicitudes,
})



@login_required
def ver_perfil_entrenador(request):
    """
    Verifica si el usuario tiene un perfil de entrenador.
    Si no lo tiene, muestra un error. 
    De lo contrario, renderiza el perfil del entrenador.
    """
    if not hasattr(request.user, 'entrenador'):
        # Si el usuario no es entrenador, mostrar un mensaje de error
        return render(request, 'error.html', {
            'message': 'No tienes acceso al perfil de entrenador porque no eres un entrenador.'
        })

    # Renderizar el perfil del entrenador
    entrenador = request.user.entrenador
    return render(request, 'ver_perfilEntrenador.html', {
        'entrenador': entrenador,
        'user': request.user,
    })


@login_required
def editar_perfil_entrenador(request):
    if not hasattr(request.user, 'entrenador'):
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')

    entrenador = request.user.entrenador

    if request.method == 'POST':
        entrenador.nombre = request.POST.get('nombre', entrenador.nombre)
        entrenador.apellidos = request.POST.get('apellidos', entrenador.apellidos)
        entrenador.genero = request.POST.get('genero', entrenador.genero)
        entrenador.nivel_experiencia = request.POST.get('nivel_experiencia', entrenador.nivel_experiencia)
        entrenador.especialidades = request.POST.get('especialidades', entrenador.especialidades)
        entrenador.experiencia = request.POST.get('experiencia', entrenador.experiencia)
        entrenador.formacion = request.POST.get('formacion', entrenador.formacion)
        entrenador.plazas_abiertas = request.POST.get('plazas_abiertas', entrenador.plazas_abiertas)

        # Guardar el avatar si se sube uno nuevo
        if 'avatar' in request.FILES:
            entrenador.avatar = request.FILES['avatar']

        entrenador.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('ver_perfil_entrenador')
    
    context = {
        'entrenador': entrenador
    }
    return render(request, 'editar_perfilEntrenador.html', context)

from .forms import SolicitudEntrenamientoForm  # Creamos este formulario en el siguiente paso


from django.template.context_processors import request
from django.shortcuts import render
from .context_processors import solicitudes_pendientes_context  # Importa el context processor

@login_required
def listar_entrenadores(request):
    # Obtener entrenadores aprobados y con plazas disponibles
    entrenadores_disponibles = Entrenador.objects.filter(aprobado_por_admin=True, plazas_abiertas__gt=0)

    # Obtener entrenadores con los que el usuario ya tiene un entrenamiento activo
    entrenadores_entrenados = Entrenamiento.objects.filter(usuario=request.user).values_list('entrenador_id', flat=True)

    # Excluir entrenadores con los que ya está entrenando
    entrenadores = entrenadores_disponibles.exclude(id__in=entrenadores_entrenados)

    # Obtener entrenadores a los que el usuario ha enviado una solicitud sin respuesta
    solicitudes_pendientes = SolicitudEntrenamiento.objects.filter(
        usuario=request.user, respuesta_recibida=False
    ).values_list("entrenador_id", flat=True)

    if request.method == "POST":
        entrenador_id = request.POST.get("entrenador")
        mensaje = request.POST.get("mensaje")

        if entrenador_id and mensaje:
            entrenador = Entrenador.objects.get(id=entrenador_id)

            # Verificar si el usuario ya tiene una solicitud pendiente con este entrenador
            if int(entrenador_id) in solicitudes_pendientes:
                messages.warning(
                    request, "⚠️ Ya has enviado una solicitud a este entrenador, debes esperar su respuesta para enviar otra."
                )
            else:
                SolicitudEntrenamiento.objects.create(
                    usuario=request.user, entrenador=entrenador, mensaje=mensaje
                )
                messages.success(request, "✅ ¡Tu solicitud ha sido enviada con éxito!")

            return redirect("listar_entrenadores")

    # 🔥 Obtener el contexto del *context processor* manualmente
    context = {
        "entrenadores": entrenadores,
        "solicitudes_pendientes": list(solicitudes_pendientes),
    }
    context.update(solicitudes_pendientes_context(request))  # Agregar el contexto global

    return render(request, "listar_entrenadores.html", context)



@login_required
def listar_solicitudes_entrenador(request):
    """Muestra las solicitudes de entrenamiento recibidas por un entrenador"""
    if not hasattr(request.user, 'entrenador'):
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('home')

    entrenador = request.user.entrenador
    solicitudes = SolicitudEntrenamiento.objects.filter(entrenador=entrenador).order_by('-fecha_envio')

    return render(request, 'listar_solicitudes_entrenador.html', {
        'solicitudes': solicitudes,
        'entrenador': entrenador
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SolicitudEntrenamiento, Entrenamiento, Entrenador

@login_required
def gestionar_solicitud_entrenamiento(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudEntrenamiento, id=solicitud_id)

    # Verificar que el usuario sea el entrenador que recibió la solicitud
    if solicitud.entrenador.user != request.user:
        messages.error(request, "No tienes permisos para gestionar esta solicitud.")
        return redirect("listar_solicitudes_entrenador")

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "aceptar":
            entrenador = solicitud.entrenador

            # Verificar si aún hay vacantes
            if entrenador.plazas_abiertas > 0:
                # Restar una vacante
                entrenador.plazas_abiertas -= 1
                entrenador.save()

                # 🔥 Verificar si ya existe el entrenamiento
                if not Entrenamiento.objects.filter(usuario=solicitud.usuario, entrenador=entrenador).exists():
                    # Crear el entrenamiento
                    Entrenamiento.objects.create(usuario=solicitud.usuario, entrenador=entrenador)
                    messages.success(request, f"✅ Has aceptado a {solicitud.usuario.username} como tu alumno.")

                # Marcar la solicitud como respondida y eliminarla
                solicitud.delete()

            else:
                messages.warning(request, "⚠️ No tienes vacantes disponibles.")

        elif accion == "rechazar":
            solicitud.delete()
            messages.info(request, f"❌ Has rechazado la solicitud de {solicitud.usuario.username}.")

    return redirect("listar_solicitudes_entrenador")

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Entrenamiento

@login_required
def listar_usuarios_entrenados(request):
    if hasattr(request.user, 'entrenador'):
        usuarios_entrenados = Entrenamiento.objects.filter(entrenador=request.user.entrenador)
    else:
        usuarios_entrenados = []

    return render(request, "listar_usuarios_entrenados.html", {
        "usuarios_entrenados": usuarios_entrenados
    })

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

@login_required
def eliminar_usuario_entrenado(request, entrenamiento_id):
    entrenamiento = get_object_or_404(Entrenamiento, id=entrenamiento_id)

    # Verificar que el usuario es el entrenador
    if entrenamiento.entrenador.user != request.user:
        messages.error(request, "No tienes permisos para eliminar este usuario.")
        return redirect("listar_usuarios_entrenados")

    # Obtener el entrenador antes de eliminar el entrenamiento
    entrenador = entrenamiento.entrenador

    # Eliminar la relación de entrenamiento
    entrenamiento.delete()

    # Aumentar el número de vacantes en 1
    entrenador.plazas_abiertas += 1
    entrenador.save()

    messages.success(request, "✅ Usuario eliminado de tu lista de entrenamientos. Vacante disponible aumentada en 1.")

    return redirect("listar_usuarios_entrenados")

# ---------------------------------------------------------
#                  SECCION GRUPOS
# ---------------------------------------------------------
@login_required
def listar_grupos(request):
    query = request.GET.get('q', '')  # Obtén el parámetro de búsqueda 'q'
    if query:
        grupos = Grupo.objects.filter(nombre__icontains=query)
    else:
        grupos = Grupo.objects.all()

    grupos_con_notificaciones = []
    for grupo in grupos:
        es_miembro = request.user in grupo.miembros.all()
        mensajes_no_leidos = 0

        if es_miembro:
            ultima_visita = GrupoVisitado.objects.filter(usuario=request.user, grupo=grupo).first()
            if ultima_visita:
                mensajes_no_leidos = MensajeGrupo.objects.filter(
                    grupo=grupo,
                    fecha_creacion__gt=ultima_visita.ultima_visita
                ).exclude(usuario=request.user).count()
            else:
                mensajes_no_leidos = MensajeGrupo.objects.filter(grupo=grupo).exclude(usuario=request.user).count()

        grupos_con_notificaciones.append({
            'grupo': grupo,
            'mensajes_no_leidos': mensajes_no_leidos,
            'es_miembro': es_miembro
        })

    return render(request, 'listar_grupos.html', {
        'grupos_con_notificaciones': grupos_con_notificaciones,
        'query': query,
    })


import logging

logger = logging.getLogger(__name__)

@login_required
def detalles_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    mensajes = MensajeGrupo.objects.filter(grupo=grupo).order_by('fecha_creacion')
    es_miembro = request.user in grupo.miembros.all()

    logger.info(f"Acceso al grupo {grupo_id} por {request.user.username}")
    logger.info(f"Mensajes no leídos antes de procesar: {MensajeGrupo.objects.filter(grupo=grupo, leido=False, usuario=request.user).count()}")

    if request.method == "POST":
        if not es_miembro:
            messages.error(request, "No puedes enviar mensajes porque no eres miembro del grupo.")
            return redirect('detalles_grupo', grupo_id=grupo_id)

        contenido = request.POST.get('mensaje')
        if contenido:
            MensajeGrupo.objects.create(grupo=grupo, usuario=request.user, contenido=contenido)
            messages.success(request, "Mensaje enviado correctamente.")
            return redirect('detalles_grupo', grupo_id=grupo_id)

    # Marcar mensajes como leídos
    MensajeGrupo.objects.filter(grupo=grupo, leido=False, usuario=request.user).update(leido=True)
    logger.info(f"Mensajes no leídos después de procesar: {MensajeGrupo.objects.filter(grupo=grupo, leido=False, usuario=request.user).count()}")

    return render(request, 'detalles_grupo.html', {'grupo': grupo, 'mensajes': mensajes, 'es_miembro': es_miembro})


@login_required
def actualizar_visita_grupo(request, grupo_id):
    if request.method == "POST":
        grupo = get_object_or_404(Grupo, id=grupo_id)
        GrupoVisitado.objects.update_or_create(
            usuario=request.user,
            grupo=grupo,
            defaults={'ultima_visita': timezone.now()}
        )
        return JsonResponse({"status": "success", "message": "Visita actualizada"}, status=200)
    return JsonResponse({"status": "error", "message": "Método no permitido"}, status=405)

@login_required
def crear_grupo(request):
    if request.method == "POST":
        form = GrupoForm(request.POST, request.FILES)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            if Grupo.objects.filter(nombre=nombre).exists():
                form.add_error('nombre', 'Ya existe un grupo con este nombre.')
            else:
                grupo = form.save(commit=False)
                grupo.creador = request.user
                if not grupo.imagen:
                    grupo.imagen = 'imgs/default-group.png'
                grupo.save()
                grupo.miembros.add(request.user)
                return redirect('listar_grupos')
    else:
        form = GrupoForm()
    return render(request, 'crear_grupo.html', {'form': form})

@login_required
def unirse_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    if request.user not in grupo.miembros.all():
        grupo.miembros.add(request.user)
        messages.success(request, f'Te has unido al grupo "{grupo.nombre}".')
    else:
        messages.warning(request, f'Ya eres miembro del grupo "{grupo.nombre}".')
    return redirect('detalles_grupo', grupo_id=grupo.id)

@login_required
def salir_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    if request.user in grupo.miembros.all():
        grupo.miembros.remove(request.user)
        messages.success(request, f'Saliste del grupo "{grupo.nombre}".')
    else:
        messages.warning(request, f'No eres miembro del grupo "{grupo.nombre}".')
    return redirect('detalles_grupo', grupo_id=grupo_id)

@login_required
def eliminar_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    if grupo.creador != request.user:
        return HttpResponseForbidden("No tienes permiso para eliminar este grupo.")
    
    grupo.delete()
    messages.success(request, f"El grupo '{grupo.nombre}' ha sido eliminado correctamente.")
    return redirect('listar_grupos')
# ---------------------------------------------------------
#                  SECCION RED SOCIAL
# ---------------------------------------------------------
@login_required
def social_home(request):
    return render(request, 'social_home.html')


@login_required
def mi_perfil(request):
    grupos_creados = Grupo.objects.filter(creador=request.user)
    grupos_perteneces = Grupo.objects.filter(miembros=request.user).exclude(creador=request.user)
    
    perfil_usuario = request.user.perfilusuario
    es_entrenador = hasattr(request.user, 'entrenador')
    entrenador = request.user.entrenador if es_entrenador else None

    # Actividades actuales y pasadas
    actividades_actuales = Actividad.objects.filter(participantes=request.user, fecha_hora__gte=now())
    actividades_pasadas = Actividad.objects.filter(participantes=request.user, fecha_hora__lt=now())

    # Publicaciones del usuario
    publicaciones_usuario = Publicacion.objects.filter(autor=request.user).order_by('-fecha_creacion')

    return render(request, 'mi_perfil.html', {
        'grupos_creados': grupos_creados,
        'grupos_perteneces': grupos_perteneces,
        'perfil_usuario': perfil_usuario,
        'es_entrenador': es_entrenador,
        'entrenador': entrenador,
        'actividades_actuales': actividades_actuales,
        'actividades_pasadas': actividades_pasadas,
        'publicaciones_usuario': publicaciones_usuario,
    })


@login_required
def detalles_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    mensajes = MensajeGrupo.objects.filter(grupo=grupo).order_by('fecha_creacion')  # Orden ascendente
    es_miembro = request.user in grupo.miembros.all()

    if request.method == "POST":
        if not es_miembro:
            messages.error(request, "No puedes enviar mensajes porque no eres miembro del grupo.")
            return redirect('detalles_grupo', grupo_id=grupo_id)

        contenido = request.POST.get('mensaje')
        if contenido:
            MensajeGrupo.objects.create(grupo=grupo, usuario=request.user, contenido=contenido)
            messages.success(request, "Mensaje enviado correctamente.")
            return redirect('detalles_grupo', grupo_id=grupo_id)

    return render(request, 'detalles_grupo.html', {
        'grupo': grupo,
        'mensajes': mensajes,
        'es_miembro': es_miembro,
    })

@login_required
def editar_mensaje_grupo(request, mensaje_id):
    mensaje = get_object_or_404(MensajeGrupo, id=mensaje_id)

    if mensaje.usuario != request.user and not request.user.is_staff:
        return HttpResponseForbidden("No tienes permiso para editar este mensaje.")

    if request.method == 'POST':
        nuevo_contenido = request.POST.get('contenido')
        if nuevo_contenido:
            mensaje.contenido = nuevo_contenido
            mensaje.editado = True
            mensaje.save()
            messages.success(request, "Mensaje editado correctamente.")
        return redirect('detalles_grupo', grupo_id=mensaje.grupo.id)

    return render(request, 'editar_mensaje_grupo.html', {'mensaje': mensaje})

@login_required
def eliminar_mensaje_grupo(request, mensaje_id):
    mensaje = get_object_or_404(MensajeGrupo, id=mensaje_id)

    if mensaje.usuario != request.user and not request.user.is_staff:
        return HttpResponseForbidden("No tienes permiso para eliminar este mensaje.")

    grupo_id = mensaje.grupo.id
    mensaje.delete()
    messages.success(request, "Mensaje eliminado correctamente.")
    return redirect('detalles_grupo', grupo_id=grupo_id)

@login_required
def editar_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)

    if grupo.creador != request.user and not request.user.is_staff:
        return HttpResponseForbidden("No tienes permiso para editar este grupo.")

    if request.method == 'POST':
        form = GrupoForm(request.POST, request.FILES, instance=grupo)
        if form.is_valid():
            form.save()
            messages.success(request, "Información del grupo actualizada.")
            return redirect('detalles_grupo', grupo_id=grupo_id)

    form = GrupoForm(instance=grupo)
    return render(request, 'editar_grupo.html', {'form': form, 'grupo': grupo})


# ---------------------------------------------------------
#                  SECCION ACTIVIDAD
# ---------------------------------------------------------
import calendar
from datetime import datetime

def calendario(request, year=None, month=None):
    # Obtener el mes actual si no se proporciona
    if not year or not month:
        today = now()
        year = today.year
        month = today.month

    # Generar los días del mes con eventos
    _, num_days = monthrange(year, month)
    days_with_events = []
    for day in range(1, num_days + 1):
        actividades = Actividad.objects.filter(
            fecha_hora__year=year,
            fecha_hora__month=month,
            fecha_hora__day=day
        )
        day_of_week = calendar.day_name[datetime(year, month, day).weekday()]  # Nombre del día
        days_with_events.append({
            'day': day,
            'event': len(actividades),
            'is_today': (date.today().year == year and date.today().month == month and date.today().day == day),
            'is_empty': len(actividades) == 0,
            'day_name': day_of_week,
        })

    # Contexto para la plantilla
    context = {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],  # Nombre del mes
        'days_with_events': days_with_events,
        'prev_year': year if month > 1 else year - 1,
        'prev_month': month - 1 if month > 1 else 12,
        'next_year': year if month < 12 else year + 1,
        'next_month': month + 1 if month < 12 else 1,
    }

    return render(request, 'calendar.html', context)

def dia_actividades(request, year, month, day):
    query = request.GET.get('q', '')
    actividades = Actividad.objects.filter(
        fecha_hora__year=year,
        fecha_hora__month=month,
        fecha_hora__day=day
    )
    
    if query:
        actividades = actividades.filter(nombre__icontains=query)

    context = {
        'selected_date': f"{day}/{month}/{year}",
        'eventos': actividades,
        'year': year,
        'month': month,
        'day': day,
    }
    return render(request, 'day_events.html', context)

def crear_actividad(request):
    if request.method == "POST":
        form = ActividadForm(request.POST, request.FILES)
        if form.is_valid():
            actividad = form.save(commit=False)
            actividad.creado_por = request.user

            if 'imagen' in request.FILES:
                actividad.imagen = request.FILES['imagen']

            actividad.save()
            actividad.participantes.add(request.user)
            ChatActividad.objects.create(actividad=actividad)
            messages.success(request, f"Actividad '{actividad.nombre}' creada exitosamente.")
            return redirect('calendar', year=now().year, month=now().month)
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        form = ActividadForm()
    return render(request, 'crear_actividad.html', {'form': form, 'now': now()})

from django.utils.timezone import now


from django.contrib import messages

@login_required
def unirse_actividad(request, actividad_id):
    actividad = get_object_or_404(Actividad, id=actividad_id)
    if actividad.limite_participantes and actividad.participantes.count() >= actividad.limite_participantes:
        messages.error(request, "La actividad ya ha alcanzado su límite de participantes.")
    else:
        actividad.participantes.add(request.user)
        messages.success(request, f"Te has unido a la actividad '{actividad.nombre}'.")
    return redirect('calendar', year=actividad.fecha_hora.year, month=actividad.fecha_hora.month)


@login_required
def abandonar_actividad(request, actividad_id):
    actividad = get_object_or_404(Actividad, id=actividad_id)
    if request.user in actividad.participantes.all():
        actividad.participantes.remove(request.user)
        messages.success(request, f"Has abandonado la actividad '{actividad.nombre}'.")
    else:
        messages.error(request, "No estás inscrito en esta actividad.")
    return redirect('calendar', year=actividad.fecha_hora.year, month=actividad.fecha_hora.month)


@login_required
def chat_actividad(request, actividad_id):
    actividad = get_object_or_404(Actividad, id=actividad_id)
    chat = actividad.chat
    mensajes = MensajeActividad.objects.filter(chat=chat).order_by('fecha_envio')

    if request.method == "POST":
        contenido = request.POST.get('mensaje')
        if contenido:
            MensajeActividad.objects.create(chat=chat, usuario=request.user, contenido=contenido)
            messages.success(request, "Mensaje enviado.")
        return redirect('chat_actividad', actividad_id=actividad_id)

    return render(request, 'chat_actividad.html', {'actividad': actividad, 'mensajes': mensajes})


@login_required
def detalles_actividad(request, actividad_id):
    actividad = get_object_or_404(Actividad, id=actividad_id)
    mensajes = MensajeActividad.objects.filter(chat=actividad.chat).order_by('fecha_envio')
    es_miembro = request.user in actividad.participantes.all()
    es_creador = request.user == actividad.creado_por

    # Extraer la fecha de la actividad
    year = actividad.fecha_hora.year
    month = actividad.fecha_hora.month
    day = actividad.fecha_hora.day

    # Verificar si la actividad ya ha finalizado
    actividad_finalizada = actividad.fecha_hora < now()

    if request.method == "POST":
        action = request.POST.get('action')

        if action == "join" and not actividad_finalizada:
            if actividad.limite_participantes and actividad.participantes.count() >= actividad.limite_participantes:
                messages.error(request, "La actividad ya ha alcanzado su límite de participantes.")
            else:
                actividad.participantes.add(request.user)
                messages.success(request, f"Te has unido a la actividad '{actividad.nombre}'.")

        elif action == "leave":
            if es_miembro:
                actividad.participantes.remove(request.user)
                messages.success(request, f"Has abandonado la actividad '{actividad.nombre}'.")
            else:
                messages.error(request, "No estás inscrito en esta actividad.")

        elif action == "delete" and es_creador:
            actividad.delete()
            messages.success(request, f"La actividad '{actividad.nombre}' ha sido eliminada.")
            return redirect('calendar', year=now().year, month=now().month)
        
        elif action == "send_message":
            contenido = request.POST.get('mensaje')
            if es_miembro and contenido:
                MensajeActividad.objects.create(chat=actividad.chat, usuario=request.user, contenido=contenido)
                messages.success(request, "Mensaje enviado.")
            elif not es_miembro:
                messages.error(request, "Debes ser participante de la actividad para enviar mensajes.")
            else:
                messages.error(request, "No se puede enviar un mensaje vacío.")

        return redirect('detalles_actividad', actividad_id=actividad.id)

    return render(request, 'detalles_actividad.html', {
        'actividad': actividad,
        'mensajes': mensajes,
        'es_miembro': es_miembro,
        'es_creador': es_creador,
        'year': year,
        'month': month,
        'day': day,
        'actividad_finalizada': actividad_finalizada,  # ✅ Se pasa esta variable a la plantilla
    })


@login_required
def editar_mensaje_actividad(request, mensaje_id):
    mensaje = get_object_or_404(MensajeActividad, id=mensaje_id)

    if mensaje.usuario != request.user and not request.user.is_staff:
        return HttpResponseForbidden("No tienes permiso para editar este mensaje.")

    if request.method == 'POST':
        nuevo_contenido = request.POST.get('contenido')
        if nuevo_contenido:
            mensaje.contenido = nuevo_contenido
            mensaje.editado = True
            mensaje.save()
            messages.success(request, "Mensaje editado correctamente.")
        return redirect('detalles_actividad', actividad_id=mensaje.chat.actividad.id)

    return render(request, 'editar_mensaje_actividad.html', {'mensaje': mensaje})

@login_required
def eliminar_mensaje_actividad(request, mensaje_id):
    mensaje = get_object_or_404(MensajeActividad, id=mensaje_id)

    if mensaje.usuario != request.user and not request.user.is_staff:
        return HttpResponseForbidden("No tienes permiso para eliminar este mensaje.")

    actividad_id = mensaje.chat.actividad.id
    mensaje.delete()
    messages.success(request, "Mensaje eliminado correctamente.")
    return redirect('detalles_actividad', actividad_id=actividad_id)

def editar_actividad(request, actividad_id):
    actividad = get_object_or_404(Actividad, id=actividad_id)
    if request.method == 'POST':
        form = ActividadForm(request.POST, request.FILES, instance=actividad)
        if form.is_valid():
            form.save()
            messages.success(request, "Actividad actualizada correctamente.")
            return redirect('detalles_actividad', actividad_id=actividad.id)
        else:
            # Si hay errores, mostrarlos en la plantilla
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = ActividadForm(instance=actividad)
    return render(request, 'editar_actividad.html', {'form': form, 'actividad': actividad})

# ---------------------------------------------------------
#              SECCION MENSAJES PRIVADOS
# ---------------------------------------------------------
from django.db.models import Q

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from .models import User, Entrenamiento, MensajePrivado

@login_required
def mensajes_directos(request):
    usuario_actual = request.user

    if usuario_actual.is_staff:
        # 🔥 Administradores ven a todos los usuarios y entrenadores
        usuarios_disponibles = User.objects.exclude(id=usuario_actual.id)
    
    elif hasattr(usuario_actual, 'entrenador'):
        # 🔥 Entrenadores ven a TODOS los entrenadores + usuarios que entrenan + administradores
        usuarios_entrenados = Entrenamiento.objects.filter(entrenador=usuario_actual.entrenador).values_list('usuario', flat=True)
        usuarios_disponibles = User.objects.filter(
            Q(is_staff=True) |  # Admins
            Q(id__in=usuarios_entrenados) |  # Usuarios entrenados
            Q(id__in=User.objects.filter(entrenador__isnull=False))  # TODOS los entrenadores
        ).exclude(id=usuario_actual.id)
    
    else:
        # 🔥 Usuarios ven: Administradores + Entrenadores que los entrenan + Otros usuarios
        entrenadores_aceptados = Entrenamiento.objects.filter(usuario=usuario_actual).values_list('entrenador__user_id', flat=True)
        usuarios_disponibles = User.objects.filter(
            Q(is_staff=True) |  # Admins
            Q(id__in=entrenadores_aceptados) |  # Entrenadores del usuario
            Q(id__in=User.objects.filter(entrenador=None))  # Otros usuarios
        ).exclude(id=usuario_actual.id)

    usuarios_list = [
        {
            'usuario': usuario,
            'es_entrenador': hasattr(usuario, 'entrenador') and usuario.entrenador.aprobado_por_admin,
            'es_admin': usuario.is_staff,
        }
        for usuario in usuarios_disponibles
    ]

    # 🔥 Obtener las conversaciones activas
    conversaciones = []
    mensajes = MensajePrivado.objects.filter(Q(remitente=usuario_actual) | Q(destinatario=usuario_actual)).distinct()

    for mensaje in mensajes:
        otro_usuario = mensaje.remitente if mensaje.destinatario == usuario_actual else mensaje.destinatario
        if not any(c['otro_usuario'] == otro_usuario for c in conversaciones):
            mensajes_no_leidos = MensajePrivado.objects.filter(remitente=otro_usuario, destinatario=usuario_actual, leido=False).count()
            conversaciones.append({
                'otro_usuario': otro_usuario,
                'mensajes_no_leidos': mensajes_no_leidos,
                'es_entrenador': hasattr(otro_usuario, 'entrenador') and otro_usuario.entrenador.aprobado_por_admin,
                'es_admin': otro_usuario.is_staff,
            })

    return render(request, 'mensajes_directos.html', {
        'usuarios': usuarios_list,
        'conversaciones': conversaciones,
    })





@login_required
def enviar_mensaje(request, usuario_id):
    destinatario = get_object_or_404(User, id=usuario_id)
    if request.method == 'POST':
        contenido = request.POST.get('contenido')
        if contenido:
            MensajePrivado.objects.create(
                remitente=request.user,
                destinatario=destinatario,
                contenido=contenido
            )
            return redirect('detalle_conversacion', usuario_id=usuario_id)
    return render(request, 'enviar_mensaje.html', {'destinatario': destinatario})

@login_required
def detalle_conversacion(request, usuario_id):
    otro_usuario = get_object_or_404(User, id=usuario_id)
    mensajes = MensajePrivado.objects.filter(
        (models.Q(remitente=request.user) & models.Q(destinatario=otro_usuario)) |
        (models.Q(remitente=otro_usuario) & models.Q(destinatario=request.user))
    ).order_by('fecha_envio')

    MensajePrivado.objects.filter(destinatario=request.user, remitente=otro_usuario, leido=False).update(leido=True)

    if request.method == "POST":
        contenido = request.POST.get('contenido')
        if contenido:
            MensajePrivado.objects.create(
                remitente=request.user,
                destinatario=otro_usuario,
                contenido=contenido
            )
            return redirect('detalle_conversacion', usuario_id=usuario_id)

    return render(request, 'detalles_conversacion.html', {
        'mensajes': mensajes,
        'otro_usuario': otro_usuario
    })

@login_required
def editar_mensaje_privado(request, mensaje_id):
    mensaje = get_object_or_404(MensajePrivado, id=mensaje_id)

    if mensaje.remitente != request.user:
        return HttpResponseForbidden("No tienes permiso para editar este mensaje.")

    if request.method == 'POST':
        nuevo_contenido = request.POST.get('contenido')
        if nuevo_contenido:
            mensaje.contenido = nuevo_contenido
            mensaje.editado = True
            mensaje.save()
            messages.success(request, "Mensaje editado correctamente.")
        return redirect('detalle_conversacion', usuario_id=mensaje.destinatario.id)

    return render(request, 'editar_mensaje_privado.html', {'mensaje': mensaje})


@login_required
def eliminar_mensaje_privado(request, mensaje_id):
    mensaje = get_object_or_404(MensajePrivado, id=mensaje_id)

    if mensaje.remitente != request.user:
        return HttpResponseForbidden("No tienes permiso para eliminar este mensaje.")

    destinatario_id = mensaje.destinatario.id
    mensaje.delete()
    messages.success(request, "Mensaje eliminado correctamente.")
    return redirect('detalle_conversacion', usuario_id=destinatario_id)

# ---------------------------------------------------------
#                  SECCION PUBLICACIONES
# ---------------------------------------------------------
@login_required
def social_home(request):
    publicaciones = Publicacion.objects.all().order_by('-fecha_creacion')

    # Añadir atributo personalizado a las publicaciones
    for publicacion in publicaciones:
        publicacion.user_liked = publicacion.likes.filter(usuario=request.user).exists()
        # Marcar como destacada si el autor es un entrenador aprobado
        publicacion.es_destacada = (
            hasattr(publicacion.autor, 'entrenador') and 
            publicacion.autor.entrenador.aprobado_por_admin
        )

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            publicacion_id = request.POST.get('publicacion_id')
            publicacion = get_object_or_404(Publicacion, id=publicacion_id)
            comentario = form.save(commit=False)
            comentario.publicacion = publicacion
            comentario.autor = request.user
            comentario.save()
            return redirect('social_home')

    return render(request, 'social_home.html', {
        'publicaciones': publicaciones,
        'form_comentario': ComentarioForm(),
    })

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@login_required
@csrf_exempt
def dar_like(request, publicacion_id):
    if request.method == "POST":
        publicacion = get_object_or_404(Publicacion, id=publicacion_id)
        like, created = Like.objects.get_or_create(publicacion=publicacion, usuario=request.user)
        if not created:  # Si ya existía el like, lo elimina
            like.delete()
            user_liked = False
        else:
            user_liked = True
        return JsonResponse({
            "success": True,
            "like_count": publicacion.likes.count(),
            "user_liked": user_liked,
        })
    return JsonResponse({"success": False}, status=400)

@login_required
def crear_comentario(request, publicacion_id):
    if request.method == "POST":
        contenido = json.loads(request.body).get("contenido")
        if contenido:
            comentario = Comentario.objects.create(
                publicacion_id=publicacion_id,
                autor=request.user,
                contenido=contenido
            )
            return JsonResponse({
                "success": True,
                "comentario_id": comentario.id,
                "comentario_autor": comentario.autor.username,
                "comentario_contenido": comentario.contenido,
                "fecha_creacion": comentario.fecha_creacion.strftime("%d %b %Y %H:%M")
            })
    return JsonResponse({"success": False}, status=400)

@login_required
def crear_publicacion(request):
    if request.method == 'POST':
        form = PublicacionForm(request.POST, request.FILES)
        if form.is_valid():
            publicacion = form.save(commit=False)
            publicacion.autor = request.user
            # Destacar la publicación si el autor es un entrenador aprobado
            if hasattr(request.user, 'entrenador') and request.user.entrenador.aprobado_por_admin:
                publicacion.destacado = True
            publicacion.save()
            messages.success(request, "Publicación creada exitosamente.")
            return redirect('social_home')
    else:
        form = PublicacionForm()

    return render(request, 'crear_publicacion.html', {'form': form})


@login_required
@csrf_exempt
def eliminar_publicacion(request, publicacion_id):
    if request.method == "DELETE":
        publicacion = get_object_or_404(Publicacion, id=publicacion_id, autor=request.user)
        publicacion.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)

@login_required
def editar_publicacion(request, publicacion_id):
    publicacion = get_object_or_404(Publicacion, id=publicacion_id, autor=request.user)

    if request.method == "POST":
        contenido = request.POST.get("contenido", publicacion.contenido)
        imagen = request.FILES.get("imagen", publicacion.imagen)
        video = request.FILES.get("video", publicacion.video)

        publicacion.contenido = contenido
        publicacion.imagen = imagen
        publicacion.video = video
        publicacion.save()

        messages.success(request, "Publicación actualizada correctamente.")
        return redirect("social_home")

    return render(request, "editar_publicacion.html", {"publicacion": publicacion})

@login_required
@csrf_exempt
def eliminar_comentario(request, comentario_id):
    if request.method == "DELETE":
        comentario = get_object_or_404(Comentario, id=comentario_id, autor=request.user)
        comentario.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)



from django.shortcuts import redirect, get_object_or_404
@login_required
def editar_comentario(request, comentario_id):
    try:
        comentario = get_object_or_404(Comentario, id=comentario_id)
        if request.method == "POST":
            contenido = request.POST.get("contenido", "").strip()
            if contenido:
                comentario.contenido = contenido
                comentario.save()
                return redirect(f"/comunidad/#comentario-{comentario.id}")
    except Http404:
        return redirect("/comunidad/")  # Si el comentario no existe, redirige a la comunidad

    return render(request, "editar_comentario.html", {"comentario": comentario})

@login_required
def detalle_publicacion(request, publicacion_id):
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    comentarios = Comentario.objects.filter(publicacion=publicacion).order_by('-fecha_creacion')

    return render(request, 'detalle_publicacion.html', {
        'publicacion': publicacion,
        'comentarios': comentarios,
    })

# ---------------------------------------------------------
#              SECCION RETOS
# ---------------------------------------------------------
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CrearRetoForm

def crear_reto(request):
    # Permitir acceso a administradores y entrenadores aprobados
    if not request.user.is_staff and (not hasattr(request.user, 'entrenador') or not request.user.entrenador.aprobado_por_admin):
        messages.error(request, "Solo los administradores o entrenadores aprobados pueden crear retos.")
        return HttpResponseForbidden("No tienes permisos para crear retos.")

    if request.method == "POST":
        form = CrearRetoForm(request.POST, request.FILES)  # Añadimos request.FILES para archivos
        if form.is_valid():
            reto = form.save(commit=False)
            reto.creador = request.user  # Asignamos el creador al usuario logueado
            reto.save()
            messages.success(request, f"Reto '{reto.nombre}' creado exitosamente.")
            return redirect('listar_retos')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = CrearRetoForm()

    return render(request, 'crear_reto.html', {'form': form})


from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Reto

@login_required
def listar_retos(request):
    # Obtener el parámetro de búsqueda (si existe)
    query = request.GET.get('q', '').strip()

    if query:
        # Filtrar retos activos y finalizados según el término de búsqueda
        retos_activos = Reto.objects.filter(
            fecha_fin__gte=now(),
            nombre__icontains=query
        ).order_by('fecha_inicio', 'fecha_fin')  # Ordenar retos activos
        retos_finalizados = Reto.objects.filter(
            fecha_fin__lt=now(),
            nombre__icontains=query
        ).order_by('fecha_inicio', 'fecha_fin')  # Ordenar retos finalizados
    else:
        # Si no hay búsqueda, mostrar todos los retos
        retos_activos = Reto.objects.filter(fecha_fin__gte=now()).order_by('fecha_inicio', 'fecha_fin')
        retos_finalizados = Reto.objects.filter(fecha_fin__lt=now()).order_by('fecha_inicio', 'fecha_fin')

    # Verificar si el usuario es un entrenador aprobado
    es_entrenador_aprobado = (
        request.user.is_authenticated
        and hasattr(request.user, 'entrenador')
        and request.user.entrenador.aprobado_por_admin
    )

    return render(request, 'listar_retos.html', {
        'retos_activos': retos_activos,
        'retos_finalizados': retos_finalizados,
        'es_entrenador_aprobado': es_entrenador_aprobado,
        'query': query,  # Pasar la búsqueda al contexto
    })



@login_required
def unirse_reto(request, reto_id):
    reto = get_object_or_404(Reto, id=reto_id)
    if not reto.esta_activo():
        messages.error(request, "El reto no está activo.")
        return redirect('listar_retos')

    participacion, created = ParticipacionReto.objects.get_or_create(usuario=request.user, reto=reto)
    if created:
        messages.success(request, f"Te has unido al reto: {reto.nombre}")
    else:
        messages.warning(request, "Ya estás participando en este reto.")
    return redirect('listar_retos')


from .forms import RegistrarProgresoForm

@login_required
def ver_ranking(request, reto_id):
    reto = get_object_or_404(Reto, id=reto_id)
    participacion = ParticipacionReto.objects.filter(usuario=request.user, reto=reto).first()

    if request.method == 'POST' and reto.esta_activo():
        form = RegistrarProgresoForm(request.POST)
        if form.is_valid():
            progreso = form.cleaned_data['progreso']
            unidad = form.cleaned_data['unidad']

            # Crear participación si no existe
            if not participacion:
                participacion = ParticipacionReto.objects.create(
                    usuario=request.user,
                    reto=reto,
                    progreso_acumulado=0,
                    unidad=unidad,
                )

            participacion.progreso_acumulado += progreso
            participacion.unidad = unidad
            participacion.save()

            # ** Notificaciones automáticas **
            porcentaje_progreso = (participacion.progreso_acumulado / reto.objetivo) * 100

            # Priorizar notificación del 100% sobre el 50%
            if porcentaje_progreso >= 100:
                # Crear notificación solo si no existe previamente
                Notificacion.objects.get_or_create(
                    usuario=request.user,
                    mensaje=f"¡Felicidades! Has completado el reto '{reto.nombre}'."
                )
            elif porcentaje_progreso >= 50:
                # Crear notificación solo si no existe previamente
                Notificacion.objects.get_or_create(
                    usuario=request.user,
                    mensaje=f"¡Genial! Has alcanzado el 50% del objetivo en el reto '{reto.nombre}'."
                )

            messages.success(request, f"Se ha registrado tu progreso de {progreso} {unidad}.")
        else:
            messages.error(request, "Por favor, completa el formulario correctamente.")
        return redirect('ver_ranking', reto_id=reto_id)

    # Obtener la última notificación relacionada con este reto
    notificaciones = Notificacion.objects.filter(usuario=request.user, mensaje__icontains=reto.nombre).order_by('-fecha')[:1]

    ranking = ParticipacionReto.objects.filter(reto=reto).order_by('-progreso_acumulado')
    form = RegistrarProgresoForm()

    return render(request, 'ver_ranking.html', {
        'reto': reto,
        'ranking': ranking,
        'form': form,
        'notificaciones': notificaciones,
    })



@login_required
def editar_reto(request, reto_id):
    reto = get_object_or_404(Reto, id=reto_id)

    # Permitir editar solo al creador o a los administradores
    if reto.creador != request.user and not request.user.is_staff:
        return HttpResponseForbidden("No tienes permiso para editar este reto.")

    if request.method == "POST":
        form = CrearRetoForm(request.POST, request.FILES, instance=reto)
        if form.is_valid():
            form.save()
            messages.success(request, "Reto actualizado correctamente.")
            return redirect("listar_retos")
    else:
        form = CrearRetoForm(
            instance=reto,
            initial={
                'fecha_inicio': reto.fecha_inicio.strftime('%Y-%m-%dT%H:%M'),
                'fecha_fin': reto.fecha_fin.strftime('%Y-%m-%dT%H:%M'),
            }
        )

    return render(request, "editar_reto.html", {"form": form, "reto": reto})


@login_required
def eliminar_reto(request, reto_id):
    reto = get_object_or_404(Reto, id=reto_id)
    if reto.creador != request.user and not request.user.is_staff:
        return HttpResponseForbidden("No tienes permiso para eliminar este reto.")
    
    if request.method == "POST":
        reto.delete()
        messages.success(request, f"Reto '{reto.nombre}' eliminado correctamente.")
        return redirect('listar_retos')
    
    return render(request, 'confirmar_eliminacion_reto.html', {'reto': reto})


# ---------------------------------------------------------
#              SECCION METAS
# ---------------------------------------------------------ç
from .models import MetaUsuario,ProgresoMeta
from .forms import MetaUsuarioForm,ProgresoMetaForm

@login_required
def crear_meta(request):
    if request.method == 'POST':
        form = MetaUsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            meta = form.save(commit=False)
            meta.usuario = request.user
            meta.save()
            messages.success(request, "Meta creada con éxito.")
            return redirect('listar_metas')
    else:
        form = MetaUsuarioForm()
    return render(request, 'crear_meta.html', {'form': form})

@login_required
def listar_metas(request):
  
    # Obtener todas las metas del usuario
    metas = MetaUsuario.objects.filter(usuario=request.user).order_by('fecha_inicio', 'fecha_fin')

    return render(request, 'listar_metas.html', {
        'metas': metas,
        "now": now()
    })


@login_required
def registrar_progreso(request, meta_id):
    meta = get_object_or_404(MetaUsuario, id=meta_id, usuario=request.user)
    if request.method == 'POST':
        form = ProgresoMetaForm(request.POST, request.FILES)
        if form.is_valid():
            progreso = form.save(commit=False)
            progreso.meta = meta
            progreso.save()

            # Verificar si la meta ya se ha cumplido
            if meta.progreso_actual() >= meta.objetivo:
                meta.completada = True
                meta.save()

            messages.success(request, "Progreso registrado con éxito.")
            return redirect('detalle_meta', meta_id=meta.id)
    else:
        form = ProgresoMetaForm()
    return render(request, 'registrar_progreso.html', {'form': form, 'meta': meta})

from django.utils.timezone import now

@login_required
def detalle_meta(request, meta_id):
    meta = get_object_or_404(MetaUsuario, id=meta_id, usuario=request.user)
    progresos = meta.progresos.order_by("-fecha")
    fecha_actual = now()  # Obtener la fecha actual
    
    return render(request, 'detalle_meta.html', {
        'meta': meta,
        'progresos': progresos,
        'fecha_actual': fecha_actual
    })


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import MetaUsuario

@login_required
def obtener_progreso_meta(request, meta_id):
    """ Devuelve el progreso en tiempo real de una meta. """
    meta = get_object_or_404(MetaUsuario, id=meta_id, usuario=request.user)
    
    data = {
        "porcentaje_progreso": meta.porcentaje_completado,
        "progreso_actual": meta.progreso_actual,
        "objetivo": meta.objetivo,
        "unidad": meta.unidad
    }

    # Debugging: Imprime en la consola de Django para verificar que la vista se ejecuta correctamente.
    print(f"📊 Actualizando progreso para Meta {meta_id}: {data}")

    return JsonResponse(data)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MetaUsuario
from .forms import MetaUsuarioForm

@login_required
def editar_meta(request, meta_id):
    meta = get_object_or_404(MetaUsuario, id=meta_id, usuario=request.user)
    
    if request.method == 'POST':
        form = MetaUsuarioForm(request.POST, request.FILES, instance=meta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Meta actualizada con éxito.')
            return redirect('listar_metas')
        else:
            # Si el formulario tiene errores, aseguramos que `fecha_fin_formateada` siempre esté definida
            fecha_fin_formateada = request.POST.get('fecha_fin', meta.fecha_fin.strftime('%Y-%m-%dT%H:%M') if meta.fecha_fin else '')
    else:
        form = MetaUsuarioForm(instance=meta)
        fecha_fin_formateada = meta.fecha_fin.strftime('%Y-%m-%dT%H:%M') if meta.fecha_fin else ''

    return render(request, 'editar_meta.html', {
        'form': form,
        'meta': meta,
        'fecha_fin_formateada': fecha_fin_formateada  # Agregamos la fecha al contexto
    })


@login_required
def eliminar_meta(request, meta_id):
    meta = get_object_or_404(MetaUsuario, id=meta_id, usuario=request.user)
    if request.method == 'POST':
        meta.delete()
        messages.success(request, 'Meta eliminada con éxito.')
        return redirect('listar_metas')
    return render(request, 'confirmar_eliminacion_meta.html', {'meta': meta})
 # ---------------------------------------------------------
    #              SECCION EJERCICIOS
# ----------------------------------------------------------
    

from django.shortcuts import render
from .models import Entreno  # Modelo que crearemos en el siguiente paso

# Mapeo de nombres con lados a grupos genéricos solo para la API externa
# Mapeo de nombres con lados a grupos genéricos solo para la API externa
MAPEO_ALIAS_PARTES = {
    "chest-left": "pecho", "chest-right": "pecho",
    "shoulder-left": "hombros", "shoulder-right": "hombros",
    "arm-left": "brazos", "arm-right": "brazos",
    "forearm-left": "antebrazo", "forearm-right": "antebrazo",
    "ribs-left": "core", "ribs-right": "core",
    "back-left": "espalda", "back-right": "espalda",  # Asegurarse de mapear estos casos
    "clavicule-left": "espalda", "clavicule-right": "espalda",
    "thigh-left": "piernas", "thigh-right": "piernas",
}


def listar_ejercicios(request, parte_cuerpo):
    ejercicios = list(Entreno.objects.filter(parte_cuerpo=parte_cuerpo))
    ejercicios_extra = []
    nombre_mostrado = MAPEO_ALIAS_PARTES.get(parte_cuerpo.lower(), parte_cuerpo).capitalize()

    if len(ejercicios) < 5:
        cantidad_a_completar = 5 - len(ejercicios)

        parte_generica = MAPEO_ALIAS_PARTES.get(parte_cuerpo.lower())
        if parte_generica:
            parte_api = MAPEO_GRUPOS.get(parte_generica)

            if parte_api:
                url_api = f"https://exercisedb.p.rapidapi.com/exercises/bodyPart/{parte_api}"
                headers = {
                    "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
                    "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
                }

                try:
                    response = requests.get(url_api, headers=headers)
                    if response.status_code == 200:
                        ejercicios_disponibles = response.json()
                        if ejercicios_disponibles:
                            seleccionados = random.sample(ejercicios_disponibles, min(cantidad_a_completar, len(ejercicios_disponibles)))
                            for ejercicio in seleccionados:
                                nombre = ejercicio.get("name", "Ejercicio desconocido")
                                gif = ejercicio.get("gifUrl", "")
                                descripcion_raw = buscar_en_api_ninjas(nombre).get("instructions") or ejercicio.get("instructions", "")
                                if isinstance(descripcion_raw, list):
                                    descripcion_raw = " ".join(descripcion_raw)
                                descripcion = normalizar_descripcion(descripcion_raw)

                                ejercicios_extra.append({
                                    "nombre": nombre,
                                    "imagen": gif,
                                    "descripcion": descripcion,
                                    "es_api": True
                                })
                    else:
                        ejercicios_extra = buscar_en_api_ninjas_por_grupo(parte_generica)[:cantidad_a_completar]

                except Exception as e:
                    print(f"⚠️ Error al obtener ejercicios externos: {e}")

    
    return render(request, "listar_ejercicios.html", {
        "parte_cuerpo": parte_cuerpo,
        "nombre_mostrado": nombre_mostrado,
        "ejercicios": ejercicios,
        "ejercicios_extra": ejercicios_extra
    })

  # ---------------------------------------------------------
    #              SECCION ENTRENADOR VIRTUAL
# ----------------------------------------------------------
import requests
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import RutinaForm

# URLs de las APIs
EXERCISEDB_API_URL = "https://exercisedb.p.rapidapi.com/exercises/bodyPart/"
API_NINJAS_URL = "https://api.api-ninjas.com/v1/exercises"

# Headers para autenticación
HEADERS_EXERCISEDB = {
    "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
    "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
}

HEADERS_NINJAS = {
    "X-Api-Key": settings.API_NINJAS_KEY
}

 
import random
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# 🔥 MAPEO DE GRUPOS MUSCULARES A LOS QUE ACEPTA LA API
MAPEO_GRUPOS = {
    "pecho": "chest",
    "espalda": "back",
    "piernas": "upper legs",
    "brazos": "upper arms",
    "core": "waist",
    "cardio": "cardio"
}

OBJETIVOS_MUSCULARES = {
    "perder_peso": ["cardio", "pecho", "espalda", "piernas"],
    "ganar_musculo": ["pecho", "espalda", "piernas", "brazos"],
    "resistencia": ["piernas", "core", "cardio"],
    "definicion": ["pecho", "espalda", "piernas", "core"]
}

NUM_EJERCICIOS = {"principiante": 1, "intermedio": 2, "avanzado": 3}

# 🔥 MAPEO DE REPETICIONES Y DESCANSOS SEGÚN EL OBJETIVO
OBJETIVO_REPETICIONES_DESCANSO = {
    "ganar_musculo": {"repeticiones": "4-8 reps", "descanso": "120s"},
    "perder_peso": {"repeticiones": "6-12 reps", "descanso": "60s"},
    "resistencia": {"repeticiones": "10-20 reps", "descanso": "30s"},
    "definicion": {"repeticiones": "6-12 reps", "descanso": "90s"}
}

def obtener_ejercicios(objetivo, nivel):
    cantidad_ejercicios = NUM_EJERCICIOS.get(nivel, 1)
    grupos_musculares = OBJETIVOS_MUSCULARES.get(objetivo, ["full body"])
    ejercicios_finales = []

    repeticiones = OBJETIVO_REPETICIONES_DESCANSO[objetivo]["repeticiones"]
    descanso = OBJETIVO_REPETICIONES_DESCANSO[objetivo]["descanso"]

    for grupo in grupos_musculares:
        grupo_api = MAPEO_GRUPOS.get(grupo)
        if not grupo_api:
            logger.warning(f"⚠️ Grupo muscular '{grupo}' no tiene mapeo en la API. Se ignora.")
            continue  

        url_exercisedb = f"https://exercisedb.p.rapidapi.com/exercises/bodyPart/{grupo_api}"
        headers_exercisedb = {
            "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
            "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
        }

        logger.info(f"🔍 Solicitando ejercicios de ExerciseDB para {grupo} (API: {grupo_api})")

        try:
            response_exercisedb = requests.get(url_exercisedb, headers=headers_exercisedb)

            if response_exercisedb.status_code == 200:
                ejercicios_disponibles = response_exercisedb.json()
                logger.info(f"✅ ExerciseDB respondió correctamente para {grupo}: {len(ejercicios_disponibles)} ejercicios encontrados.")

                if ejercicios_disponibles:
                    ejercicios_seleccionados = random.sample(
                        ejercicios_disponibles, 
                        min(cantidad_ejercicios, len(ejercicios_disponibles))
                    )
                    for ejercicio in ejercicios_seleccionados:
                        nombre_ejercicio = ejercicio["name"]

                        # 🔥 Complementamos con API Ninjas (si hay)
                        detalles_extra = buscar_en_api_ninjas(nombre_ejercicio)
                       # 🔁 Prioridad: primero intentamos con la API Ninjas, si falla usamos la de ExerciseDB
                        descripcion_cruda = detalles_extra.get("instructions") or ejercicio.get("instructions", "")

                        # Si descripción es una lista, la unimos
                        if isinstance(descripcion_cruda, list):
                            descripcion_cruda = " ".join(descripcion_cruda)

                        descripcion_traducida = normalizar_descripcion(descripcion_cruda)

                        ejercicios_finales.append({
                            "grupo": grupo,
                            "nombre": nombre_ejercicio,
                            "descripcion": descripcion_traducida,
                            "imagen": ejercicio["gifUrl"],
                            "series": 3 if nivel == "principiante" else 4 if nivel == "intermedio" else 5,
                            "repeticiones": repeticiones,
                            "descanso": descanso
                        })

            else:
                logger.error(f"❌ Error en la API de ExerciseDB ({response_exercisedb.status_code}): {response_exercisedb.text}")

        except requests.RequestException as e:
            logger.error(f"🚨 Error de conexión con ExerciseDB: {e}")

        # 🔁 Si no se encontraron ejercicios en ExerciseDB
        if not ejercicios_finales:
            logger.warning(f"⚠️ No se encontraron ejercicios en ExerciseDB para {grupo}. Buscando en API Ninjas...")
            ejercicios_ninjas = buscar_en_api_ninjas_por_grupo(grupo)
            ejercicios_finales.extend(ejercicios_ninjas)

    return ejercicios_finales



# 🔍 FUNCIONES AUXILIARES PARA API NINJAS
def buscar_en_api_ninjas(nombre_ejercicio):
    """Busca detalles de un ejercicio en API Ninjas por nombre."""
    url_ninjas = "https://api.api-ninjas.com/v1/exercises"
    headers_ninjas = {"X-Api-Key": settings.API_NINJAS_KEY}

    try:
        response = requests.get(url_ninjas, params={"name": nombre_ejercicio}, headers=headers_ninjas)
        
        if response.status_code == 200 and response.json():
            return response.json()[0]  
        else:
            return {}

    except requests.RequestException as e:
        logger.error(f"🚨 Error de conexión con API Ninjas: {e}")
        return {}


def buscar_en_api_ninjas_por_grupo(grupo):
    """Busca ejercicios en API Ninjas según el grupo muscular y los traduce."""
    url_ninjas = "https://api.api-ninjas.com/v1/exercises"
    headers_ninjas = {"X-Api-Key": settings.API_NINJAS_KEY}
    
    ejercicios_finales = []

    try:
        response = requests.get(url_ninjas, params={"muscle": grupo}, headers=headers_ninjas)
        
        if response.status_code == 200 and response.json():
            ejercicios_disponibles = response.json()
            logger.info(f"✅ API Ninjas devolvió {len(ejercicios_disponibles)} ejercicios para {grupo}")

            for ejercicio in ejercicios_disponibles[:3]:  
                descripcion_cruda = ejercicio.get("instructions", "")
                if isinstance(descripcion_cruda, list):
                    descripcion_cruda = " ".join(descripcion_cruda)

                descripcion_traducida = normalizar_descripcion(descripcion_cruda)

                ejercicios_finales.append({
                    "grupo": grupo,
                    "nombre": ejercicio["name"],
                    "descripcion": descripcion_traducida,
                    "imagen": "https://via.placeholder.com/150",
                    "series": 3,
                    "repeticiones": "15-20 reps",
                    "descanso": "60s"
                })

        else:
            logger.warning(f"⚠️ No se encontraron ejercicios en API Ninjas para {grupo}.")

    except requests.RequestException as e:
        logger.error(f"🚨 Error de conexión con API Ninjas: {e}")

    return ejercicios_finales


@login_required
def entrenador_virtual(request):
    """Genera una rutina de ejercicios personalizada basada en el objetivo y nivel del usuario."""
    if request.method == "POST":
        form = RutinaForm(request.POST)
        if form.is_valid():
            objetivo = form.cleaned_data['objetivo']
            nivel = form.cleaned_data['nivel']
            
            logger.info(f"🏋️ Generando rutina para objetivo: {objetivo} | nivel: {nivel}")

            # Obtener ejercicios
            ejercicios = obtener_ejercicios(objetivo, nivel)
            
            # Agrupar ejercicios por músculo
            ejercicios_por_grupo = {}
            for ejercicio in ejercicios:
                grupo = ejercicio.get("grupo", "Otros")
                if grupo not in ejercicios_por_grupo:
                    ejercicios_por_grupo[grupo] = []
                ejercicios_por_grupo[grupo].append(ejercicio)

            logger.info(f"📊 Ejercicios generados: {ejercicios_por_grupo}")

            return render(request, 'rutina_generada.html', {
                'nivel': nivel,
                'ejercicios_por_grupo': ejercicios_por_grupo
            })

    else:
        form = RutinaForm()

    return render(request, 'entrenador_virtual.html', {'form': form})


import wordninja

def unir_letras_separadas(texto):
    """
    Detecta si un texto viene con letras separadas por espacios y reconstruye las palabras.
    """
    tokens = texto.strip().split()
    letras_sueltas = sum(1 for t in tokens if len(t) == 1)
    ratio = letras_sueltas / len(tokens) if tokens else 0

    print(f"[🔍 DETECCIÓN] Tokens: {tokens[:10]}... | Total: {len(tokens)} | Letras sueltas: {letras_sueltas} | Ratio: {ratio:.2f}")

    if len(tokens) > 10 and ratio > 0.8:
        texto_unido = ''.join(tokens)
        print(f"[🔧 RECONSTRUIR] Texto unido sin espacios: {texto_unido}")

        palabras = wordninja.split(texto_unido)
        print(f"[🔧 WORDNINJA] Resultado de wordninja: {palabras[:10]}...")

        return ' '.join(palabras)

    return texto




from deep_translator import GoogleTranslator
import re

def normalizar_descripcion(texto):
    """Limpia, traduce al español y repara texto separado por letras."""

    if not texto or not isinstance(texto, str) or texto.strip() == "":
        return "No hay descripción disponible."

    print(f"[🔹ORIGINAL] Texto original recibido: {texto}")

    # Etapa 1: Unir si está separado por letras
    texto = unir_letras_separadas(texto)
    print(f"[🔹POST-UNIR] Después de unir letras (pre-traducción): {texto}")

    # Etapa 2: Traducción
    try:
        traducido = GoogleTranslator(source='auto', target='es').translate(texto).strip()
        print(f"[🔹TRADUCCIÓN] Resultado de la traducción: {traducido}")
    except Exception as e:
        print(f"❌ Error al traducir descripción: {e}")
        return texto

    # Etapa 3: Reparar si la traducción vino mal
    traducido = unir_letras_separadas(traducido)
    print(f"[🔹POST-UNIR-TRAD] Después de unir letras (post-traducción): {traducido}")

    # Etapa 4: limpieza final
    traducido = re.sub(r'\s+', ' ', traducido).strip()
    if not traducido.endswith(('.', '!', '?')):
        traducido += '.'

    resultado = traducido[0].upper() + traducido[1:] if traducido else "No hay descripción disponible."
    print(f"[✅FINAL] Resultado final normalizado: {resultado}")

    return resultado
