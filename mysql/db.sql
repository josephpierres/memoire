-- Création de la base de données
CREATE DATABASE IF NOT EXISTS gestion_bibliotheque CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Utilisation de la base de données
USE gestion_bibliotheque;

CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    ISBN VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- insertion de donnees
ALTER TABLE books AUTO_INCREMENT=1;
INSERT INTO books (title, ISBN, user_id) VALUES ('Le seigneur des anneaux', '978-2-226-13100-9', '1');
INSERT INTO books (title, ISBN, user_id) VALUES ('Harry Potter', '178-2-226-13100-6', '2');
INSERT INTO books (title, ISBN, user_id) VALUES ('La marque de la bete', '578-2-226-13100-7', '3');
INSERT INTO books (title, ISBN, user_id) VALUES ('Le Prince Harry', '978-5-226-13100-5', '4'); 
```