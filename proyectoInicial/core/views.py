from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import RegistroForm, ReporteForm

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

@login_required
def panel(request):
    form = ReporteForm()
    return render(request, "core/panel.html", {"form": form})