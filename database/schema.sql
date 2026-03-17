-- Création de la table universites
CREATE TABLE universites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255),
    lat FLOAT,
    lon FLOAT
);

-- Création de la table bibliotheques
CREATE TABLE bibliotheques (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255),
    lat FLOAT,
    lon FLOAT
);

-- Création de la table logements
CREATE TABLE logements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lat FLOAT,
    lon FLOAT,
    surface FLOAT,
    prix_m2 FLOAT,
    loyer_estime FLOAT
);
