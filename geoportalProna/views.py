from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import LoginForm
from .forms import RegistroUsuarioForm
from .models import Usuario
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
from django.http import FileResponse
#from osgeo import gdal
from django.views.decorators.cache import cache_control
import openai
from openai import OpenAI
# Create your views here.

@cache_control(max_age=3600)
def serve_geotiff(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'TCI.tif')
    
    # Verificar integridad del archivo primero
    #try:
    #    dataset = gdal.Open(file_path)
    #    if not dataset:
    #        raise ValueError("El archivo no es un GeoTIFF válido")
    #    dataset = None  # Cerrar el dataset
    #except Exception as e:
    #    return HttpResponse(f"Error en el archivo GeoTIFF: {str(e)}", status=500)
    
    response = FileResponse(
        open(file_path, 'rb'),
        content_type='image/tiff',
        headers={
            'Content-Disposition': 'inline',
            'Access-Control-Allow-Origin': '*'  # Importante para CORS
        }
    )
    return response

def mapa(request):
    '''return render(request, "")'''
    return render(request, "inicio.html")

def trazabilidad(request):
    '''return render(request, "")'''
    return render(request, "trazabilidad.html")

def ganaderia(request):
    return render(request, "mapa_ganaderia.html")

def documentos(request):
    with connection.cursor() as cursor:
        query = """SELECT id FROM ranchos """
        cursor.execute(query)
        resultados = cursor.fetchall()
        ranchos = [{'id': fila[0]} for fila in resultados]
    with connection.cursor() as cursor:
        query = """SELECT distinct(tipo) FROM mapas """
        cursor.execute(query)
        resultados = cursor.fetchall()
        mapas = [{'tipo': fila[0]} for fila in resultados]
    return render(request, "documentos.html",{'ranchos': ranchos, 'tipo_mapa': mapas})

@require_POST
@csrf_exempt
def consulta_mapas_ranchos(request):
    try:
        datos = json.loads(request.body)
        consulta = datos.get('datos')
        tipo = datos.get('tipo')
        print(tipo)
        if tipo == "rancho":
            with connection.cursor() as cursor:
                query="""SELECT tipo, direccion_descarga FROM public.mapas where fkrancho = %s
                        ORDER BY idmapa ASC """
                cursor.execute(query,[consulta])
                resultados = cursor.fetchall()
                mapas = [{'imagen': "mapas/" + fila[0]+ "/" + fila[1], 'tipo': fila[0]} for fila in resultados]
        else:
            with connection.cursor() as cursor:
                query="""SELECT tipo, direccion_descarga, fkrancho FROM public.mapas where tipo = %s
                        ORDER BY idmapa ASC """
                cursor.execute(query,[consulta])
                resultados = cursor.fetchall()
                mapas = [{'imagen': "mapas/" + fila[0]+ "/" + fila[1], 'tipo': fila[2]} for fila in resultados]

        return JsonResponse({
            "imagenes": mapas,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def agregar_usuario(request):
    #form = RegistroUsuarioForm()
    if request.method == 'POST':
            form = RegistroUsuarioForm(request.POST)
            if form.is_valid():
                # Procesar datos
                usuario = request.POST.get('usuario')
                nombre= request.POST.get('nombre')
                apellidos= request.POST.get('apellidos')
                contrasena= request.POST.get('contrasena')
                #nombre = form.cleaned_data()
                #return redirect('exito')
                usuario = Usuario.objects.create_user(username=usuario,password=contrasena,nombre=nombre,apellidos=apellidos)
                #usuario.save()
    else:
        form = RegistroUsuarioForm()
    return render(request, "agregar_usuarios.html", {'form': form})

def login_view(request):
    form = LoginForm(request, data=request.POST)
    if request.method == 'POST':
        print(form.errors)
        if form.is_valid():
                
            user = form.get_user()
            
            login(request, user)
            return redirect('administrador') 
    return render(request, 'login.html', {'form': form})

def enviar_login(request):
    #if request.method == 'POST':
    #    email = request.POST.get('email')
    #    password = request.POST.get('password')
    #    print(email)
    return render(request, "administrador.html")

def usuarios_total(request):
    #with connection.cursor() as cursor:
    #    cursor.execute("""
    #                   SELECT * FROM public.admin_app ORDER BY id ASC """)
    usuarios = Usuario.objects.all()
    print(usuarios)
        #columnas = [col[0] for col in cursor.description]  
        #print(columnas)
        #resultados = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]  # lista de diccionarios
    return render(request, "usuarios_todos.html",{'usuarios': usuarios})

@require_POST
@csrf_exempt
def update_productor(request):
    try:
        usuario_id = request.POST.get('id')
        print(usuario_id)
        usuario = Usuario.objects.get(id=usuario_id)

        fields = ['username', 'nombre', 'apellidos']
        for field in fields:
            if field in request.POST:
                setattr(usuario, field, request.POST.get(field))
        usuario.save()
        return JsonResponse({'success': True})
    except Usuario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Productor no encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
@csrf_exempt
def consulta_ranchos(request):
    try:
        datos = json.loads(request.body)
        rancho = datos.get('tabla')
        with connection.cursor() as cursor:
            query = """SELECT id, name, ST_AsGeoJSON(geom) AS geojson,
              ST_Area(geom::geography) as area FROM ranchos"""
            cursor.execute(query)
            resultados = cursor.fetchall()
            features = []
            for id, name, geojson, area in resultados:
                features.append({
                    "type": "Feature",
                    "geometry": json.loads(geojson),
                    "properties": {
                        "id": id,
                        "nombre": name,
                        "area" : area,
                        "tabla": rancho,
                    }
                })
        return JsonResponse({
            "type": "FeatureCollection",
            "features": features
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
@csrf_exempt
def consulta_climas(request):
    try:
        #datos = json.loads(request.body)
        #rancho = datos.get('tabla')
        with connection.cursor() as cursor:
            query = """SELECT id, tipo, ST_AsGeoJSON(geom) AS geojson FROM climas"""
            cursor.execute(query)
            resultados = cursor.fetchall()
            features = []
            for id, tipo, geojson in resultados:
                features.append({
                    "type": "Feature",
                    "geometry": json.loads(geojson),
                    "properties": {
                        "id": id,
                        "tipo": tipo,
                    }
                })
        return JsonResponse({
            "type": "FeatureCollection",
            "features": features
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
@csrf_exempt
def consulta_temperatura_max_may_oct(request):
    try:

        with connection.cursor() as cursor:
            query = """SELECT id, descrip, ST_AsGeoJSON(geom) AS geojson FROM public.temp_max_may_oct
"""
            cursor.execute(query)
            resultados = cursor.fetchall()
            features = []
            for id, descrip, geojson in resultados:
                features.append({
                    "type": "Feature",
                    "geometry": json.loads(geojson),
                    "properties": {
                        "id": id,
                        "tipo": descrip,
                    }
                })
        return JsonResponse({
            "type": "FeatureCollection",
            "features": features
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@require_POST
@csrf_exempt
def consulta_temperatura_max_nov_abr(request):
    try:

        with connection.cursor() as cursor:
            query = """SELECT id, descrip, ST_AsGeoJSON(geom) AS geojson FROM public.temp_max_nov_abr
"""
            cursor.execute(query)
            resultados = cursor.fetchall()
            features = []
            for id, descrip, geojson in resultados:
                features.append({
                    "type": "Feature",
                    "geometry": json.loads(geojson),
                    "properties": {
                        "id": id,
                        "tipo": descrip,
                    }
                })
        return JsonResponse({
            "type": "FeatureCollection",
            "features": features
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
@csrf_exempt
def consulta_temperatura_min_may_oct(request):
    try:

        with connection.cursor() as cursor:
            query = """SELECT id, descrip, ST_AsGeoJSON(geom) AS geojson FROM public.temp_min_may_oct
"""
            cursor.execute(query)
            resultados = cursor.fetchall()
            features = []
            for id, descrip, geojson in resultados:
                features.append({
                    "type": "Feature",
                    "geometry": json.loads(geojson),
                    "properties": {
                        "id": id,
                        "tipo": descrip,
                    }
                })
        return JsonResponse({
            "type": "FeatureCollection",
            "features": features
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
@csrf_exempt
def consulta_temperatura_min_nov_abr(request):
    try:

        with connection.cursor() as cursor:
            query = """SELECT id, descrip, ST_AsGeoJSON(geom) AS geojson FROM public.temp_min_nov_abr
"""
            cursor.execute(query)
            resultados = cursor.fetchall()
            features = []
            for id, descrip, geojson in resultados:
                features.append({
                    "type": "Feature",
                    "geometry": json.loads(geojson),
                    "properties": {
                        "id": id,
                        "tipo": descrip,
                    }
                })
        return JsonResponse({
            "type": "FeatureCollection",
            "features": features
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@require_POST
@csrf_exempt
def consulta_precp_may_oct(request):
    try:

        with connection.cursor() as cursor:
            query = """SELECT id, descrip, ST_AsGeoJSON(geom) AS geojson FROM public.precp_may_oct
"""
            cursor.execute(query)
            resultados = cursor.fetchall()
            features = []
            for id, descrip, geojson in resultados:
                features.append({
                    "type": "Feature",
                    "geometry": json.loads(geojson),
                    "properties": {
                        "id": id,
                        "tipo": descrip,
                    }
                })
        return JsonResponse({
            "type": "FeatureCollection",
            "features": features
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


require_POST
@csrf_exempt
def consulta_erosion(request):
    try:
        #datos = json.loads(request.body)
        #rancho = datos.get('tabla')
        with connection.cursor() as cursor:
            query = """SELECT id, intensidad, ST_AsGeoJSON(geom) AS geojson FROM erosion"""
            cursor.execute(query)
            resultados = cursor.fetchall()
            features = []
            for id, intensidad, geojson in resultados:
                features.append({
                    "type": "Feature",
                    "geometry": json.loads(geojson),
                    "properties": {
                        "id": id,
                        "tipo": intensidad,
                    }
                })
        return JsonResponse({
            "type": "FeatureCollection",
            "features": features
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


require_POST
@csrf_exempt
def consulta_geologia(request):
    try:
        #datos = json.loads(request.body)
        #rancho = datos.get('tabla')
        with connection.cursor() as cursor:
            query = """SELECT id, tipo, ST_AsGeoJSON(geom) AS geojson FROM geologia"""
            cursor.execute(query)
            resultados = cursor.fetchall()
            features = []
            for id, tipo, geojson in resultados:
                features.append({
                    "type": "Feature",
                    "geometry": json.loads(geojson),
                    "properties": {
                        "id": id,
                        "tipo": tipo,
                    }
                })
        return JsonResponse({
            "type": "FeatureCollection",
            "features": features
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

require_POST
@csrf_exempt
def consulta_deslizamiento(request):
    try:
        #datos = json.loads(request.body)
        #rancho = datos.get('tabla')
        with connection.cursor() as cursor:
            query = """SELECT id, tipo, ST_AsGeoJSON(geom) AS geojson FROM peligro_deslizamientos"""
            cursor.execute(query)
            resultados = cursor.fetchall()
            features = []
            for id, tipo, geojson in resultados:
                features.append({
                    "type": "Feature",
                    "geometry": json.loads(geojson),
                    "properties": {
                        "id": id,
                        "tipo": tipo,
                    }
                })
        return JsonResponse({
            "type": "FeatureCollection",
            "features": features
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


require_POST
@csrf_exempt
def consulta_rios(request):
    try:
        #datos = json.loads(request.body)
        #rancho = datos.get('tabla')
        with connection.cursor() as cursor:
            query = """SELECT id, ST_AsGeoJSON(geom) AS geojson FROM rios"""
            cursor.execute(query)
            resultados = cursor.fetchall()
            features = []
            for id, geojson in resultados:
                features.append({
                    "type": "Feature",
                    "geometry": json.loads(geojson),
                    "properties": {
                        "id": id,
                    }
                })
        return JsonResponse({
            "type": "FeatureCollection",
            "features": features
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

require_POST
@csrf_exempt
def consulta_suelos(request):
    try:
        #datos = json.loads(request.body)
        #rancho = datos.get('tabla')
        with connection.cursor() as cursor:
            query = """SELECT id, suelo, ST_AsGeoJSON(geom) AS geojson FROM suelos"""
            cursor.execute(query)
            resultados = cursor.fetchall()
            features = []
            for id, suelo, geojson in resultados:
                features.append({
                    "type": "Feature",
                    "geometry": json.loads(geojson),
                    "properties": {
                        "id": id,
                        "tipo": suelo,
                    }
                })
        return JsonResponse({
            "type": "FeatureCollection",
            "features": features
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

require_POST
@csrf_exempt
def consulta_topoformas(request):
    try:
        #datos = json.loads(request.body)
        #rancho = datos.get('tabla')
        with connection.cursor() as cursor:
            query = """SELECT id, descrip, ST_AsGeoJSON(geom) AS geojson FROM topoformas"""
            cursor.execute(query)
            resultados = cursor.fetchall()
            features = []
            for id,descrip,geojson in resultados:
                features.append({
                    "type": "Feature",
                    "geometry": json.loads(geojson),
                    "properties": {
                        "id": id,
                        "tipo": descrip,
                    }
                })
        return JsonResponse({
            "type": "FeatureCollection",
            "features": features
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


require_POST
@csrf_exempt
def consulta_usv_2014(request):
    try:
        #datos = json.loads(request.body)
        #rancho = datos.get('tabla')
        with connection.cursor() as cursor:
            query = """SELECT id, descrip, ST_AsGeoJSON(geom) AS geojson FROM uso_suelo_vegetacion"""
            cursor.execute(query)
            resultados = cursor.fetchall()
            features = []
            for id,descrip,geojson in resultados:
                features.append({
                    "type": "Feature",
                    "geometry": json.loads(geojson),
                    "properties": {
                        "id": id,
                        "tipo": descrip,
                    }
                })
        return JsonResponse({
            "type": "FeatureCollection",
            "features": features
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
@csrf_exempt
def consulta_graficos(request):
    try:
        def ejecutar_query(sql,rancho):
            with connection.cursor() as cursor:
                cursor.execute(sql,[rancho])
                return cursor.fetchall()
            
        datos = json.loads(request.body)
        rancho = datos.get('tabla')
        with connection.cursor() as cursor:
            suelos = ejecutar_query("""SELECT 
                    r.name AS dueno_rancho,
                    s.suelo AS tipo_suelo,
                    ST_Area(ST_Intersection(r.geom, s.geom)::geography) /10000 AS area_interseccion
                FROM 
                    ranchos r
                JOIN 
                    suelos s ON ST_Intersects(r.geom, s.geom)
                Where r.id = %s""",rancho)
            vegetacion_suelo = ejecutar_query("""SELECT 
                    r.name AS dueno_rancho,
                    v.descrip AS tipo_vegetacion,
                    ST_Area(ST_Intersection(r.geom, v.geom)::geography) /10000 AS area_interseccion
                FROM 
                    ranchos r
                JOIN 
                    uso_suelo_vegetacion v ON ST_Intersects(r.geom, v.geom)
                Where r.id = %s""",rancho)
            climas = ejecutar_query("""SELECT 
                    r.name AS dueno_rancho,
                    v.tipo AS climas_tipo,
                    ST_Area(ST_Intersection(r.geom, v.geom)::geography) /10000 AS area_interseccion
                FROM 
                    ranchos r
                JOIN 
                    climas v ON ST_Intersects(r.geom, v.geom)
                Where r.id = %s""",rancho)
            
            #suelos=  {     'titulo': 'Superficie de tipo de Suelo (Ha)',
            #                'labels': [v[1] for v in suelos],
            #                'datos': [v[2] for v in suelos],
            #            }
            #prompt = f"""Genera un análisis técnico breve a partir de estos datos de tipos de suelo (en hectáreas): {suelos}.
            #        Describe la función ecológica de cada tipo y su importancia para el uso agropecuario."""
            #respuesta = client.chat.completions.create(
            #            model="gpt-4o-mini",
            #            messages=[
            #                {"role": "user", "content": prompt}
            #            ]
            #        )

        #analisis = respuesta.choices[0].message.content
        return JsonResponse({
            'suelos': {
                'titulo': 'Superficie de tipo de Suelo (Ha)',
                'labels': [v[1] for v in suelos],
                'datos': [v[2] for v in suelos],
                #'reporte': analisis,
            },
            'veg_uso_suelo': {
                'titulo': 'Superficie de Vegetación y uso del Suelo (Ha)',
                'labels': [c[1] for c in vegetacion_suelo],
                'datos': [c[2] for c in vegetacion_suelo],
                #'reporte': analisis,
            },
            'climas': {
                'titulo': 'Superficie de Tipo de clima (Ha)',
                'labels': [c[1] for c in climas],
                'datos': [c[2] for c in climas],
                #'reporte': analisis,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
@csrf_exempt
def ganado(request):
    try:
        def ejecutar_query(sql,rancho):
            with connection.cursor() as cursor:
                cursor.execute(sql,[rancho])
                return cursor.fetchall()
            
        datos = json.loads(request.body)
        rancho = datos.get('tabla')
        with connection.cursor() as cursor:
            ganado = ejecutar_query("""SELECT 
                    idganado, nombre, raza, sexo, procedencia, peso, estado 
                    FROM public.ganado where fk_rancho = %s""",rancho)
            features = []
            for idganado, nombre, raza, sexo, procedencia, peso, estado in ganado:
                features.append({
                    "idganado": idganado,
                    "nombre": nombre,
                    "raza":raza,
                    "sexo": sexo,
                    "procedencia": procedencia,
                    "peso":peso,  
                    "estado": estado                  
                })
        return JsonResponse({"ganado": features})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
@csrf_exempt
def consulta_ganado(request):
    try:
        def ejecutar_query(sql,idGanado):
            with connection.cursor() as cursor:
                cursor.execute(sql,[idGanado])
                return cursor.fetchall()
            
        datos = json.loads(request.body)
        idGanado = datos.get('ganado')
        with connection.cursor() as cursor:
            vacuna = ejecutar_query("""SELECT 
                                    DATE_TRUNC('day',v.fecha_vacunacion)::DATE, 
                                    DATE_TRUNC('day',v.proxima_vacuna)::DATE, a.vacuna, a.descripcion
                                    FROM public.vacunacion v
                                    Join public.vacunas a on v.fkvacuna = a.idvacuna 
                                    where v.fkganado = %s""",idGanado)
            vacunas = []
            for fecha_vacuna, proxima_vacuna, tipo_vacuna, descripci in vacuna:
                vacunas.append({
                    "fecha_vacuna": fecha_vacuna,
                    "proxima_vacuna": proxima_vacuna,
                    "tipo_vacuna":tipo_vacuna,      
                    "descripcion": descripci,          
                })
            desparacitante = ejecutar_query("""SELECT 
                                    DATE_TRUNC('day',v.fecha_desparacitacion)::DATE, 
                                    DATE_TRUNC('day',v.proxima_fecha)::DATE, a.producto, a.descripcion
                                    FROM public.desparacitacion v 
                                    Join public.desparasitantes a on v.fkdesparasitante = a.iddesparasitantes
                                    where v.fkganado = %s""",idGanado)
            desparacitantes = []
            for fecha_desparacitacion, proxima_desparacitacion, tipo_desparacitande, descripci in desparacitante:
                desparacitantes.append({
                    "fecha_desparacitacion": fecha_desparacitacion,
                    "proxima_desparacitacion": proxima_desparacitacion,
                    "tipo_desparacitande":tipo_desparacitande,      
                    "descripcion": descripci,          
                })
        return JsonResponse({"vacunas": vacunas,
                             "desparacitantes":desparacitantes})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
@csrf_exempt
def reporte_general(request):
    try:
        def ejecutar_query(sql,idGanado):
            with connection.cursor() as cursor:
                cursor.execute(sql,[idGanado])
                return cursor.fetchall()
            
        datos = json.loads(request.body)
        idGanado = datos.get('ganado')
        with connection.cursor() as cursor:
            vacuna = ejecutar_query("""SELECT 
                                    DATE_TRUNC('day',v.fecha_vacunacion)::DATE, 
                                    DATE_TRUNC('day',v.proxima_vacuna)::DATE, a.vacuna, a.descripcion
                                    FROM public.vacunacion v
                                    Join public.vacunas a on v.fkvacuna = a.idvacuna 
                                    where v.fkganado = %s""",idGanado)
            vacunas = []
            for fecha_vacuna, proxima_vacuna, tipo_vacuna, descripci in vacuna:
                vacunas.append({
                    "fecha_vacuna": fecha_vacuna,
                    "proxima_vacuna": proxima_vacuna,
                    "tipo_vacuna":tipo_vacuna,      
                    "descripcion": descripci,          
                })
            desparacitante = ejecutar_query("""SELECT 
                                    DATE_TRUNC('day',v.fecha_desparacitacion)::DATE, 
                                    DATE_TRUNC('day',v.proxima_fecha)::DATE, a.producto, a.descripcion
                                    FROM public.desparacitacion v 
                                    Join public.desparasitantes a on v.fkdesparasitante = a.iddesparasitantes
                                    where v.fkganado = %s""",idGanado)
            desparacitantes = []
            for fecha_desparacitacion, proxima_desparacitacion, tipo_desparacitande, descripci in desparacitante:
                desparacitantes.append({
                    "fecha_desparacitacion": fecha_desparacitacion,
                    "proxima_desparacitacion": proxima_desparacitacion,
                    "tipo_desparacitande":tipo_desparacitande,      
                    "descripcion": descripci,          
                })
            parto = ejecutar_query("""SELECT DATE_TRUNC('day',v.fecha_parto)::DATE, a.nombre
                        FROM public.partos v Join public.ganado a on v.fkganadohijo = a.idganado
                        where v.fkganado = %s""",idGanado)
            partos = []
            for fecha_parto, nombre in parto:
                partos.append({
                    "fecha_parto": fecha_parto,
                    "nombre_becerro": nombre,     
                })
        return JsonResponse({"vacunas": vacunas,
                             "desparacitantes":desparacitantes,
                             "partos": partos})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
@csrf_exempt
def consulta_partos(request):
    try:
        def ejecutar_query(sql,idGanado):
            with connection.cursor() as cursor:
                cursor.execute(sql,[idGanado])
                return cursor.fetchall()
            
        datos = json.loads(request.body)
        idGanado = datos.get('ganado')
        with connection.cursor() as cursor:
            parto = ejecutar_query("""SELECT DATE_TRUNC('day',v.fecha_parto)::DATE, a.nombre
                        FROM public.partos v Join public.ganado a on v.fkganadohijo = a.idganado
                        where v.fkganado = %s""",idGanado)
            partos = []
            for fecha_parto, nombre in parto:
                partos.append({
                    "fecha_parto": fecha_parto,
                    "nombre_becerro": nombre,     
                })
        return JsonResponse({"partos": partos})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def agave(request):
    return render(request, "mapa_agave.html")

def cafe(request):
    return render(request, "mapa_cafe.html")

def prueba(request):
    return render(request, "prueba.html")