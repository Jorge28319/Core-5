from django.contrib import admin

from .models import Evento, Membresia, Nucleo, Reporte

admin.site.register(Nucleo)
admin.site.register(Membresia)
admin.site.register(Evento)
admin.site.register(Reporte)