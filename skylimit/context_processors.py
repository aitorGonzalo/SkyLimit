# ---------------------------------------------------------
#              SECCION BARRA LATERAL
# ---------------------------------------------------------
from django.db.models import Q
from .models import MensajeGrupo, Grupo, MensajePrivado, GrupoVisitado

def notificaciones_context(request):
    if request.user.is_authenticated:
        # Notificaciones de Grupos
        grupos = Grupo.objects.filter(miembros=request.user)
        notificaciones_grupos = 0

        for grupo in grupos:
            ultima_visita = GrupoVisitado.objects.filter(usuario=request.user, grupo=grupo).first()
            if ultima_visita:
                mensajes_no_leidos = MensajeGrupo.objects.filter(
                    grupo=grupo,
                    fecha_creacion__gt=ultima_visita.ultima_visita
                ).exclude(usuario=request.user).count()
            else:
                mensajes_no_leidos = MensajeGrupo.objects.filter(grupo=grupo).exclude(usuario=request.user).count()
            notificaciones_grupos += mensajes_no_leidos

        # Notificaciones de Mensajes Directos
        notificaciones_directos = MensajePrivado.objects.filter(
            destinatario=request.user, leido=False
        ).count()

        return {
            'notificaciones_grupos': notificaciones_grupos,
            'notificaciones_directos': notificaciones_directos,
        }
    return {}



from .models import SolicitudEntrenador

def solicitudes_pendientes_context(request):
    if request.user.is_staff:
        total_solicitudes = SolicitudEntrenador.objects.count()  # Contar todas las solicitudes
        return {'solicitudes_pendientes': total_solicitudes}
    return {}
