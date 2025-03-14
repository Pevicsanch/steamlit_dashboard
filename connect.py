import os
from dotenv import load_dotenv
import logging
from databricks import sql

# Configurar el logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_db_connection():
    """
    Crea una conexión a Databricks utilizando `server_hostname`, `http_path` y `access_token`
    desde variables de entorno.
    """
    load_dotenv()  # Cargar variables de entorno

    server_hostname = os.getenv("SERVER_HOSTNAME")
    http_path = os.getenv("HTTP_PATH")
    access_token = os.getenv("ACCESS_TOKEN")

    # Verificar que las variables estén definidas
    if not all([server_hostname, http_path, access_token]):
        logger.error("Las variables SERVER_HOSTNAME, HTTP_PATH y ACCESS_TOKEN deben estar definidas en el archivo .env")
        raise EnvironmentError("Configuración de conexión incompleta en el archivo .env")

    try:
        # Establecer conexión con Databricks
        connection = sql.connect(
            server_hostname=server_hostname,
            http_path=http_path,
            access_token=access_token
        )
        logger.info("Conexión establecida exitosamente con Databricks.")
        return connection
    except sql.Error as e:
        logger.error(f"Error al conectar con Databricks: {str(e)}")
        raise e
    
def test_db_connection():
    """
    Prueba la conexión a Databricks ejecutando una consulta simple.
    """
try:
    # Crear la conexión
    conn = create_db_connection()

    # Crear un cursor y ejecutar una consulta de prueba
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `eptu`.`layer_gold`.`volume_washes_per_day_location_product_short` LIMIT 1")  # Consulta básica que debería funcionar en la mayoría de los entornos

    # Obtener el resultado
    result = cursor.fetchone()
    if result:
        logger.info(f"Conexión exitosa. Resultado de prueba: {result}")
    else:
        logger.warning("Conexión establecida, pero no se obtuvo ningún resultado.")

    # Cerrar la conexión
    cursor.close()
    conn.close()
    logger.info("Conexión cerrada correctamente.")

except Exception as e:
    logger.error(f"Error al probar la conexión: {str(e)}")