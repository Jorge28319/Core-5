from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Evento, Membresia, Nucleo, Reporte


class BorrarCuentaTests(TestCase):
    def setUp(self):
        self.ana = User.objects.create_user("ana@correo.cl", password="clave-segura-1", first_name="Ana")
        self.beto = User.objects.create_user("beto@correo.cl", password="clave-segura-2", first_name="Beto")
        # Ana creó "Casa" y Beto está en él; "Solo Ana" no tiene a nadie más; Beto creó "Trabajo"
        self.casa = Nucleo.objects.create(nombre="Casa", codigo_invitacion="CAS111", creador=self.ana)
        self.solo = Nucleo.objects.create(nombre="Solo Ana", codigo_invitacion="SOL222", creador=self.ana)
        self.trabajo = Nucleo.objects.create(nombre="Trabajo", codigo_invitacion="TRA333", creador=self.beto)
        Membresia.objects.create(usuario=self.ana, nucleo=self.casa, rol="creador")
        Membresia.objects.create(usuario=self.beto, nucleo=self.casa)
        Membresia.objects.create(usuario=self.ana, nucleo=self.solo, rol="creador")
        Membresia.objects.create(usuario=self.beto, nucleo=self.trabajo, rol="creador")
        Membresia.objects.create(usuario=self.ana, nucleo=self.trabajo)
        Reporte.objects.create(usuario=self.ana, estado="AYUDA", referencia="en la casa")
        Reporte.objects.create(usuario=self.beto, estado="BIEN", referencia="en la oficina")
        Evento.objects.create(nucleo=self.casa)
        self.client.force_login(self.ana)

    def test_mi_cuenta_pide_iniciar_sesion(self):
        self.client.logout()
        respuesta = self.client.get(reverse("mi_cuenta"))
        self.assertRedirects(respuesta, reverse("login") + "?next=" + reverse("mi_cuenta"))

    def test_el_nombre_del_encabezado_lleva_a_mi_cuenta(self):
        respuesta = self.client.get(reverse("inicio"))
        self.assertContains(respuesta, f'<a href="{reverse("mi_cuenta")}" class="persona"')

    def test_mi_cuenta_lleva_a_la_confirmacion(self):
        respuesta = self.client.get(reverse("mi_cuenta"))
        self.assertContains(respuesta, reverse("borrar_cuenta"))
        self.assertContains(respuesta, "Borrar mi cuenta")

    def test_abrir_la_confirmacion_no_borra_nada(self):
        respuesta = self.client.get(reverse("borrar_cuenta"))
        self.assertContains(respuesta, "no se puede deshacer")
        self.assertContains(respuesta, "csrfmiddlewaretoken")
        self.assertTrue(User.objects.filter(id=self.ana.id).exists())

    def test_contrasena_incorrecta_no_borra_nada(self):
        respuesta = self.client.post(reverse("borrar_cuenta"), {"password": "otra-clave"})
        self.assertContains(respuesta, "La contraseña no es correcta")
        self.assertTrue(User.objects.filter(id=self.ana.id).exists())
        self.assertEqual(Reporte.objects.filter(usuario=self.ana).count(), 1)
        self.assertEqual(Membresia.objects.filter(usuario=self.ana).count(), 3)
        self.assertEqual(Nucleo.objects.count(), 3)

    def test_contrasena_correcta_borra_la_cuenta(self):
        respuesta = self.client.post(reverse("borrar_cuenta"), {"password": "clave-segura-1"}, follow=True)

        self.assertRedirects(respuesta, reverse("login"))
        self.assertContains(respuesta, "Tu cuenta fue eliminada")
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertFalse(User.objects.filter(id=self.ana.id).exists())
        self.assertFalse(Reporte.objects.filter(usuario_id=self.ana.id).exists())
        self.assertFalse(Membresia.objects.filter(usuario_id=self.ana.id).exists())

        # El núcleo que Ana creó sigue para Beto, con él como creador y su evento intacto
        self.casa.refresh_from_db()
        self.assertEqual(self.casa.creador, self.beto)
        self.assertEqual(Membresia.objects.get(nucleo=self.casa).rol, "creador")
        self.assertTrue(Evento.objects.filter(nucleo=self.casa).exists())
        # El núcleo donde Ana estaba sola se borra
        self.assertFalse(Nucleo.objects.filter(id=self.solo.id).exists())
        # El núcleo de Beto y su reporte no se tocan
        self.assertTrue(Membresia.objects.filter(usuario=self.beto, nucleo=self.trabajo).exists())
        self.assertEqual(Reporte.objects.filter(usuario=self.beto).count(), 1)
