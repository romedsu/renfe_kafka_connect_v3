import logging
import requests
import time
import json
import psycopg2
# from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def conectar_db():
    while True:
        try:
            conn = psycopg2.connect("dbname=vuelos_asturias_db user=admin password=password123 host=postgres")
            logging.info("Conexión exitosa a la base de datos.")
            return conn
        except psycopg2.OperationalError:
            logging.warning("Base de datos no disponible. Reintentando en 5 segundos...")
            time.sleep(5)


# -- OPCION A - con select (solo imprime pantalla)
# url = "https://www.aena.es/es/asturias/aerolineas-y-destinos/destinos-del-aeropuerto.html"
# headers = {'User-Agent': 'Mozilla/5.0'}

# response = requests.get(url, headers=headers)
# soup = BeautifulSoup(response.text, 'html.parser')


# # Seleccionamos cada fila de resultado
# filas = soup.select('article.fila.resultado')

# for fila in filas:
#     # 1. Extraer destino (está en el primer li)
#     destino = fila.select_one('li[role="cell"] span.title').text.strip()
    
#     # 2. Extraer país (dentro de .detalles)
#     pais = fila.select_one('.detalles li:nth-of-type(1) .resultado').text.strip()
    
#     # 3. Extraer aerolíneas (puede haber varias, buscamos el texto del span nombre)
#     aerolineas = [a.text.strip() for a in fila.select('.detalles li:nth-of-type(2) span.nombre')]
    
#     print(f"Destino: {destino} | País: {pais} | Aerolíneas: {', '.join(aerolineas)}")


# --


# -- OPCION B
def guardar_db(data):
    conn = conectar_db()

    cur = conn.cursor()

    try:
        for d in data:        
            cur.execute("INSERT INTO rutasAenaAsturias (destino,pais,aerolinea) VALUES (%s, %s, %s)", 
                            (d['destino'], d['pais'],d['aerolinea']))
            conn.commit()

            logging.info(f"¡ÉXITO! Transacción guardada: {d}")

    except Exception as e:
        conn.rollback()
        logging.error(f"Error al insertar en la base de datos: {e}")
    finally:
        cur.close()
        conn.close()
        logging.info("Conexiones a la base de datos cerradas correctamente.")
    
     

def scraper_aena_asturias():
    url = "https://www.aena.es/es/asturias/aerolineas-y-destinos/destinos-del-aeropuerto.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        logging.error(f"Error al acceder a Aena: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    
    #  contenedor padre que agrupa cada destino 
    # inspeccionar qué clase envuelve al bloque completo de destino/pais/aerolinea

    # items = soup.find_all('article', class_="tabla tres-col h6 tag-result") 
    items = soup.find_all('article', class_="fila resultado regular filtered visible") 

    # logging.info(f'rutas ASTURIAS (OVD) : {items}')
    
    data = []
    for item in items:
        destino = item.find('span', class_='title bold').text.strip()
        pais = item.find('span', class_='resultado').text.strip()
        aerolinea = item.find('span', class_='nombre').text.strip()
        
        data.append({
            'destino': destino,
            'pais': pais,
            'aerolinea': aerolinea
        })
    
    df = pd.DataFrame(data)

    # crear columna id
    df.insert(0, 'id', range(1, len(df) + 1))
    
    # df.to_csv('/app/output/rutas_ovd.csv', index=True, index_label='id')
    df.to_csv('/app/output/rutas_aena_asturias.csv', index=False)

    logging.info(f"Web scraping con exito --> Se han guardado .csv --> {len(df)} rutas")

    guardar_db(data)

if __name__ == "__main__":
    scraper_aena_asturias()