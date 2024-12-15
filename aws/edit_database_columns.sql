-- Rename column vendido_por
ALTER TABLE Premios
CHANGE COLUMN vendido_por vendedor VARCHAR(255);


-- Add missing columns in Premios
ALTER TABLE Premios
ADD COLUMN ciudad VARCHAR(255),
ADD COLUMN departamento VARCHAR(255);