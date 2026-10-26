import secrets
import string

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
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
            return redirect("inicio")
    else:
        form = RegistroForm()
    return render(request, "core/registro.html", {"form": form})

def abrir_eventos(nucleos):
    ahora = timezone.now()
    for nucleo in nucleos:
        hay_evento_activo = Evento.objects.filter(nucleo=nucleo, fecha_cierre__gt=ahora).exists()
        if not hay_evento_activo:
            Evento.objects.create(nucleo=nucleo)


@login_required
def panel(request):
    nucleos = Nucleo.objects.filter(membresia__usuario=request.user)
    if request.method == "POST":
        form = ReporteForm(request.POST)
        if form.is_valid() and nucleos.exists():
            reporte = form.save(commit=False)
            reporte.usuario = request.user
            reporte.save()
            abrir_eventos(nucleos)
            return redirect("panel")
    else:
        form = ReporteForm()
    ultimo = Reporte.objects.filter(usuario=request.user).order_by("-fecha_hora").first()
    return render(request, "core/panel.html", {"form": form, "nucleos": nucleos, "ultimo": ultimo})

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