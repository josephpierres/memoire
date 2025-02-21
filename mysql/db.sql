-- Création de la base de données
CREATE DATABASE IF NOT EXISTS gestion_bibliotheque CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Utilisation de la base de données
USE gestion_bibliotheque;

CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ISBN VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- insertion de donnees
ALTER TABLE books AUTO_INCREMENT=1;
insert into books (ISBN, user_id) values ('978-2-1234-5680-3', '1');
insert into books (ISBN, user_id) values ('978-2-1234-5680-4', '2');            
insert into books (ISBN, user_id) values ('978-2-1234-5680-5', '3');
insert into books (ISBN, user_id) values ('978-2-1234-5680-6', '4');
insert into books (ISBN, user_id) values ('978-2-1234-5680-7', '5');
insert into books (ISBN, user_id) values ('978-2-1234-5680-8', '6');
insert into books (ISBN, user_id) values ('978-2-1234-5680-9', '7');
insert into books (ISBN, user_id) values ('978-2-1234-5680-10', '8');


ALTER TABLE users AUTO_INCREMENT=1;
INSERT INTO users (name, email, password) VALUES ('admin', 'admin@bibliomgmt.net', 'admin');
INSERT INTO users (name, email, password) VALUES ('user1', 'user1@bibliomgmt.net', 'user1');
```