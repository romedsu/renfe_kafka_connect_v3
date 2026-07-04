import json
import logging
from confluent_kafka import avro
from confluent_kafka.avro import AvroConsumer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.basicConfig(level=logging.INFO)

# icao24
# callsign
# pais_origen



# CONFIGURACION
SCHEMA_REGISTRY_URL = 'http://schema-registry:8081'
BOOTSTRAP_SERVERS = 'kafka:9092'
TOPIC_INPUT = 'datos_api_vuelos_asturias'

# cargar schema .avsc
try:
    value_schema = avro.load('./schemas/vuelos_schema.avsc')
except Exception as e:
    logging.error(f"No se pudo cargar el archivo de esquema: {e}")
    exit(1)

ruta = "/app/data/dic_rutas_callsign.json"

def cargar_diccionario():
    try:
        with open(ruta,'r',encoding='utf-8') as f:
            return json.load(f)
    
    except Exception as e:
        logging.error(f'Error al cargar el diccionario')
        return {}
    
diccionario_rutas = cargar_diccionario()


# consumer
def main():
    consumer_conf = {
        'bootstrap.servers': BOOTSTRAP_SERVERS,
        'schema.registry.url': SCHEMA_REGISTRY_URL,
        'group.id': 'vuelos_asturias_update',
        'auto.offset.reset': 'earliest'
    }
    try:
        consumer = AvroConsumer(
                            config=consumer_conf,
                            reader_key_schema=None,
                            reader_value_schema=value_schema
                            )
        
        consumer.subscribe([TOPIC_INPUT])

        logging.info(f"Conectado con éxito a Kafka ({BOOTSTRAP_SERVERS})")    

    except Exception as e:
        logging.error(f"Error al conectar con {TOPIC_INPUT}: {e}")
        exit(1)


    logging.info("Consumidor iniciado. Esperando mensajes...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None: continue

            # Deserialización automática a diccionario de Python
            datos_vuelo = msg.value()
            
            # Enriquecimiento mediante búsqueda de clave
            callsign = datos_vuelo.get("callsign")
            info_ruta = diccionario_rutas.get(callsign, {})

            if info_ruta:
                datos_vuelo.update(info_ruta)
                logging.info(f"Vuelo {callsign} update: {datos_vuelo['origen']['codigo']} -> {datos_vuelo['destino']['codigo']}")
            else:
                logging.warning(f"Vuelo {callsign} no encontrado en el diccionario.")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    main()