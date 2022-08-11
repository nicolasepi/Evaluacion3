import requests
import json
from tabulate import tabulate
from datetime import datetime
from conf import conf_properties

# Deshabilitar los mensajes de Warnings del certificado SLL autofirmado
requests.packages.urllib3.disable_warnings()


#Obtener Token mediante usuario y contrasena almacenados en archivo "conf/conf_properties.py"
def login(user, password):
    url = conf_properties.url_API + "/api/aaaLogin.json"
    body = {
        "aaaUser": {
            "attributes": {
                "name": user,
                "pwd": password
            }
        }
    }
    header = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=header, data=json.dumps(body), verify=False)
    except Exception as error:
        print("Error al obtener Token por problemas de conectividad")
        exit(1)
    token = response.json()['imdata'][0]['aaaLogin']['attributes']['token']
    name = response.json()['imdata'][0]['aaaLogin']['attributes']['firstName']
    lastname = response.json()['imdata'][0]['aaaLogin']['attributes']['lastName']
    print(u'\u2500' * 80)
    print("Sesion creada correctamente, TokenID: " + token)
    #Se devuelve el nombre del responsable de la cuenta de usuario
    print("Nombre del usuario: " + name, lastname)
    print(u'\u2500' * 80)
    return token


#Eliminar el token creada para borrar la sesión de usuario
def logout(user, key):
    url = conf_properties.url_API + "/api/aaaLogout.json"
    body = {
        "aaaUser": {
            "attributes": {
                "name": user
            }
        }
    }
    header = {
        "Content-Type": "application/json"
    }
    cookie = {
        "APIC-Cookie": key
    }
    try:
        response = requests.post(url, headers=header, data=json.dumps(body), cookies=cookie, verify=False)
    except Exception as error:
        print("Error al eliminar la sesion por problemas de conectividad")
        exit(1)
    print("Sesión cerrada, token destruido.")


#Información general sobre los objetos del sistema
def top_system():
    header = {
        "Content-Type": "application/json"
    }
    cookie = {
        "APIC-Cookie": token
    }
    try:
        respuesta = requests.get(conf_properties.url_API + "/api/class/topSystem.json", headers=header, cookies=cookie, verify=False)
    except Exception as error:
        print("Error al consumir el API por problemas de conexión")
        exit(1)
    total_nodos = int(respuesta.json()["totalCount"])
    table = []
    #Se genera el header para la el formato de la tabla de datos
    columns = ['DN','Nombre', 'IP', 'MAC', 'Estado', 'Uptime']

    for i in range(0, total_nodos):
        dn_local = respuesta.json()["imdata"][i]["topSystem"]["attributes"]["dn"]
        name_local = respuesta.json()["imdata"][i]["topSystem"]["attributes"]["name"]
        ip_local = respuesta.json()["imdata"][i]["topSystem"]["attributes"]["address"]
        mac_local = respuesta.json()["imdata"][i]["topSystem"]["attributes"]["fabricMAC"]
        state_local = respuesta.json()["imdata"][i]["topSystem"]["attributes"]["state"]
        uptime_local = respuesta.json()["imdata"][i]["topSystem"]["attributes"]["systemUpTime"]
        insert = (dn_local, name_local, ip_local, mac_local, state_local, uptime_local)
        table.append(insert)
    print(tabulate(table, headers=columns, tablefmt='grid'))


#Mostrar las versiones disponibles de software en el controlador
def show_version():
    cabecera = {
        "Content-Type": "application/json"
    }
    galleta = {
        "APIC-Cookie": token
    }
    try:
        respuesta = requests.get(conf_properties.url_API + "/api/class/compatCtlrFw.json", headers=cabecera, cookies=galleta, verify=False)
    except Exception as err:
        print("Error al consumir el API por problemas de conexión")
        exit(1)
    total_nodos = int(respuesta.json()["totalCount"])
    table = []
    # Se genera el header para la el formato de la tabla de datos
    columns = ['DN','Nombre', 'Vendor', 'Version']
    for i in range(0, total_nodos):
        dn_version = respuesta.json()["imdata"][i]["compatCtlrFw"]["attributes"]["dn"]
        name_version = respuesta.json()["imdata"][i]["compatCtlrFw"]["attributes"]["name"]
        vendor_version = respuesta.json()["imdata"][i]["compatCtlrFw"]["attributes"]["vendor"]
        ver_version = respuesta.json()["imdata"][i]["compatCtlrFw"]["attributes"]["version"]
        insert = (dn_version, name_version, vendor_version, ver_version)
        table.append(insert)
    print(tabulate(table, headers=columns, tablefmt='grid'))


#Mostrar los Tenants de la arqutiectura
def show_tenant():
    cabecera = {
        "Content-Type": "application/json"
    }
    galleta = {
        "APIC-Cookie": token
    }
    try:
        respuesta = requests.get(conf_properties.url_API + "/api/class/fvTenant.json", headers=cabecera, cookies=galleta, verify=False)
    except Exception as err:
        print("Error al consumir el API por problemas de conexión")
        exit(1)
    total_nodos = int(respuesta.json()["totalCount"])
    table = []
    # Se genera el header para la el formato de la tabla de datos
    columns = ['DN', 'Nombre', 'UID']
    for i in range(0, total_nodos):
        dn_tenant = respuesta.json()["imdata"][i]["fvTenant"]["attributes"]["dn"]
        name_tenant = respuesta.json()["imdata"][i]["fvTenant"]["attributes"]["name"]
        uid_tenant = respuesta.json()["imdata"][i]["fvTenant"]["attributes"]["uid"]
        insert = (dn_tenant, name_tenant, uid_tenant)
        table.append(insert)
    print(tabulate(table, headers=columns, tablefmt='grid'))


#Crear un nuevo tenant bajo le nombre de la hora actual
def new_tenant():
    now = datetime.now()
    name_date = now.strftime("%H%M%S")
    header = {
        "Content-Type": "application/json"
    }
    cookie = {
        "APIC-Cookie": token
    }
    body = {
        "fvTenant": {
            "attributes": {
                "name": name_date
            }
        }
    }
    try:
        respuesta = requests.post(conf_properties.url_API + "/api/mo/uni.json", headers=header, data=json.dumps(body), cookies=cookie, verify=False)
    except Exception as err:
        print("Error al consumir el API por problemas de conexión")
        exit(1)
    print("Nuevo Tenant creado con exito con el nombre: " + name_date)


token = login(conf_properties.user, conf_properties.password)
print("Crear un nuevo Tenant utilizando la hora como nombre")
new_tenant()
print(u'\u2500' * 80)
print("Información General de los elementos del sistema")
top_system()
print(u'\u2500' * 80)
print("Información General de los Firmware del Controlador")
show_version()
print(u'\u2500' * 80)
print("Lista de los Tenants de la Arquitectura")
show_tenant()
print(u'\u2500' * 80)
logout(conf_properties.user, token)

