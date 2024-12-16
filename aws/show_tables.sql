show TABLES;

SELECT * FROM Premios;

SELECT * FROM Sorteos;

SHOW CREATE TABLE Premios;

-- See details for Premios
DESCRIBE Premios;

-- See details for Sorteos
DESCRIBE Sorteos;

-- check there is not text values in monto
SELECT monto FROM Premios WHERE monto NOT REGEXP '^[0-9]+(\.[0-9]{1,2})?$';

SELECT * FROM Premios ORDER BY monto;

SELECT * FROM Premios WHERE monto = "NO VENDIDO";