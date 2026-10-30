"""
URL configuration for proyectoInicial project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from core import views
from core.forms import IngresoForm
urlpatterns = [path("nucleos/", views.nucleos, name="nucleos"),
    path("nucleos/<int:nucleo_id>/salir/", views.salir_nucleo, name="salir_nucleo"),    path("mapa/", views.mapa, name="mapa"),
    path("registro/", views.registro, name="registro"),
    path("admin/", admin.site.urls),
    path("", views.inicio, name="inicio"), path("panel/", views.panel, name="panel"),
    path("ingresar/", auth_views.LoginView.as_view(authentication_form=IngresoForm), name="login"),
    path("salir/", auth_views.LogoutView.as_view(), name="logout"),
    path("nosotros/", views.nosotros, name="nosotros"),
]
