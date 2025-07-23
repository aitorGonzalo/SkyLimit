🏋️‍♂️ SkyLimit – Plataforma social para salud y deporte

SkyLimit es una red social móvil que combina tecnologías avanzadas, deporte, y bienestar físico y mental, con el objetivo de combatir el sedentarismo y promover hábitos saludables a través de la tecnología y la comunidad.
🌍 Introducción

En un contexto global donde el sedentarismo y la obesidad son crecientes problemas de salud pública, SkyLimit surge como una solución integral para fomentar la actividad física, la motivación y el acompañamiento profesional, todo desde un mismo entorno digital.

El proyecto está orientado tanto a personas que buscan mejorar su salud como a deportistas que quieren mantenerse activos, con especial atención en deportes extremos como el surf y el esquí, incorporando funciones de seguimiento y condiciones climáticas en tiempo real.
🎯 Objetivos del proyecto

    Promover hábitos saludables en la población

    Motivar la actividad física a través de la comunidad y el soporte profesional

    Integrar herramientas tecnológicas modernas en el ámbito del deporte y la salud

    Ofrecer una plataforma integral, intuitiva y accesible desde dispositivos móviles

🧠 Características principales

    🤖 Entrenador Virtual
    Genera planes de entrenamiento personalizados con ayuda de inteligencia artificial.

    🧍 Cuerpo Dinámico Interactivo
    Interfaz visual donde se pueden seleccionar grupos musculares para obtener ejercicios específicos.

    🌐 Red Social Saludable
    Espacio de interacción para compartir progreso, publicaciones, comentarios y reacciones.

    🧑‍🏫 Conexión con Entrenadores Verificados
    Comunicación directa con profesionales de la salud y el deporte.

    🌦️ Monitorización del Clima en Zonas Deportivas
    Información en tiempo real sobre condiciones meteorológicas para actividades al aire libre.

    📱 Diseño 100% adaptable a dispositivos móviles
    Experiencia fluida, intuitiva y accesible en cualquier momento y lugar.

    🧬 Integración con APIs externas basadas en IA
    Recomendación de ejercicios, traducción de contenido y adaptación inteligente al nivel del usuario.

👨‍🎓 Autor

Aitor Gonzalo González
Grado en Ingeniería Informática de Gestión y Sistemas de Información
Trabajo de Fin de Grado – SkyLimit
💡 Motivación

Este proyecto nace del interés por aplicar soluciones tecnológicas al ámbito de la salud y el deporte, promoviendo un estilo de vida activo mediante herramientas interactivas, personalizadas y accesibles para cualquier tipo de usuario.

SkyLimit busca ir más allá del simple registro de actividad, construyendo una comunidad motivadora, ofreciendo asesoramiento profesional, y utilizando inteligencia artificial para mejorar el rendimiento y la salud de las personas.
📈 Impacto esperado

    Reducción del sedentarismo y mejora de la salud general

    Acompañamiento profesional accesible desde el móvil

    Creación de una comunidad enfocada en el bienestar integral

    Democratización del acceso a rutinas personalizadas mediante tecnología



## 📄 Memoria del proyecto

Puedes descargar la memoria completa del proyecto desde este enlace:  
[Descargar Memoria SkyLimit (PDF)](https://drive.google.com/file/d/1D9bjyhW6tgHBdRSGxDxrHQT3bHjIbUti/view?usp=drive_link)

## Prerrequisitos

- Python 3.x instalado
- `pip` instalado (normalmente incluido con Python)
- Virtualenv (opcional pero recomendado)

## Instrucciones de instalación y ejecución
git clone https://github.com/aitorGonzalo/SkyLimit
### 1. Crear un entorno virtual

Es altamente recomendable usar un entorno virtual para evitar conflictos entre dependencias. Sigue los pasos según tu sistema operativo:

#### En Linux/MacOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

Con el entorno virtual activado, instala las dependencias necesarias ejecutando:

```bash
pip install -r requirements.txt
Aplica las migraciones

python manage.py migrate
Restaura datos con el backup

python manage.py loaddata backup.json
```

### 4. Ejecutar la aplicación

Después de instalar las dependencias, inicia el servidor local con el siguiente comando:

```bash
python manage.py runserver
```

### 5. Acceder a la aplicación

Abre tu navegador web y accede a la siguiente URL:

[http://localhost:8000](http://localhost:8000)
