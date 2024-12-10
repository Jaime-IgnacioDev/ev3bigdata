import json
import mysql.connector

# Configuración de conexión a la base de datos MySQL en Azure
conn = mysql.connector.connect(
    host="viviendascrap.mysql.database.azure.com",
    user="jaime",
    password="1596big.",
    database="viviendascrap",
    port=3306
)

cursor = conn.cursor()

# Leer los datos desde el archivo JSON
with open('viviendas.json', 'r', encoding='utf-8') as json_file:
    data_list = json.load(json_file)

# Insertar los datos (solo si no existe la URL)
for data in data_list:
    try:
        # Verificar si la URL ya existe en la base de datos
        cursor.execute("""
            SELECT COUNT(*) FROM viviendas WHERE url = %s
        """, (data['URL'],))
        exists = cursor.fetchone()[0]

        if not exists:
            # Insertar los datos en la tabla
            cursor.execute("""
                INSERT INTO viviendas (
                    titulo, precio_uf, precio_clp, ubicacion_completa, calle, sector, ciudad, region, superficie, dormitorios, banos, url
                ) VALUES (
                    %(Titulo)s, %(Precio_UF)s, %(Precio_CLP)s, %(ubicacion_completa)s, %(calle)s, %(sector)s, %(ciudad)s, %(region)s, %(Superficie)s, %(Dormitorios)s, %(Banos)s, %(URL)s
                )
            """, data)
            conn.commit()
            print(f"Datos insertados para la URL: {data['URL']}")
        else:
            print(f"Vivienda con URL {data['URL']} ya existe, no se insertará.")

    except mysql.connector.Error as err:
        print(f"Error al insertar datos: {err}")
        conn.rollback()

# Cerrar la conexión
cursor.close()
conn.close()

print("Proceso completado. Datos del JSON han sido insertados en la base de datos.")
