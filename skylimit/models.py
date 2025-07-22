from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import timedelta
from django.utils.timezone import now
# Create your models here.

# ---------------------------------------------------------
#                SECCION MODELO PERFIL USUARIO
# ---------------------------------------------------------
# models.py
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=30, blank=True)
    apellidos = models.CharField(max_length=50, blank=True)
    descripcion = models.TextField(blank=True)
    edad = models.PositiveIntegerField(null=True, blank=True)
    genero = models.CharField(
        max_length=10,
        choices=[
            ('Masculino', 'Masculino'),
            ('Femenino', 'Femenino'),
            ('Otro', 'Otro'),
        ],
        blank=True
    )
    intereses = models.TextField(blank=True)  # Campo para intereses en texto
    nivel_experiencia = models.CharField(
        max_length=15,
        choices=[
            ('Principiante', 'Principiante'),
            ('Intermedio', 'Intermedio'),
            ('Avanzado', 'Avanzado'),
        ],
        blank=True
    )
    metas = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"


# ---------------------------------------------------------
#              SECCION ENTRENADORES
# ---------------------------------------------------------


class SolicitudEntrenador(models.Model):
    username = models.CharField(max_length=30, unique=True, verbose_name="Usuario")
    email = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    password = models.CharField(max_length=128, verbose_name="Contraseña")
    nombre = models.CharField(max_length=30, verbose_name="Nombre")
    apellidos = models.CharField(max_length=50, verbose_name="Apellidos")
    genero = models.CharField(
        max_length=10,
        choices=[
            ('Masculino', 'Masculino'),
            ('Femenino', 'Femenino'),
            ('Otro', 'Otro')
        ],
        verbose_name="Género"
    )
    nivel_experiencia = models.CharField(
        max_length=15,
        choices=[
            ('Principiante', 'Principiante'),
            ('Intermedio', 'Intermedio'),
            ('Avanzado', 'Avanzado')
        ],
        verbose_name="Nivel de Experiencia"
    )
    especialidades = models.TextField(verbose_name="Especialidades deportivas")
    experiencia = models.TextField(verbose_name="Experiencia profesional")
    formacion = models.TextField(verbose_name="Formación académica")
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de solicitud")

    def __str__(self):
        return f"Solicitud de {self.username} ({self.nombre} {self.apellidos})"

class Entrenador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)  
    nombre = models.CharField(max_length=30, blank=True, verbose_name="Nombre")
    apellidos = models.CharField(max_length=50, blank=True, verbose_name="Apellidos")
    genero = models.CharField(
        max_length=10,
        choices=[
            ('Masculino', 'Masculino'),
            ('Femenino', 'Femenino'),
            ('Otro', 'Otro'),
        ],
        blank=True,
        verbose_name="Género"
    )
    nivel_experiencia = models.CharField(
        max_length=15,
        choices=[
            ('Principiante', 'Principiante'),
            ('Intermedio', 'Intermedio'),
            ('Avanzado', 'Avanzado'),
        ],
        blank=True,
        verbose_name="Nivel de Experiencia"
    )
    especialidades = models.TextField(blank=True, verbose_name="Especialidades deportivas")
    experiencia = models.TextField(blank=True, verbose_name="Experiencia profesional")
    formacion = models.TextField(blank=True, verbose_name="Formación académica")
    aprobado_por_admin = models.BooleanField(default=False, verbose_name="Aprobado por el administrador")
    plazas_abiertas = models.PositiveIntegerField(default=5)
    es_entrenador = models.BooleanField(default=True, editable=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/imgs/default-avatar.png'  
    def __str__(self):
        return f"{self.nombre} {self.apellidos} - {'Aprobado' if self.aprobado_por_admin else 'Pendiente de aprobación'}"

class Entrenamiento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="entrenamientos")
    entrenador = models.ForeignKey(Entrenador, on_delete=models.CASCADE, related_name="usuarios_entrenados")
    fecha_inicio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} entrena con {self.entrenador.nombre} {self.entrenador.apellidos}"

class SolicitudEntrenamiento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    entrenador = models.ForeignKey(Entrenador, on_delete=models.CASCADE, related_name="solicitudes")
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    respuesta_recibida = models.BooleanField(default=False)  # 🔥 Nuevo campo
    
    def __str__(self):
        return f"Solicitud de {self.usuario.username} para {self.entrenador.nombre} {self.entrenador.apellidos}"

# ---------------------------------------------------------
#              SECCION SEÑALES (SIGNALS)
# ---------------------------------------------------------

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.perfilusuario.save()

# ---------------------------------------------------------
#              SECCION GRUPOS
# ---------------------------------------------------------
from django.db import models
from django.contrib.auth.models import User

class Grupo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    creador = models.ForeignKey(User, on_delete=models.CASCADE, related_name="grupos_creados")
    miembros = models.ManyToManyField(User, related_name="grupos_miembros", blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    imagen = models.ImageField(upload_to='grupos/', default='imgs/default-group.png')
    def __str__(self):
        return self.nombre


class MensajeGrupo(models.Model):
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name='mensajes')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    editado = models.BooleanField(default=False)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"Mensaje de {self.usuario.username} en {self.grupo.nombre}"

class GrupoVisitado(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    grupo = models.ForeignKey('Grupo', on_delete=models.CASCADE)
    ultima_visita = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('usuario', 'grupo')

# ---------------------------------------------------------
#              SECCION ACTIVIDADES
# ---------------------------------------------------------

class Actividad(models.Model):
    UNIDADES_DURACION = [
        ('seconds', 'Segundos'),
        ('minutes', 'Minutos'),
        ('hours', 'Horas'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_hora = models.DateTimeField()
    duracion_valor = models.PositiveIntegerField(null=True, blank=True)  # Valor numérico de la duración
    duracion_unidad = models.CharField(
        max_length=10, 
        choices=UNIDADES_DURACION, 
        default='minutes'
    )  # Unidad de la duración
    ubicacion = models.CharField(max_length=200)
    limite_participantes = models.PositiveIntegerField(null=True, blank=True)
    participantes = models.ManyToManyField(User, related_name="actividades_participantes", blank=True)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='actividades/', default='imgs/default_actividad.jpg')  # Ruta de imagen por defecto

    def __str__(self):
        return self.nombre

    def cupo_disponible(self):
        if self.limite_participantes:
            return self.limite_participantes - self.participantes.count()
        return None

    def obtener_duracion(self):
        """
        Devuelve la duración como un objeto timedelta basado en el valor y la unidad especificados.
        """
        if self.duracion_valor:
            if self.duracion_unidad == 'seconds':
                return timedelta(seconds=self.duracion_valor)
            elif self.duracion_unidad == 'minutes':
                return timedelta(minutes=self.duracion_valor)
            elif self.duracion_unidad == 'hours':
                return timedelta(hours=self.duracion_valor)
        return None

    def duracion_formateada(self):
        """
        Devuelve la duración en un formato legible.
        """
        duracion = self.obtener_duracion()
        if duracion:
            total_seconds = int(duracion.total_seconds())
            horas, resto = divmod(total_seconds, 3600)
            minutos, segundos = divmod(resto, 60)
            partes = []
            if horas > 0:
                partes.append(f"{horas} horas")
            if minutos > 0:
                partes.append(f"{minutos} minutos")
            if segundos > 0:
                partes.append(f"{segundos} segundos")
            return ', '.join(partes)
        return "No especificada"

class ChatActividad(models.Model):
    actividad = models.OneToOneField(Actividad, on_delete=models.CASCADE, related_name="chat")
    mensajes = models.ManyToManyField(User, through="MensajeActividad")

    def __str__(self):
        return f"Chat para {self.actividad.nombre}"


class MensajeActividad(models.Model):
    chat = models.ForeignKey(ChatActividad, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    editado = models.BooleanField(default=False)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"Mensaje de {self.usuario.username} en {self.chat.actividad.nombre}"
# ---------------------------------------------------------
#              SECCION MENSAJES PRIVADOS
# ---------------------------------------------------------
class MensajePrivado(models.Model):
    remitente = models.ForeignKey(User, related_name='mensajes_enviados', on_delete=models.CASCADE)
    destinatario = models.ForeignKey(User, related_name='mensajes_recibidos', on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(default=now)
    leido = models.BooleanField(default=False)
    editado = models.BooleanField(default=False)  # Nuevo campo para marcar si fue editado

    def __str__(self):
        return f"De {self.remitente.username} a {self.destinatario.username}"


# ---------------------------------------------------------
#              SECCION PUBLICACIONES
# ---------------------------------------------------------
# Modelo de publicación
# models.py
class Publicacion(models.Model):
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='publicaciones')
    contenido = models.TextField(blank=True, null=True)  # Texto opcional de la publicación
    imagen = models.ImageField(upload_to='publicaciones/', blank=True, null=True)  # Imagen opcional
    video = models.FileField(upload_to='publicaciones/videos/', blank=True, null=True)  # Video opcional
    fecha_creacion = models.DateTimeField(default=now)  # Fecha de creación
    destacado = models.BooleanField(default=False)  # Nuevo campo para destacar publicaciones (usado para entrenadores)

    def __str__(self):
        return f"Publicación de {self.autor.username} - {self.fecha_creacion.strftime('%Y-%m-%d %H:%M')}"

    def tiene_multimedia(self):
        """Comprueba si la publicación tiene una imagen o un video"""
        return self.imagen or self.video

# Modelo de comentario
class Comentario(models.Model):
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentarios')
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(default=now)

    def __str__(self):
        return f"Comentario de {self.autor.username} en {self.publicacion.id}"

# Modelo de like
class Like(models.Model):
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='likes')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    fecha = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('publicacion', 'usuario')  # Evita múltiples likes de un usuario a la misma publicación

    def __str__(self):
        return f"{self.usuario.username} dio like a {self.publicacion.id}"

# ---------------------------------------------------------
#              SECCION RETOS
# ---------------------------------------------------------

from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

class Reto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    objetivo = models.PositiveIntegerField()  # Valor objetivo del reto
    unidad_objetivo = models.CharField(
        max_length=20,
        choices=[
            ('km', 'Kilómetros'),
            ('pasos', 'Pasos'),
            ('horas', 'Horas'),
            ('min', 'Minutos'),
            ('rep', 'Repeticiones'),
        ],
        default='km'
    )
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    imagen = models.ImageField(upload_to='retos/', blank=True, null=True)  # Campo para la imagen
    creador = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # Relación con el usuario creador

    def imagen_o_por_defecto(self):
        """
        Devuelve la imagen del reto o una imagen por defecto.
        """
        if self.imagen:
            return self.imagen.url
        return '/static/imgs/default-reto.png'

    def esta_activo(self):
        return self.fecha_inicio <= now() <= self.fecha_fin

    def futuro(self):
        return self.fecha_inicio > now()
    
    def finalizado(self):
        return now() > self.fecha_fin

    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        if not self.imagen:
            self.imagen = 'retos/default-reto.png'  # Ruta dentro de tu carpeta MEDIA
        super().save(*args, **kwargs)

       

class ParticipacionReto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    reto = models.ForeignKey(Reto, on_delete=models.CASCADE)
    progreso_acumulado = models.PositiveIntegerField(default=0)  # Progreso registrado
    unidad = models.CharField(max_length=20, default="kilómetros")  # Unidad de progreso
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.reto.nombre} - {self.progreso_acumulado} {self.unidad}"


class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificación para {self.usuario.username}: {self.mensaje}"
    

# ---------------------------------------------------------
#              SECCION METAS
# ---------------------------------------------------------
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class MetaUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="metas")
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    objetivo = models.FloatField()
    unidad = models.CharField(
        max_length=20,
        choices=[
            ("kg", "Kilogramos"),
            ("km", "Kilómetros"),
            ("pasos", "Pasos"),
            ("horas", "Horas"),
            ("minutos", "Minutos"),
            ("repeticiones", "Repeticiones"),
        ]
    )
    fecha_inicio = models.DateTimeField(default=now)
    fecha_fin = models.DateTimeField()
    imagen = models.ImageField(upload_to='metas/', blank=True, null=True, default="metas/default-reto.png") 
   
    def save(self, *args, **kwargs):
        if not self.imagen:  # Si no tiene imagen, asignar la imagen por defecto
            self.imagen = "metas/default-reto.png"
        super().save(*args, **kwargs)

    def progreso_actual(self):
        """ Retorna el progreso total acumulado. """
        return sum(self.progresos.values_list("cantidad", flat=True))

   
    def porcentaje_completado(self):
        """ Calcula el porcentaje basado en el objetivo. """
        progreso = self.progreso_actual()  # <-- Llamando correctamente el método
        if self.objetivo == 0:
            return 0
        return min(100, (progreso / self.objetivo) * 100)  # Usando el valor obtenido
    def meta_completada(self):
        """ Devuelve True si la fecha ha pasado y el progreso acumulado es mayor o igual al objetivo. """
        return now() >= self.fecha_fin and self.progreso_actual() >= self.objetivo

    def __str__(self):
        return f"{self.usuario.username} - {self.nombre}"

class ProgresoMeta(models.Model):
    meta = models.ForeignKey(MetaUsuario, on_delete=models.CASCADE, related_name="progresos")
    fecha = models.DateTimeField(default=now)
    cantidad = models.FloatField()
    imagen = models.ImageField(upload_to='progreso/', blank=True, null=True)
    video = models.FileField(upload_to='progreso/videos/', blank=True, null=True)

    def __str__(self):
        return f"{self.meta.usuario.username} - {self.meta.nombre} - {self.fecha}"

 # ---------------------------------------------------------
    #              SECCION EJERCICIOS
# ----------------------------------------------------------
from django.db import models

class Entreno(models.Model):
    parte_cuerpo = models.CharField(max_length=50)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='ejercicios/imagenes/', blank=True, null=True)
    video = models.FileField(upload_to='ejercicios/videos/', blank=True, null=True)
    descripcionEjer = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.parte_cuerpo}"

    def multimedia(self):
        """
        Devuelve la imagen si existe, de lo contrario devuelve el video.
        """
        if self.imagen:
            return self.imagen.url
        elif self.video:
            return self.video.url
        return None
