"""
URL configuration for geoportal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from geoportalProna import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.mapa, name='inicio'),
    path('mapa_ganaderia', views.ganaderia, name='mapaGanaderia'),
    path('documentos/', views.documentos, name='documentos'),
    path('login/', views.login_view, name="login"),
    path('administrador/', views.enviar_login, name="administrador"),
    path('mapa_agave/', views.agave, name="mapaAgave"),
    path('mapa_cafe/', views.cafe, name="mapaCafe"),
    path('prueba', views.prueba, name="prueba"),
    path('trazabilidad', views.trazabilidad, name="trazabilidad"),
    path('agregar_usuarios', views.agregar_usuario, name="agregar_usuarios"),
    path('usuarios_todos', views.usuarios_total, name="usuarios"),
    path('usuarios/update', views.update_productor, name='usuarios_update'),
    path('consulta_ranchos', views.consulta_ranchos, name="consulta_ranchos"),
    path('consulta_suelos', views.consulta_suelos, name="consulta_suelos"),
    path('consulta_climas', views.consulta_climas, name = "consulta_climas"),
    path('consulta_erosion', views.consulta_erosion, name = "consulta_erosion"),
    path('consulta_geologia', views.consulta_geologia, name = "consulta_geologia"),    
    path('consulta_deslizamiento', views.consulta_deslizamiento, name = "consulta_deslizamiento"),    
    path('consulta_rios', views.consulta_rios, name = "consulta_rios"),  
    path('consulta_usv_2014', views.consulta_usv_2014, name = "consulta_usv_2014"),  
    path('consulta_topoformas', views.consulta_topoformas, name = "consulta_topoformas"), 
    path('consulta_graficos', views.consulta_graficos, name = "consulta_graficos"), 
    path('consulta_mapas_ranchos', views.consulta_mapas_ranchos, name = "consulta_mapas_ranchos"),
    path('consulta_temperatura_max_may_oct', views.consulta_temperatura_max_may_oct, name = "consulta_temperatura_max_may_oct"),
    path('consulta_temperatura_max_nov_abr', views.consulta_temperatura_max_nov_abr, name = "consulta_temperatura_max_nov_abr"),
    path('consulta_temperatura_min_may_oct', views.consulta_temperatura_min_may_oct, name = "consulta_temperatura_min_may_oct"),
    path('consulta_temperatura_min_nov_abr', views.consulta_temperatura_min_nov_abr, name = "consulta_temperatura_min_nov_abr"),
    path('consulta_precp_may_oct', views.consulta_precp_may_oct, name = "consulta_precp_may_oct"),
    path('ganado', views.ganado, name = "ganado"),
    path('geotiff/', views.serve_geotiff, name = "serve_geotiff"),
    path('consulta_ganado', views.consulta_ganado, name = "consulta_ganado"),
    path('consulta_partos', views.consulta_partos, name = "consulta_partos"),
    path('reporte_general', views.reporte_general, name = "reporte_general"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)