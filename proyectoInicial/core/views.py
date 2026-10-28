import secrets
import string
import math

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CrearNucleoForm, RegistroForm, ReporteForm, UnirseForm
from .models import Evento, Membresia, Nucleo, Reporte

def inicio(request):
    return render(request, "core/inicio.html")


def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect("nucleos")
    else:
        form = RegistroForm()
    return render(request, "core/registro.html", {"form": form})

def abrir_eventos(nucleos, inicio):
    for nucleo in nucleos:
        hay_evento_activo = Evento.objects.filter(nucleo=nucleo, fecha_cierre__gt=inicio).exists()
        if not hay_evento_activo:
            Evento.objects.create(nucleo=nucleo, fecha_inicio=inicio)


ORDEN_ESTADOS = {"AYUDA": 0, "NO": 1, "BIEN": 2}


def estados_del_nucleo(nucleo):
    evento = Evento.objects.filter(nucleo=nucleo, fecha_cierre__gt=timezone.now()).order_by("-fecha_inicio").first()
    filas = []
    if evento:
        for membresia in nucleo.membresia_set.all():
            reporte = (
                Reporte.objects.filter(usuario=membresia.usuario, fecha_hora__gte=evento.fecha_inicio)
                .order_by("-fecha_hora")
                .first()
            )
            estado = reporte.estado if reporte else "NO"
            filas.append({"usuario": membresia.usuario, "reporte": reporte, "estado": estado})
        filas.sort(key=lambda fila: ORDEN_ESTADOS[fila["estado"]])
    return evento, filas


@login_required
def panel(request):
    nucleos = Nucleo.objects.filter(membresia__usuario=request.user)
    if request.method == "POST":
        form = ReporteForm(request.POST)
        if form.is_valid() and nucleos.exists():
            reporte = form.save(commit=False)
            reporte.usuario = request.user
            reporte.save()
            abrir_eventos(nucleos, reporte.fecha_hora)
            return redirect("panel")
    else:
        form = ReporteForm()
    ultimo = Reporte.objects.filter(usuario=request.user).order_by("-fecha_hora").first()

    seleccionado = None
    evento = None
    filas = []
    if nucleos.exists():
        nucleo_id = request.GET.get("nucleo", "")
        if nucleo_id.isdigit():
            seleccionado = get_object_or_404(nucleos, id=nucleo_id)
        else:
            seleccionado = nucleos.first()
        evento, filas = estados_del_nucleo(seleccionado)

    return render(request, "core/panel.html", {
        "form": form,
        "nucleos": nucleos,
        "ultimo": ultimo,
        "seleccionado": seleccionado,
        "evento": evento,
        "filas": filas,
        "ahora": timezone.now(),
    })
def generar_codigo():
    while True:
        letras = "".join(secrets.choice(string.ascii_uppercase) for _ in range(3))
        numeros = "".join(secrets.choice(string.digits) for _ in range(3))
        codigo = letras + numeros
        if not Nucleo.objects.filter(codigo_invitacion=codigo).exists():
            return codigo

@login_required
def nucleos(request):
    crear_form = CrearNucleoForm()
    unirse_form = UnirseForm()
    if request.method == "POST":
        accion = request.POST.get("accion")
        if accion == "crear":
            crear_form = CrearNucleoForm(request.POST)
            if crear_form.is_valid():
                nucleo = Nucleo.objects.create(
                    nombre=crear_form.cleaned_data["nombre"],
                    codigo_invitacion=generar_codigo(),
                    creador=request.user,
                )
                Membresia.objects.create(usuario=request.user, nucleo=nucleo, rol="creador")
                messages.success(request, f"Creaste el núcleo {nucleo.nombre}. Comparte el código con quienes quieras que estén en él.")
                return redirect("nucleos")
        elif accion == "unirse":
            unirse_form = UnirseForm(request.POST)
            if unirse_form.is_valid():
                nucleo = Nucleo.objects.get(codigo_invitacion=unirse_form.cleaned_data["codigo"])
                membresia, es_nueva = Membresia.objects.get_or_create(usuario=request.user, nucleo=nucleo)
                if es_nueva:
                    messages.success(request, f"Te uniste a {nucleo.nombre}.")
                else:
                    messages.info(request, f"Ya eras parte de {nucleo.nombre}.")
                return redirect("nucleos")
    mis_nucleos = Nucleo.objects.filter(membresia__usuario=request.user)
    return render(request, "core/nucleos.html", {
        "crear_form": crear_form,
        "unirse_form": unirse_form,
        "mis_nucleos": mis_nucleos,
    })

def nosotros(request):
    return render(request, "core/nosotros.html")


def enlace_mapa(lat, lng):
    return f"https://www.google.com/maps?q={lat},{lng}"


def distancia_km(lat1, lng1, lat2, lng2):
    radio_tierra = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2)
    return 2 * radio_tierra * math.asin(math.sqrt(a))


def texto_distancia(km):
    if km < 0.05:
        return "menos de 50 m"
    if km < 1:
        return f"{round(km * 1000, -1):.0f} m"
    return f"{km:.1f} km".replace(".", ",")


def puntos_mapa(filas):
    puntos = []
    for fila in filas:
        reporte = fila["reporte"]
        if reporte and reporte.latitud is not None:
            puntos.append({
                "lat": reporte.latitud,
                "lng": reporte.longitud,
                "nombre": fila["usuario"].first_name or fila["usuario"].username,
                "estado": fila["estado"],
                "hora": timezone.localtime(reporte.fecha_hora).strftime("%H:%M"),
                "enlace": enlace_mapa(reporte.latitud, reporte.longitud),
            })
    return puntos


@login_required
def mapa(request):
    nucleos = Nucleo.objects.filter(membresia__usuario=request.user)
    if not nucleos.exists():
        return redirect("nucleos")
    nucleo_id = request.GET.get("nucleo", "")
    if nucleo_id.isdigit():
        seleccionado = get_object_or_404(nucleos, id=nucleo_id)
    else:
        seleccionado = nucleos.first()