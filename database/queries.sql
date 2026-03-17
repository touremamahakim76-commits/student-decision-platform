
-- Nombre total de logements
SELECT COUNT(*) AS total_logements
FROM logements;

-- Nombre total de bibliothèques
SELECT COUNT(*) AS total_bibliotheques
FROM bibliotheques;

-- Nombre total d’universités
SELECT COUNT(*) AS total_universites
FROM universites;

-- Loyer moyen estimé
SELECT AVG(loyer_estime) AS loyer_moyen
FROM logements;

-- Prix moyen au m²
SELECT AVG(prix_m2) AS prix_moyen_m2
FROM logements;

-- Liste des universités
SELECT nom
FROM universites
ORDER BY nom ASC;

-- Top 10 logements les moins chers
SELECT *
FROM logements
ORDER BY loyer_estime ASC
LIMIT 10;
