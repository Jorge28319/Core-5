from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

DURACION_EVENTO = timedelta(hours=72)

class Nucleo(models.Model):
    nombre = models.CharField(max_length=50)
    codigo_invitacion = models.CharField(max_length=6, unique=True)
    creador = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Membresia(models.Model):
    ROLES = [
        ("creador", "Creador"),
        ("integrante", "Integrante"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nucleo = models.ForeignKey(Nucleo, on_delete=models.CASCADE)
    rol = models.CharField(max_length=10, choices=ROLES, default="integrante")
    fecha_union = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["usuario", "nucleo"], name="membresia_unica"),
        ]

    def __str__(self):
        return f"{self.usuario} en {self.nucleo}"

class Evento(models.Model):
    nucleo = models.ForeignKey(Nucleo, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_cierre = models.DateTimeField(blank=True)

    def save(self, *args, **kwargs):
        if self.fecha_cierre is None:
            self.fecha_cierre = self.fecha_inicio + DURACION_EVENTO
        super().save(*args, **kwargs)

    def esta_activo(self):
        return timezone.now() < self.fecha_cierre

    def __str__(self):
        return f"Evento de {self.nucleo}"

class Reporte(models.Model):
    ESTADOS = [
        ("BIEN", "Estoy bien"),
        ("AYUDA", "Necesito ayuda"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.CharField(max_length=5, choices=ESTADOS)
    detalle = models.CharField(max_length=100, blank=True)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    referencia = models.CharField(max_length=100, blank=True)
    fecha_hora = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.usuario}: {self.get_estado_display()}"