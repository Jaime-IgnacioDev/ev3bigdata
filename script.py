from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time
import json

# Configuración de Firefox con uBlock Origin
options = Options()
driver = webdriver.Firefox(options=options)

# Ruta al archivo de la extensión uBlock Origin
ublock_origin_path = "C:/Users/jaime/AppData/Roaming/Mozilla/Firefox/Profiles/boe7k7wq.default-release/extensions/uBlock0@raymondhill.net.xpi"

# Instalar uBlock Origin
driver.install_addon(ublock_origin_path, temporary=True)

# Abrir la página principal
driver.get("https://www.portalinmobiliario.com/")
time.sleep(5)  # Esperar a que la página cargue

# Lista para almacenar los datos de las viviendas
datos_viviendas = []

# Número máximo de viviendas que queremos scrapear
max_viviendas = 10
viviendas_scrapeadas = 0

while viviendas_scrapeadas < max_viviendas:
    try:
        # Encontrar viviendas en la página
        viviendas = driver.find_elements(By.CSS_SELECTOR, 
            "#react-aria-\\:R27r\\: > div:nth-child(2) > div:nth-child(2) > div")
        
        for vivienda in viviendas:
            if viviendas_scrapeadas >= max_viviendas:
                break

            try:
                # Click en la vivienda
                vivienda.click()
                time.sleep(3)

                # Extraer datos
                precio = driver.find_element(By.CSS_SELECTOR, "span.andes-money-amount__fraction:nth-child(3)").text
                ubicacion = driver.find_element(By.CSS_SELECTOR, "div.ui-pdp-media__body:nth-child(2) > p:nth-child(1)").text
                dormitorios = driver.find_element(By.CSS_SELECTOR, "#\\:R2imsha9im\\:-value").text
                banos = driver.find_element(By.CSS_SELECTOR, "#\\:R2iusha9im\\:-value").text
                superficie = driver.find_element(By.CSS_SELECTOR, "#\\:R2iesha9im\\:-value").text
                estacionamiento = driver.find_element(By.CSS_SELECTOR, "#\\:R2j6sha9im\\:-value").text

                # Guardar en formato JSON
                vivienda_datos = {
                    "precio": precio,
                    "ubicacion": ubicacion,
                    "dormitorios": dormitorios,
                    "banos": banos,
                    "superficie": superficie,
                    "estacionamiento": estacionamiento
                }
                datos_viviendas.append(vivienda_datos)
                viviendas_scrapeadas += 1
                print(f"Vivienda {viviendas_scrapeadas} extraída exitosamente.")

            except Exception as e:
                print(f"Error al extraer datos de la vivienda: {e}")
            
            # Volver a la página principal
            driver.find_element(By.CSS_SELECTOR, ".nav-logo").click()
            time.sleep(3)

    except Exception as e:
        print(f"Error al manejar la página: {e}")
        break

# Guardar los datos en un archivo JSON
with open("viviendas.json", "w", encoding="utf-8") as archivo:
    json.dump(datos_viviendas, archivo, ensure_ascii=False, indent=4)

# Cerrar el navegador
driver.quit()

print("Scraping completado. Datos guardados en 'viviendas.json'.")


import mysql.connector 

# Conexión a la base de datos MySQL en Azure
conn = mysql.connector.connect(
    host="viviendas.mysql.database.azure.com", 
    user="jaime",
    password="1596big.",
    database="viviendascrap", 
    port=3306
)

cursor = conn.cursor()

# Leer los datos del archivo JSON generado
with open("viviendas.json", "r", encoding="utf-8") as archivo:
    datos_viviendas = json.load(archivo)

# Insertar los datos en la tabla
for vivienda in datos_viviendas:
    cursor.execute("""
    INSERT INTO viviendas (precio, ubicacion, dormitorios, banos, superficie, estacionamiento)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        vivienda["precio"],
        vivienda["ubicacion"],
        vivienda["dormitorios"],
        vivienda["banos"],
        vivienda["superficie"],
        vivienda["estacionamiento"]
    ))

# Confirmar los cambios
conn.commit()

# Cerrar la conexión
cursor.close()
conn.close()

print("Datos insertados correctamente en la base de datos.")
