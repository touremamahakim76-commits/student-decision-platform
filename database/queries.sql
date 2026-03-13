-- Number of universities
SELECT COUNT(*) FROM universite;

-- Average number of libraries per area
SELECT ville, COUNT(*) FROM bibliotheque GROUP BY ville;

-- Example analysis query
SELECT * FROM appartement ORDER BY latitude;
