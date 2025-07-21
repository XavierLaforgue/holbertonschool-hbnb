-- A script that creates the tables needed by the app and adds some
-- records to those tables.

-- DROP TABLE IF EXISTS place_amenity;
-- DROP TABLE IF EXISTS reviews;
-- DROP TABLE IF EXISTS places;
-- DROP TABLE IF EXISTS amenities;
-- DROP TABLE IF EXISTS users;

CREATE TABLE users(
	id CHAR(36) PRIMARY KEY NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	first_name VARCHAR(255) NOT NULL,
	last_name VARCHAR(255) NOT NULL,
	email VARCHAR(255) NOT NULL,
	password VARCHAR(255) NOT NULL,
	is_admin BOOLEAN DEFAULT FALSE,
	UNIQUE(email)
);

CREATE TABLE places(
	id CHAR(36) PRIMARY KEY NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	title VARCHAR(255) NOT NULL,
	description TEXT,
	price DECIMAL(10, 2) NOT NULL,
	latitude FLOAT NOT NULL,
	longitude FLOAT NOT NULL,
	owner_id CHAR(36),

	FOREIGN KEY (owner_id) REFERENCES users(id)
);

CREATE TABLE reviews(
	id CHAR(36) PRIMARY KEY NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	text TEXT NOT NULL,
	rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
	user_id CHAR(36) NOT NULL,
	place_id CHAR(36) NOT NULL,

	FOREIGN KEY (user_id) REFERENCES users(id),
	FOREIGN KEY (place_id) REFERENCES places(id),
	UNIQUE(user_id, place_id)
);

CREATE TABLE amenities(
	id CHAR(36) PRIMARY KEY NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	name VARCHAR(255) NOT NULL,
	UNIQUE(name)
);

CREATE TABLE place_amenity(
	place_id CHAR(36),
	amenity_id CHAR(36),

	FOREIGN KEY (place_id) REFERENCES places(id),
	FOREIGN KEY (amenity_id) REFERENCES amenities(id),
	CONSTRAINT PK_place_amenity PRIMARY KEY (place_id, amenity_id)
);

CREATE TRIGGER update_users_updated_at
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER update_places_updated_at
AFTER UPDATE ON places
FOR EACH ROW
BEGIN
    UPDATE places SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER update_reviews_updated_at
AFTER UPDATE ON reviews
FOR EACH ROW
BEGIN
    UPDATE reviews SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER update_amenities_updated_at
AFTER UPDATE ON amenities
FOR EACH ROW
BEGIN
    UPDATE amenities SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

INSERT INTO users(id, created_at, updated_at, email, first_name, last_name, password, is_admin)
VALUES (
	'36c9050e-ddd3-4c3b-9731-9f487208bbc1',
	CURRENT_TIMESTAMP,
	CURRENT_TIMESTAMP,
	'admin@hbnb.io',
	'Admin',
	'HBnB',
	'$2y$10$5Qks2w8WX6UwdrFxZy3dQe2rgy5RU.P6ReQfUgyX9fCDaouxY/El.',
	True
	);

INSERT INTO users(id, created_at, updated_at, email, first_name, last_name, password, is_admin)
VALUES (
	'40a54b25-fc77-4353-94c8-50d882600b86',
	CURRENT_TIMESTAMP,
	CURRENT_TIMESTAMP,
	'admin@example.com',
	'Admin',
	'User',
	'$2b$12$tqImhttAtUNGQOjPqI5PZ.GFOqkO.owLSJiG16bOtT4LCzmQTaoWG',
	True
	);

INSERT INTO users(id, created_at, updated_at, email, first_name, last_name, password, is_admin)
VALUES (
	'c6eca9ff-cd38-402e-afe2-e24949a4d858',
	CURRENT_TIMESTAMP,
	CURRENT_TIMESTAMP,
	'deleted@example.com',
	'Deleted',
	'User',
	'$2b$12$KoRE19LjSeh8pAGLYdd9Q.DMMCYs7TH3EYFizvdoyuaX62JFg2TmW',
	False
	);

INSERT INTO users(id, created_at, updated_at, email, first_name, last_name, password, is_admin)
VALUES (
	'6fb5f1c1-f9d4-4987-aee3-16ab71704835',
	CURRENT_TIMESTAMP,
	CURRENT_TIMESTAMP,
	'test@example.com',
	'Test',
	'User',
	'$2b$12$KoRE19LjSeh8pAGLYdd9Q.DMMCYs7TH3EYFizvdoyuaX62JFg2TmW',
	False
	);

INSERT INTO users(id, created_at, updated_at, email, first_name, last_name, password, is_admin)
VALUES (
	'7414383a-c590-41aa-a4a5-02c11b8f2b17',
	CURRENT_TIMESTAMP,
	CURRENT_TIMESTAMP,
	'test2@example.com',
	'Second Test',
	'User',
	'$2b$12$KoRE19LjSeh8pAGLYdd9Q.DMMCYs7TH3EYFizvdoyuaX62JFg2TmW',
	False
	);

INSERT INTO amenities(id, created_at, updated_at, name)
VALUES (
	'9505dcd5-2d59-403f-a6da-b818e1db9d55',
	CURRENT_TIMESTAMP,
	CURRENT_TIMESTAMP,
	'WiFi'
);

INSERT INTO amenities(id, created_at, updated_at, name)
VALUES (
	'2cfb7c28-d405-4856-af63-28d033968df0',
	CURRENT_TIMESTAMP,
	CURRENT_TIMESTAMP,
	'Swimming Pool'
);

INSERT INTO amenities(id, created_at, updated_at, name)
VALUES(
	'a6d13673-416b-4cea-99cc-d846583cfcd1',
	CURRENT_TIMESTAMP,
	CURRENT_TIMESTAMP,
	'Air Conditioning'
);

INSERT INTO places(id, title, description, price, 
				   latitude, longitude, owner_id)
VALUES(
	'9962e46f-05fa-4ac2-9617-b53d06713a33',
	'Appartment of Test User',
	'It is an OK place',
	20,
	0,
	0,
	'6fb5f1c1-f9d4-4987-aee3-16ab71704835'
);

INSERT INTO places(id, title, description, price, 
				   latitude, longitude, owner_id)
VALUES(
	'121c0d34-a070-4773-b1bf-b850da8b2607',
	'Appartment of Second Test User',
	'It is a bad place',
	10,
	0,
	0,
	'7414383a-c590-41aa-a4a5-02c11b8f2b17'
);

INSERT INTO reviews(id, text, rating, user_id, place_id)
VALUES(
	'8785d826-963b-4294-b67d-3a4b0983e2e5',
	"I didn't like this place at all",
	1,
	'6fb5f1c1-f9d4-4987-aee3-16ab71704835',
	'121c0d34-a070-4773-b1bf-b850da8b2607'
);

INSERT INTO reviews(id, text, rating, user_id, place_id)
VALUES(
	'385fbe4c-34f8-4155-b850-cb1e4bd78a0e',
	"This place was not bad, not great either, but not bad",
	3,
	'7414383a-c590-41aa-a4a5-02c11b8f2b17',
	'9962e46f-05fa-4ac2-9617-b53d06713a33'	
);
