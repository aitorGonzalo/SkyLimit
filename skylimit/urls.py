# ---------------------------------------------------------
#                       IMPORTS
# ---------------------------------------------------------

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

# ---------------------------------------------------------
#                    SECCION URLPATTERNS
# ---------------------------------------------------------

urlpatterns = [
    # -----------------------------------------------------
    #                  SECCION PÁGINA PRINCIPAL
    # -----------------------------------------------------
    path('', views.index, name='home'),
    path('login', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('entrenadores/login/', views.login_entrenador, name='login_entrenador'),
    path('clima/<str:lat>/<str:lon>/', views.mostrar_clima, name='mostrar_clima'),  # Nueva ruta
    path('oleaje/<str:lat>/<str:lon>/', views.mostrar_oleaje, name='mostrar_oleaje'),
    path('mapa/', views.mapa, name='mapa'),
    path('cuerpo-humano/', views.cuerpo_humano, name='cuerpo_humano'),
    # -----------------------------------------------------
    #                   SECCION REGISTRO
    # -----------------------------------------------------
    path("register/", views.register, name="register"),
    path('entrenadores/registrar/', views.registrar_entrenador, name='registrar_entrenador'),
     # -----------------------------------------------------
    #                   SECCION CONTACTO
    # -----------------------------------------------------
    path('contacto/', views.contacto, name='contacto'),  
    # -----------------------------------------------------
    #                   SECCION PERFIL
    # -----------------------------------------------------
    path('perfil/', views.ver_perfil, name='ver_perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    # -----------------------------------------------------
    #                   SECCION ENTRENADORES
    # -----------------------------------------------------
    path('gestionar-entrenadores/', views.gestionar_entrenadores, name='gestionar_entrenadores'),
    path('perfil-entrenador/', views.ver_perfil_entrenador, name='ver_perfil_entrenador'),
    path("entrenadores/", views.listar_entrenadores, name="listar_entrenadores"),
    path('perfil-entrenador/editar/', views.editar_perfil_entrenador, name='editar_perfilEntrenador'),
    path('solicitudes-entrenador/', views.listar_solicitudes_entrenador, name="listar_solicitudes_entrenador"),
    path('gestionar-solicitud/<int:solicitud_id>/', views.gestionar_solicitud_entrenamiento, name="gestionar_solicitud_entrenamiento"),
    path('eliminar-usuario/<int:entrenamiento_id>/', views.eliminar_usuario_entrenado, name='eliminar_usuario_entrenado'),
    path('mis-usuarios/', views.listar_usuarios_entrenados, name='listar_usuarios_entrenados'),
    # -----------------------------------------------------
    #                   SECCION GRUPOS
    # -----------------------------------------------------
    path('grupos/', views.listar_grupos, name='listar_grupos'),
    path('grupos/<int:grupo_id>/', views.detalles_grupo, name='detalles_grupo'),
    path('grupos/crear/', views.crear_grupo, name='crear_grupo'),
    path('grupos/<int:grupo_id>/unirse/', views.unirse_grupo, name='unirse_grupo'),
    path('grupos/<int:grupo_id>/salir/', views.salir_grupo, name='salir_grupo'),
    path('grupos/<int:grupo_id>/eliminar/', views.eliminar_grupo, name='eliminar_grupo'),
    path('mensajes_grupo/<int:mensaje_id>/editar/', views.editar_mensaje_grupo, name='editar_mensaje_grupo'),
    path('mensajes_grupo/<int:mensaje_id>/eliminar/', views.eliminar_mensaje_grupo, name='eliminar_mensaje_grupo'),
    path('grupos/<int:grupo_id>/editar/', views.editar_grupo, name='editar_grupo'),
    path('grupo/<int:grupo_id>/actualizar_visita/', views.actualizar_visita_grupo, name='actualizar_visita_grupo'),

     # -----------------------------------------------------
    #                   SECCION RED SOCIAL
    # -----------------------------------------------------
    path('comunidad/', views.social_home, name='social_home'),
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
     # -----------------------------------------------------
    #                   SECCION ACTIVIDAD
    # -----------------------------------------------------
    path('calendario/', views.calendario, name='calendar'),
    path('calendario/<int:year>/<int:month>/', views.calendario, name='calendar'),
    path('calendario/<int:year>/<int:month>/<int:day>/', views.dia_actividades, name='day_events_view'),
    path('actividades/crear/', views.crear_actividad, name='crear_actividad'),
    path('actividades/<int:actividad_id>/unirse/', views.unirse_actividad, name='unirse_actividad'),
    path('actividades/<int:actividad_id>/abandonar/', views.abandonar_actividad, name='abandonar_actividad'),
    path('actividades/<int:actividad_id>/', views.detalles_actividad, name='detalles_actividad'),
    path('actividades/<int:actividad_id>/chat/', views.chat_actividad, name='chat_actividad'),
    path('mensajes_actividad/<int:mensaje_id>/editar/', views.editar_mensaje_actividad, name='editar_mensaje_actividad'),
    path('actividades/<int:actividad_id>/editar/', views.editar_actividad, name='editar_actividad'),
    path('mensajes_actividad/<int:mensaje_id>/eliminar/', views.eliminar_mensaje_actividad, name='eliminar_mensaje_actividad'),
    # ---------------------------------------------------------
    #              SECCION MENSAJES PRIVADOS
    # ---------------------------------------------------------
    path('mensajes/', views.mensajes_directos, name='mensajes_directos'),
    path('mensajes/enviar/<int:usuario_id>/', views.enviar_mensaje, name='enviar_mensaje'),
    path('mensajes/<int:usuario_id>/', views.detalle_conversacion, name='detalle_conversacion'),
    path('mensajes/<int:mensaje_id>/editar/', views.editar_mensaje_privado, name='editar_mensaje_privado'),
    path('mensajes/<int:mensaje_id>/eliminar/', views.eliminar_mensaje_privado, name='eliminar_mensaje_privado'),
        # ---------------------------------------------------------
    #              SECCION PUBLICACIONES
    # ---------------------------------------------------------
    path('comunidad/', views.social_home, name='social_home'),
    path('comunidad/publicacion/crear/', views.crear_publicacion, name='crear_publicacion'),
    path('publicacion/<int:publicacion_id>/like/', views.dar_like, name='dar_like'),
    path('publicacion/<int:publicacion_id>/comentario/', views.crear_comentario, name='crear_comentario'),
    path('publicacion/<int:publicacion_id>/delete/', views.eliminar_publicacion, name='eliminar_publicacion'),
    path('publicacion/<int:publicacion_id>/edit/', views.editar_publicacion, name='editar_publicacion'),
    path('comentario/<int:comentario_id>/delete/', views.eliminar_comentario, name='eliminar_comentario'),
    path('comentario/<int:comentario_id>/edit/', views.editar_comentario, name='editar_comentario'),
    path('publicacion/<int:publicacion_id>/', views.detalle_publicacion, name='detalle_publicacion'),
    # ---------------------------------------------------------
    #              SECCION RETOS
    # ---------------------------------------------------------
    path('retos/', views.listar_retos, name='listar_retos'),
    path('retos/crear/', views.crear_reto, name='crear_reto'),
    path('retos/<int:reto_id>/unirse/', views.unirse_reto, name='unirse_reto'),
    path('retos/<int:reto_id>/ranking/', views.ver_ranking, name='ver_ranking'),
    path('retos/<int:reto_id>/editar/', views.editar_reto, name='editar_reto'),
    path('retos/<int:reto_id>/eliminar/', views.eliminar_reto, name='eliminar_reto'),
     # ---------------------------------------------------------
    #              SECCION METAS
    # ----------------------------------------------------------
    path('metas/', views.listar_metas, name='listar_metas'),
    path('metas/crear/', views.crear_meta, name='crear_meta'),
    path('metas/<int:meta_id>/', views.detalle_meta, name='detalle_meta'),
    path('metas/<int:meta_id>/progreso/', views.registrar_progreso, name='registrar_progreso'),
    path('meta/<int:meta_id>/progreso/', views.obtener_progreso_meta, name='obtener_progreso_meta'),
    path('meta/editar/<int:meta_id>/', views.editar_meta, name='editar_meta'),
    path('meta/eliminar/<int:meta_id>/', views.eliminar_meta, name='eliminar_meta'),
     # ---------------------------------------------------------
    #              SECCION EJERCICIOS
    # ----------------------------------------------------------
    path('ejercicios/<str:parte_cuerpo>/', views.listar_ejercicios, name='listar_ejercicios'),

     # ---------------------------------------------------------
    #              SECCION ENTRENADOR VIRTUAL
    # ----------------------------------------------------------
    path("entrenador-virtual/", views.entrenador_virtual, name="entrenador_virtual"),
    ]







# ---------------------------------------------------------
#       Añadir rutas para archivos multimedia en debug
# ---------------------------------------------------------

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
