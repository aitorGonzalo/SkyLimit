from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import AdminSplitDateTime
from .models import PerfilUsuario,Entrenador,Grupo,Actividad, ProgresoMeta, Reto
from django.utils.timezone import now
# ---------------------------------------------------------
#                SECCION FORMULARIO DE REGISTRO
# ---------------------------------------------------------

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo Electrónico")
    nombre = forms.CharField(max_length=30, required=True, label="Nombre")
    apellidos = forms.CharField(max_length=50, required=True, label="Apellidos")
    descripcion = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'placeholder': 'Escribe algo sobre ti...'}),
        label="Descripción"
    )
    edad = forms.IntegerField(required=True, min_value=1, label="Edad")
    genero = forms.ChoiceField(
        choices=[
            ('Masculino', 'Masculino'),
            ('Femenino', 'Femenino'),
            ('Otro', 'Otro')
        ],
        required=True,
        label="Género"
    )
    intereses = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Escribe tus intereses aquí...'}),
        label="Intereses"
    )
    nivel_experiencia = forms.ChoiceField(
        choices=[
            ('Principiante', 'Principiante'),
            ('Intermedio', 'Intermedio'),
            ('Avanzado', 'Avanzado')
        ],
        required=True,
        label="Nivel de Experiencia"
    )
    metas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Escribe tus metas aquí...'}),
        label="Metas"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "nombre", "apellidos", "edad", "genero", "descripcion", "intereses", "nivel_experiencia", "metas"]

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("El nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está en uso.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Verificar si ya existe un perfil para este usuario
            perfil, created = PerfilUsuario.objects.get_or_create(
                user=user,
                defaults={
                    'nombre': self.cleaned_data.get('nombre', ''),
                    'apellidos': self.cleaned_data.get('apellidos', ''),
                    'descripcion': self.cleaned_data.get('descripcion', ''),
                    'edad': self.cleaned_data.get('edad', None),
                    'genero': self.cleaned_data.get('genero', ''),
                    'intereses': self.cleaned_data.get('intereses', ''),
                    'nivel_experiencia': self.cleaned_data.get('nivel_experiencia', ''),
                    'metas': self.cleaned_data.get('metas', '')
                }
            )
            if not created:
                # Si ya existe un perfil, puedes actualizarlo (opcional)
                perfil.nombre = self.cleaned_data.get('nombre', perfil.nombre)
                perfil.apellidos = self.cleaned_data.get('apellidos', perfil.apellidos)
                perfil.descripcion = self.cleaned_data.get('descripcion', perfil.descripcion)
                perfil.edad = self.cleaned_data.get('edad', perfil.edad)
                perfil.genero = self.cleaned_data.get('genero', perfil.genero)
                perfil.intereses = self.cleaned_data.get('intereses', perfil.intereses)
                perfil.nivel_experiencia = self.cleaned_data.get('nivel_experiencia', perfil.nivel_experiencia)
                perfil.metas = self.cleaned_data.get('metas', perfil.metas)
                perfil.save()
        return user


class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['nombre', 'apellidos', 'descripcion', 'edad', 'genero', 'intereses', 'nivel_experiencia', 'metas', 'avatar']



class EntrenadorRegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=30, required=True, label="Usuario")
    email = forms.EmailField(required=True, label="Correo Electrónico")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    nombre = forms.CharField(max_length=30, required=True, label="Nombre")
    apellidos = forms.CharField(max_length=50, required=True, label="Apellidos")
    genero = forms.ChoiceField(
        choices=[
            ('Masculino', 'Masculino'),
            ('Femenino', 'Femenino'),
            ('Otro', 'Otro')
        ],
        required=True,
        label="Género"
    )
    nivel_experiencia = forms.ChoiceField(
        choices=[
            ('Principiante', 'Principiante'),
            ('Intermedio', 'Intermedio'),
            ('Avanzado', 'Avanzado')
        ],
        required=True,
        label="Nivel de Experiencia"
    )
    especialidades = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Especialidades deportivas...'}), label="Especialidades")
    experiencia = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Describe tu experiencia profesional...'}), label="Experiencia")
    formacion = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Detalles de tu formación académica...'}), label="Formación")
    
    class Meta:
        model = Entrenador
        fields = ['nombre', 'apellidos', 'genero', 'nivel_experiencia', 'especialidades', 'experiencia', 'formacion']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        entrenador = super().save(commit=False)
        entrenador.user = user
        if commit:
            user.save()
            entrenador.save()
        return entrenador


class GrupoForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ['nombre', 'descripcion', 'imagen']


from django import forms
from .models import Actividad
from django.utils.timezone import now

class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = ['nombre', 'descripcion', 'fecha_hora', 'duracion_valor', 'duracion_unidad', 'ubicacion', 'limite_participantes', 'imagen']
        widgets = {
            'fecha_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_fecha_hora(self):
        fecha_hora = self.cleaned_data.get('fecha_hora')
        if fecha_hora and fecha_hora < now():
            raise forms.ValidationError("La fecha y hora no pueden ser menores a la actual.")
        return fecha_hora


    def save(self, commit=True):
        actividad = super().save(commit=False)

        # Si no se sube una nueva imagen, no modificar la actual
        if 'imagen' not in self.changed_data:
            actividad.imagen = self.instance.imagen

        if commit:
            actividad.save()

        return actividad

from .models import Comentario
class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido']  # Solo necesitamos el contenido del comentario
        widgets = {
            'contenido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe un comentario...',
                'maxlength': '500',
            })
        }
        labels = {
            'contenido': '',
        }

from .models import Publicacion
class PublicacionForm(forms.ModelForm):
    class Meta:
        model = Publicacion
        fields = ['contenido', 'imagen', 'video']
        widgets = {
            'contenido': forms.Textarea(attrs={'placeholder': '¿Qué estás pensando?', 'class': 'form-control'}),
        }




from django.utils.timezone import localtime
from django import forms
from django.utils.timezone import now
from .models import Reto

class CrearRetoForm(forms.ModelForm):
    class Meta:
        model = Reto
        fields = ['nombre', 'descripcion', 'objetivo', 'unidad_objetivo', 'fecha_inicio', 'fecha_fin', 'imagen']
        widgets = {
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['fecha_inicio'].widget.attrs['value'] = self.instance.fecha_inicio.strftime('%Y-%m-%dT%H:%M')
            self.fields['fecha_fin'].widget.attrs['value'] = self.instance.fecha_fin.strftime('%Y-%m-%dT%H:%M')

    def clean_fecha_inicio(self):
        fecha_inicio = self.cleaned_data['fecha_inicio']
        if fecha_inicio < now():
            raise forms.ValidationError("La fecha de inicio no puede ser anterior a la fecha actual.")
        return fecha_inicio

    def clean_fecha_fin(self):
        fecha_fin = self.cleaned_data['fecha_fin']
        if fecha_fin < now():
            raise forms.ValidationError("La fecha de fin no puede ser anterior a la fecha actual.")
        if 'fecha_inicio' in self.cleaned_data and fecha_fin < self.cleaned_data['fecha_inicio']:
            raise forms.ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio.")
        return fecha_fin

from django import forms

class RegistrarProgresoForm(forms.Form):
    progreso = forms.FloatField(label="Cantidad", min_value=0.01, required=True)
    unidad = forms.ChoiceField(
        choices=[
            ("kilómetros", "Kilómetros"),
            ("pasos", "Pasos"),
            ("minutos", "Minutos"),
            ("horas", "Horas"),
            ("repeticiones", "Repeticiones"),
        ],
        label="Unidad",
        required=True,
    )


from django import forms
from django.utils.timezone import now
from .models import MetaUsuario

class MetaUsuarioForm(forms.ModelForm):
    class Meta:
        model = MetaUsuario
        fields = ['nombre', 'descripcion', 'objetivo', 'unidad', 'fecha_fin', 'imagen']
        widgets = {
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_fecha_fin(self):
        """
        Validar que la fecha de fin no pueda ser anterior a la fecha y hora actual redondeada al minuto.
        """
        fecha_fin = self.cleaned_data.get("fecha_fin")
        if fecha_fin:
            # Obtener la hora actual redondeada a los minutos actuales (sin segundos y microsegundos)
            hora_actual = now().replace(second=0, microsecond=0)

            if fecha_fin < hora_actual:
                raise forms.ValidationError("La fecha de finalización no puede ser anterior a la fecha y hora actual.")

        return fecha_fin

    def save(self, commit=True):
        meta = super().save(commit=False)
        if not meta.imagen:  # Si no se sube una imagen, asignar una por defecto
            meta.imagen = "metas/default-reto.png"  # Ruta dentro de tu carpeta MEDIA
        if commit:
            meta.save()
        return meta

from django import forms
from .models import ProgresoMeta

class ProgresoMetaForm(forms.ModelForm):
    class Meta:
        model = ProgresoMeta
        fields = ['fecha', 'cantidad', 'imagen', 'video']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),  # Ahora incluye la hora
        }


from django import forms
from .models import SolicitudEntrenamiento

class SolicitudEntrenamientoForm(forms.ModelForm):
    class Meta:
        model = SolicitudEntrenamiento
        fields = ['entrenador', 'mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={'placeholder': 'Escribe tu mensaje aquí...', 'rows': 3}),
        }


from django import forms

class RutinaForm(forms.Form):
    OBJETIVOS = [
        ("perder_peso", "Perder Peso"),
        ("ganar_musculo", "Ganar Músculo"),
        ("resistencia", "Mejorar Resistencia"),
        ("definicion", "Definición Muscular")
    ]

    NIVELES = [
        ("principiante", "Principiante"),
        ("intermedio", "Intermedio"),
        ("avanzado", "Avanzado")
    ]

    objetivo = forms.ChoiceField(choices=OBJETIVOS, label="Elige tu objetivo", widget=forms.Select(attrs={"class": "form-control"}))
    nivel = forms.ChoiceField(choices=NIVELES, label="Nivel de entrenamiento", widget=forms.Select(attrs={"class": "form-control"}))
    
    # 🔹 Nuevos campos (aunque no se usen aún)
    altura = forms.IntegerField(label="Altura (cm)", min_value=50, max_value=250, required=False, widget=forms.NumberInput(attrs={"class": "form-control"}))
    peso = forms.FloatField(label="Peso (kg)", min_value=20, max_value=300, required=False, widget=forms.NumberInput(attrs={"class": "form-control"}))
    edad = forms.IntegerField(label="Edad", min_value=5, max_value=120, required=False, widget=forms.NumberInput(attrs={"class": "form-control"}))
