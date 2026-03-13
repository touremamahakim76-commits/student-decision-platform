CREATE TABLE universite (
    id INT PRIMARY KEY,
    nom VARCHAR(255),
    ville VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT
);

CREATE TABLE bibliotheque (
    id INT PRIMARY KEY,
    nom VARCHAR(255),
    ville VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT
);

CREATE TABLE appartement (
    id INT PRIMARY KEY,
    nom VARCHAR(255),
    adresse VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT
);
