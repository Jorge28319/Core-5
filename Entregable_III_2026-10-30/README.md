# Repórtate ya

Página web liviana para avisar, después de un sismo de gran magnitud en Chile, si estás bien o necesitas ayuda. WhatsApp sirve para conversar; Repórtate ya sirve para pasar lista.

Proyecto del Equipo 12 (paralelo 207) del ramo IWG400 Proyecto Inicial de la Universidad Técnica Federico Santa María: Sofía Sepúlveda Canales, Alexis Soto, Jorge Troncoso, Benjamín Troncoso y Mauricio Tolmo.

## Qué hace

- **Reporte con un toque (funcionalidad corazón):** la persona toca "Estoy bien" o "Necesito ayuda". El reporte guarda la hora, la ubicación GPS (si el navegador la entrega) y un detalle opcional de hasta 100 caracteres. Sin GPS, se pide una referencia escrita. El reporte aparece en todos los núcleos de la persona.
- **Panel por núcleo:** muestra a cada integrante con su estado, la hora de su reporte y un enlace a su ubicación. Primero aparecen quienes necesitan ayuda, luego quienes no se han reportado y al final quienes están bien.
- **Núcleos privados:** grupos como "Familia" u "Oficina" con un código de invitación de 6 caracteres. Solo sus integrantes ven los estados y ubicaciones.
- **Mapa del núcleo (opcional):** muestra en un mapa la última ubicación de cada integrante.

Cada emergencia se abre con el primer reporte en un núcleo y dura 72 horas.

## Requisitos

- Python 3.12 o más nuevo.
- Git.
- Las dependencias de Python están en `requirements.txt` (Django 6.1 y sus dependencias). Se instalan con `pip`, como se explica abajo.
- Conexión a internet solo para ver el mapa del núcleo, que carga la librería Leaflet y los mapas de OpenStreetMap. El resto funciona sin descargar nada externo.

## Cómo ejecutarlo localmente

En Windows, abre el Símbolo del sistema (cmd) y escribe estas líneas de a una:

```
git clone https://github.com/Jorge28319/Core-5.git
cd Core-5
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd proyectoInicial
python manage.py migrate
python manage.py runserver
```

En macOS o Linux, cambia la activación del entorno virtual por `source venv/bin/activate` y usa `python3` si `python` no existe.

Cuando aparezca `Starting development server at http://127.0.0.1:8000/`, abre `http://localhost:8000` en el navegador. Para detener el servidor, apreta Ctrl+C.

Qué hace cada paso:

1. `git clone` descarga el repositorio.
2. `python -m venv venv` crea un entorno virtual y `venv\Scripts\activate` lo activa (la línea pasa a empezar con `(venv)`).
3. `pip install -r requirements.txt` instala Django y sus dependencias.
4. `python manage.py migrate` crea la base de datos SQLite (`db.sqlite3`) con todas las tablas. La base de datos no está en el repositorio, así que parte vacía.
5. `python manage.py runserver` inicia la página.

Opcional: para ver y editar los datos en `http://localhost:8000/admin`, crea una cuenta de administración con `python manage.py createsuperuser` (la contraseña no se ve mientras se escribe).

## Datos para probar la funcionalidad corazón

Como la base de datos parte vacía, estos pasos crean dos cuentas y un núcleo de prueba. Para tener dos personas a la vez en el mismo computador, usa una ventana normal del navegador y una ventana de incógnito (Ctrl+Shift+N).

| Cuenta | Nombre | Correo | Contraseña |
| --- | --- | --- | --- |
| Persona 1 (ventana normal) | Ana | ana@prueba.cl | ReportateYa2026 |
| Persona 2 (ventana de incógnito) | Diego | diego@prueba.cl | ReportateYa2026 |

1. En la ventana normal, presiona **Crear cuenta** y registra a Ana. La página la lleva a **Núcleos**.
2. Crea un núcleo llamado **Familia**. Aparece con un código de invitación, por ejemplo `RJS-482`.
3. En la ventana de incógnito, registra a Diego y, en **Núcleos**, únete a **Familia** escribiendo ese código.

### Caso 1: reporte con ubicación (escenario principal)

1. Con Diego, entra a **Panel**. Cuando el navegador pregunte, permite compartir la ubicación; debe aparecer "Tu ubicación se adjuntará al reporte".
2. Toca **Necesito ayuda** sin escribir dónde estás.
3. Con Ana, entra a **Panel** (o toca **Actualizar**). Debe decir que hay una emergencia activa, mostrar a Diego primero con "Necesito ayuda", su hora y "Ver ubicación", y a Ana como "No se ha reportado".

### Caso 2: reporte sin ubicación (escenario alternativo)

1. Con Ana, bloquea la ubicación: haz clic en el ícono a la izquierda de `localhost:8000` en la barra de direcciones, cambia el permiso de ubicación a "Bloquear" y recarga.
2. Toca **Estoy bien** sin escribir dónde estás. No se guarda nada y aparece el mensaje "No pudimos obtener tu ubicación. Escribe dónde estás."
3. Escribe "en la casa" en **¿Dónde estás?** y vuelve a tocar **Estoy bien**. El reporte se guarda sin coordenadas, y el panel muestra a Ana con su hora y la referencia, sin enlace de ubicación.

### Otras pruebas

- **Mapa:** en el Panel, toca **Ver mapa** para ver a los integrantes que compartieron su ubicación. Como las dos cuentas usan el mismo computador, sus puntos quedan juntos; para separarlos, cambia la latitud y la longitud de un reporte en el administrador (por ejemplo, -33.4372 y -70.6506).
- **Privacidad:** en la dirección del Panel, cambia el número de `?nucleo=` por uno que no sea tuyo, como `?nucleo=999`. Debe aparecer la página de "no encontrado".

## Notas

- Los navegadores solo entregan la ubicación GPS en `localhost` o en sitios con HTTPS. En localhost funciona; para probarla en un celular, la página tiene que estar publicada con HTTPS.
- Las páginas usan CSS escrito a mano, sin imágenes ni fuentes descargadas, para que carguen con señal débil. Las excepciones son el script que obtiene la ubicación GPS, la librería Leaflet en la página del mapa y la foto del equipo en Nosotros.
- El panel no se recarga solo: para ver reportes nuevos hay que tocar **Actualizar**.

## Estructura del proyecto

```
Core-5/
├── requirements.txt
└── proyectoInicial/
    ├── manage.py
    ├── proyectoInicial/      configuración (settings.py) y direcciones (urls.py)
    └── core/                 la aplicación Repórtate ya
        ├── models.py         Nucleo, Membresia, Evento y Reporte
        ├── forms.py          formularios de cuentas, reporte y núcleos
        ├── views.py          páginas y lógica del reporte, el panel y el mapa
        ├── templates/        plantillas HTML
        └── static/core/      estilos.css y la foto del equipo
```
