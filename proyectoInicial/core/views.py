from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .models import Evento, Nucleo, Reporte
from .forms import RegistroForm, ReporteForm
from django.utils import timezone

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