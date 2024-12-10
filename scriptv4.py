import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import mysql.connector

# Configuración inicial
driver = webdriver.Chrome(service=Service("chromedriver-win64/chromedriver.exe"))

# URL base
BASE_URL = "https://www.portalinmobiliario.com/venta/casa/los-lagos"
driver.get(BASE_URL)

# Aceptar cookies
try:
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "newCookieDisclaimerButton"))).click()
    print("Cookies aceptadas.")
except TimeoutException:
    print("No se encontró el botón para aceptar cookies, continuando...")

# Lista para almacenar los datos extraídos
data_list = []

# Guardar el identificador de la ventana principal
main_window = driver.current_window_handle

while True:
    # Esperar a que los resultados carguen
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ui-search-result-image__element")))
    except TimeoutException:
        print("No se pudieron cargar los resultados.")
        break

    # Obtener las propiedades en la página actual
    elements = driver.find_elements(By.CLASS_NAME, "ui-search-result-image__element")

    # Iterar por cada vivienda y extraer datos
    for element in elements:
        try:
            # Abrir la vivienda en una nueva pestaña
            driver.execute_script("arguments[0].click();", element)
            
            # Cambiar a la nueva pestaña
            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
            new_window = [window for window in driver.window_handles if window != main_window][0]
            driver.switch_to.window(new_window)
            
            # Esperar a que la página de detalles cargue
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ui-pdp-title")))
            
            # Extraer información de la vivienda
            data = {}
            
            # Título
            data['Titulo'] = driver.find_element(By.CLASS_NAME, "ui-pdp-title").text
            
            # Precio (UF o CLP)
            price_container = driver.find_element(By.ID, "price")
            data['Precio_UF'] = price_container.find_element(By.CLASS_NAME, "andes-money-amount__fraction").text
            try:
                data['Precio_CLP'] = price_container.find_element(By.CSS_SELECTOR, "div.ui-pdp-price__subtitles span.andes-money-amount__fraction").text
            except NoSuchElementException:
                data['Precio_CLP'] = None

            # Ubicación
            try:
                data['ubicacion_completa'] = driver.find_element(By.XPATH, '//*[@id="location"]/div/div[1]/div/p').text
            except NoSuchElementException:
                data['ubicacion_completa'] = None

            # Procesar la ubicación en sus componentes
            if data['ubicacion_completa']:
                parts = data['ubicacion_completa'].split(", ")
                if len(parts) == 4:
                    data['calle'] = parts[0]
                    data['sector'] = parts[1]
                    data['ciudad'] = parts[2]
                    data['region'] = parts[3]
                elif len(parts) == 3:
                    data['calle'] = parts[0]
                    data['sector'] = None
                    data['ciudad'] = parts[1]
                    data['region'] = parts[2]
                else:
                    data['calle'] = parts[0]
                    data['sector'] = None
                    data['ciudad'] = None
                    data['region'] = "Los Lagos"  # Asumiendo que la región siempre es Los Lagos
            else:
                data['calle'] = None
                data['sector'] = None
                data['ciudad'] = None
                data['region'] = "Los Lagos"  # Asumiendo que la región siempre es Los Lagos
            
            # Superficie
            try:
                superficie = driver.find_element(By.XPATH, '//*[@id="highlighted_specs_res"]/div/div[1]/span').text
                data['Superficie'] = float(superficie.split()[0])  # Convertir a float
            except NoSuchElementException:
                data['Superficie'] = None
            
            # Dormitorios
            try:
                dormitorios = driver.find_element(By.XPATH, '//*[@id="highlighted_specs_res"]/div/div[2]/span').text
                data['Dormitorios'] = int(dormitorios.split()[0])  # Convertir a int
            except NoSuchElementException:
                data['Dormitorios'] = None
            
            # Baños (se cambia 'Baños' a 'Banos' para evitar conflictos)
            try:
                banos = driver.find_element(By.XPATH, '//*[@id="highlighted_specs_res"]/div/div[3]/span').text
                data['Banos'] = int(banos.split()[0])  # Convertir a int
            except NoSuchElementException:
                data['Banos'] = None
            
            # Agregar URL
            data['URL'] = driver.current_url

            # Guardar los datos en la lista
            data_list.append(data)
            
            # Cerrar la pestaña actual y volver a la principal
            driver.close()
            driver.switch_to.window(main_window)

        except Exception as e:
            print(f"Error al procesar una vivienda: {e}")
            try:
                driver.switch_to.window(main_window)
            except Exception as switch_error:
                print(f"Error al cambiar de ventana: {switch_error}")
                driver.quit()
                break

    # Intentar hacer clic en el botón "Siguiente" para cargar la siguiente página
    try:
        next_button = driver.find_element(By.XPATH, '//*[@id="root-app"]/div/div[3]/section/nav/ul/li[12]')
        if "disabled" not in next_button.get_attribute("class"):  # Verificar si el botón está habilitado
            next_button.click()
            print("Cargando la siguiente página...")
            time.sleep(5)  # Esperar un poco antes de continuar
        else:
            print("No hay más páginas.")
            break
    except NoSuchElementException:
        print("No se encontró el botón 'Siguiente'. Finalizando.")
        break

# Guardar los datos extraídos en un archivo JSON
with open("viviendas.json", "w", encoding="utf-8") as file:
    json.dump(data_list, file, ensure_ascii=False, indent=4)

# Cerrar el navegador
driver.quit()

print("Extracción completada. Datos guardados en viviendas.json.")

# Conexión a la base de datos MySQL en Azure
conn = mysql.connector.connect(
    host="viviendascrap.mysql.database.azure.com",
    user="jaime",
    password="1596big.",
    database="viviendascrap",
    port=3306
)

cursor = conn.cursor()

# Leer los datos desde el archivo JSON
with open('viviendas.json', 'r') as json_file:
    data_list = json.load(json_file)

# Insertar los datos (solo si no existe la URL)
for data in data_list:
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM viviendas WHERE url = %s
        """, (data['URL'],))
        exists = cursor.fetchone()[0]

        if not exists:
            cursor.execute("""
                INSERT INTO viviendas (
                    titulo, precio_uf, precio_clp, ubicacion_completa, calle, sector, ciudad, region, superficie, dormitorios, banos, url
                ) VALUES (
                    %(Titulo)s, %(Precio_UF)s, %(Precio_CLP)s, %(ubicacion_completa)s, %(calle)s, %(sector)s, %(ciudad)s, %(region)s, %(Superficie)s, %(Dormitorios)s, %(Banos)s, %(URL)s
                )
            """, data)
            conn.commit()
        else:
            print(f"Vivienda con URL {data['URL']} ya existe, no se insertará.")

    except mysql.connector.Error as err:
        print(f"Error al insertar datos: {err}")
        conn.rollback()

# Cerrar la conexión
cursor.close()
conn.close()
