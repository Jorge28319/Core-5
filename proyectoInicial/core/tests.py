from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Evento, Membresia, Nucleo, Reporte


class SalirNucleoTests(TestCase):
    def setUp(self):
        self.ana = User.objects.create_user("ana@correo.cl", password="clave-segura-1", first_name="Ana")
        self.beto = User.objects.create_user("beto@correo.cl", password="clave-segura-2", first_name="Beto")
        self.casa = Nucleo.objects.create(nombre="Casa", codigo_invitacion="CAS111", creador=self.beto)
        self.trabajo = Nucleo.objects.create(nombre="Trabajo", codigo_invitacion="TRA222", creador=self.beto)
        for nucleo in (self.casa, self.trabajo):
            Membresia.objects.create(usuario=self.beto, nucleo=nucleo, rol="creador")
            Membresia.objects.create(usuario=self.ana, nucleo=nucleo)

    def reportar(self, usuario, estado):
        self.client.force_login(usuario)
        self.client.post(reverse("panel"), {"estado": estado, "referencia": "en la casa"})

    def filas_de(self, usuario, nucleo, vista="panel"):
        self.client.force_login(usuario)
        respuesta = self.client.get(reverse(vista), {"nucleo": nucleo.id})
        return [fila["usuario"] for fila in respuesta.context["filas"]]

    def test_quien_sale_ya_no_aparece_en_el_nucleo(self):
        self.reportar(self.ana, "AYUDA")
        self.client.post(reverse("salir_nucleo", args=[self.casa.id]))

        self.assertNotIn(self.ana, self.filas_de(self.beto, self.casa))
        self.assertNotIn(self.ana, self.filas_de(self.beto, self.casa, "mapa"))
        self.assertIn(self.ana, self.filas_de(self.beto, self.trabajo))
        self.assertEqual(Reporte.objects.filter(usuario=self.ana).count(), 1)

    def test_al_volver_no_aparecen_reportes_de_antes(self):
        self.reportar(self.ana, "AYUDA")
        self.client.post(reverse("salir_nucleo", args=[self.casa.id]))
        Membresia.objects.create(usuario=self.ana, nucleo=self.casa)

        self.client.force_login(self.beto)
        respuesta = self.client.get(reverse("panel"), {"nucleo": self.casa.id})
        fila_ana = next(f for f in respuesta.context["filas"] if f["usuario"] == self.ana)
        self.assertIsNone(fila_ana["reporte"])
        self.assertEqual(fila_ana["estado"], "NO")
        self.assertNotContains(respuesta, "Necesito ayuda</span>")

        # En el otro núcleo su reporte sigue visible
        respuesta = self.client.get(reverse("panel"), {"nucleo": self.trabajo.id})
        fila_ana = next(f for f in respuesta.context["filas"] if f["usuario"] == self.ana)
        self.assertEqual(fila_ana["estado"], "AYUDA")
        self.assertTrue(Evento.objects.filter(nucleo=self.casa).exists())
