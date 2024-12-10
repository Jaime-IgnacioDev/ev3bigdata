CREATE TABLE viviendas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255),
    precio_uf VARCHAR(50),
    precio_clp VARCHAR(50),
    ubicacion_completa VARCHAR(255),
    calle VARCHAR(255),
    sector VARCHAR(255),
    ciudad VARCHAR(255),
    region VARCHAR(255),
    superficie FLOAT,
    dormitorios INT,
    banos INT,
    url VARCHAR(255),
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);
