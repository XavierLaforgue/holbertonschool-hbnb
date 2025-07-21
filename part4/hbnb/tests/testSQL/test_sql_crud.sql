-- A script that tests the CRUD operations

.print ' -- ########## USERS ########## -- '

-- ### Read users before creation of new records ###
.print '# Read all users before additional creation of records #'
SELECT first_name, last_name, email, is_admin, updated_at FROM users;

-- ### Create users ###
INSERT INTO users(id, created_at, updated_at, email, first_name, last_name, password, is_admin)
VALUES (
	'0c095bc9-8ac4-4d50-b16b-e3da1e8ea3fb',
	CURRENT_TIMESTAMP,
	CURRENT_TIMESTAMP,
	'bob@crash.com',
	'bob',
	'dylan',
	'$2y$10$wTNrdOTbq4ZA3Vbzc1Nh..vzXBJzEmy2pWANeZ2SiQ4bo.NFEY6Ke',
	False
);


INSERT INTO users(id, created_at, updated_at, email, first_name, last_name, password, is_admin)
VALUES (
	'e4f87197-440f-47ae-8a27-1e1f23184be0',
	CURRENT_TIMESTAMP,
	CURRENT_TIMESTAMP,
	'bon@tranche.com',
	'jean',
	'bon',
	'$2y$10$UV5BJ0cDYUO2uQWr9SLfb.FfLzkZD475Xl3HENXtXvdcOaoTGLnKy',
	False
);

INSERT INTO users(id, created_at, updated_at, email, first_name, last_name, password, is_admin)
VALUES (
	'3b670ec5-1ff8-4431-8de7-2b646b05bd3b',
	CURRENT_TIMESTAMP,
	CURRENT_TIMESTAMP,
	'god@almighty.com',
	'supreme',
	'god',
	'$2y$10$hkpyfaMvL0iVp4Dl/FjhVuUusulCQhRCoZp3L6JnV8V8SaMiV3Dju',
	True
);

.print '# Expecting ERROR: Try to create user with an email already in use #'
INSERT INTO users(id, email, first_name, last_name, password)
VALUES (
	'9a51d348-ebcb-4fba-a16f-0399b411ca79',
	'bon@tranche.com',
	'Bad',
	'Email',
	'$2y$10$hkpyfaMvL0iVp4Dl/FjhVuUusulCQhRCoZp3L6JnV8V8SaMiV3Dju'
);

.print '# Read only the first_name of all admins #'
SELECT first_name from users WHERE is_admin = True;

.print '# Read only the email of all non-admins #'
SELECT email from users WHERE is_admin = False;

-- ### Update users ###
.print '# Update last_name of user with email bob@crash.com (reading before the update) #'
SELECT last_name, updated_at FROM users;
UPDATE users SET last_name = "'dead' dylan"
WHERE email = 'bob@crash.com';
.print '# Update of the last_name (reading after the update) #'
SELECT last_name, updated_at FROM users;

.print '# Update of the email of user bon@tranche.com to bon@sandwich.com (reading before the update) #'
SELECT email FROM users;
UPDATE users SET email = 'bon@sandwich.com'
WHERE email = 'bon@tranche.com';
.print '# Update of the email (reading after the update) #'
SELECT email FROM users;

.print '# Expecting ERROR: Update of the email of user test2@example.com to test@example.com #'
SELECT email FROM users;
UPDATE users SET email = 'test@example.com'
WHERE email = 'test2@example.com';
.print '# Reading after failed update #'
SELECT email FROM users;

-- ### Delete users ###
.print '# Delete user first_name="jean" (reading before the deletion) #'
SELECT first_name FROM users;
DELETE FROM users WHERE first_name = 'jean';
.print '# Reading after the deletion #'
SELECT first_name FROM users;

.print ' -- ########## PLACES ########## -- '

-- ### Create Place ###
INSERT OR IGNORE INTO places(id, created_at, updated_at, title, description, price, latitude, longitude, owner_id)
VALUES (
	'1992dcc6-c608-4874-ac01-76d8c58bbd64',
	CURRENT_TIMESTAMP,
	CURRENT_TIMESTAMP,
	'Maison de Campagne',
	"Petite maison cosy pour profiter d'un petit moment sympa",
	250,
	49.6460955,
	2.9596039,
	'0c095bc9-8ac4-4d50-b16b-e3da1e8ea3fb'
);

INSERT OR IGNORE INTO places(id, created_at, updated_at, title, description, price, latitude, longitude, owner_id)
VALUES (
	'2e039425-2acd-4b87-94de-3336ee838e7e',
	CURRENT_TIMESTAMP,
	CURRENT_TIMESTAMP,
	'Appartement Perdu',
	"Pour retrouver ce qu'on a perdu",
	300,
	18.46667,
	-72.46667,
	'3b670ec5-1ff8-4431-8de7-2b646b05bd3b'
);

INSERT OR IGNORE INTO places(id, created_at, updated_at, title, description, price, latitude, longitude, owner_id)
VALUES (
	'13840f3f-2cbc-4aeb-97a4-2930da5a3465',
	CURRENT_TIMESTAMP,
	CURRENT_TIMESTAMP,
	'Loft en bord de Mer',
	"Pour découvrir ce qui s'y cache",
	150,
	47.7083642,
	1.5062706,
	'e4f87197-440f-47ae-8a27-1e1f23184be0'
);


-- ### Read places ###
.print '# Read all the places #'
SELECT title, description FROM places;

.print '# Read all the places where title begin by Loft #'
SELECT title, description FROM places WHERE title LIKE 'Loft%';

-- ### Update places ###
.print '# Update description of a place (reading before the update) #'
SELECT description FROM places;
UPDATE places SET description = 'Pour se retrouver' WHERE id = '2e039425-2acd-4b87-94de-3336ee838e7e';
.print '# Update description of a place (reading after the update) #'
SELECT description FROM places;

.print '# Update location of a place (reading before the update) #'
SELECT title, latitude, longitude
FROM places
WHERE title = 'Loft en bord de Mer';
UPDATE places SET latitude = -2.3291805, longitude = -79.4009307 WHERE title = 'Loft en bord de Mer';
.print '# Update location of a place (reading after the update) #'
SELECT title, latitude, longitude
FROM places
WHERE title = 'Loft en bord de Mer';

-- ### Delete places ###
.print '# Delete a place (reading before the deletion) #'
SELECT title FROM places;
DELETE FROM places WHERE title = 'Maison de Campagne';
.print '# Delete a place (reading after the deletion) #'
SELECT title FROM places;


.print ' -- ########## AMENITIES ########## -- '

-- ### Create amenities ###
INSERT OR IGNORE INTO amenities(id, created_at, updated_at, name)
VALUES 
('0d1ac10f-555d-4198-a2c8-10b8316b51cf', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Parking'),
('cced556f-222c-45e1-a1f9-0c509d2e7550', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Pool'),
('a84ecfd3-2039-437d-8962-9f746e12a474', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'TV'),
('28eb152c-8b71-4f30-b332-1341a76845b1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Barbecue'),
('55368917-c233-42bd-b2ed-9f3fb0bf0b89', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Ping pong table');


-- ### Read amenities ###
.print '# Read all the amenities #'
SELECT name FROM amenities;

.print '# Read all the amenities beginning with P #'
SELECT name FROM amenities WHERE name LIKE 'P%';

-- ### Update amenities ###
.print '# Update an amenity (reading before the update) #'
SELECT name
FROM amenities
WHERE id = '0d1ac10f-555d-4198-a2c8-10b8316b51cf';
UPDATE amenities
SET name = 'Parking lot'
WHERE id = '0d1ac10f-555d-4198-a2c8-10b8316b51cf';
.print '# Update an amenity (reading after the update) #'
SELECT name
FROM amenities
WHERE id = '0d1ac10f-555d-4198-a2c8-10b8316b51cf';

.print '# Update another amenity (reading before the update) #'
SELECT name
FROM amenities
WHERE name = 'Barbecue';
UPDATE amenities SET name = 'BBQ' WHERE name = 'Barbecue';
.print '# Update another amenity (reading after the update) #'
SELECT name
FROM amenities
WHERE name = 'BBQ';;


-- ### Delete amenities ###
.print '# Delete an amenity (reading before the deletion) #'
SELECT name FROM amenities;
DELETE FROM amenities WHERE name = 'Ping pong table';
.print '# Delete an amenity (reading after the deletion) #'
SELECT name FROM amenities;


.print ' -- ########## REVIEWS ########## -- '

-- ### Create reviews ###
INSERT OR IGNORE INTO reviews (id, created_at, updated_at, text, rating, user_id, place_id)
VALUES (
	'2523b067-d964-42fd-b2a6-09738da46130',
	CURRENT_TIMESTAMP, 
	CURRENT_TIMESTAMP,
	"On est allé à Perdu mais on n'a rien trouvé",
	3,
	'0c095bc9-8ac4-4d50-b16b-e3da1e8ea3fb',
	'2e039425-2acd-4b87-94de-3336ee838e7e'
);

INSERT OR IGNORE INTO reviews (id, created_at, updated_at, text, rating, user_id, place_id)
VALUES (
	'bf1763f8-2696-4b1a-903b-0c55481eb903',
	CURRENT_TIMESTAMP,
	CURRENT_TIMESTAMP,
	"On est allé au fond mais on n'a rien trouvé. La prochaine fois, on ira à Perdu",
	3,
	'e4f87197-440f-47ae-8a27-1e1f23184be0',
	'13840f3f-2cbc-4aeb-97a4-2930da5a3465'
);

INSERT OR IGNORE INTO reviews (id, created_at, updated_at, text, rating, user_id, place_id)
VALUES (
	'b3e140a7-10aa-46ee-8b66-c3e0ca228f00',
	CURRENT_TIMESTAMP,
	CURRENT_TIMESTAMP,
	"Campagne était bien mais il manque l'avantage de Ville",
	4,
	'0c095bc9-8ac4-4d50-b16b-e3da1e8ea3fb',
	'1992dcc6-c608-4874-ac01-76d8c58bbd64'
);


-- ### Read reviews ###
.print '# Read all the reviews #'
SELECT text FROM reviews;

.print '# Read reviews containing Perdu #'
SELECT text FROM reviews WHERE text LIKE '%Perdu%';

-- ### Update reviews ###
.print '# Update the rating of a review (reading before the update) #'
SELECT rating
FROM reviews
WHERE id ='2523b067-d964-42fd-b2a6-09738da46130';
UPDATE reviews
SET rating = 2
WHERE id = '2523b067-d964-42fd-b2a6-09738da46130';
.print '# Update the rating of a review (reading after the update) #'
SELECT rating
FROM reviews
WHERE id = '2523b067-d964-42fd-b2a6-09738da46130';

-- ### Delete reviews ###
.print '# Delete a review (reading before the deletion) #'
SELECT text FROM reviews;
DELETE FROM reviews WHERE place_id = '13840f3f-2cbc-4aeb-97a4-2930da5a3465';
.print '# Delete a review (reading after the deletion) #'
SELECT text FROM reviews;


.print ' -- ########## PLACE_AMENITY ########## -- '

-- ### Create ###
INSERT OR IGNORE INTO place_amenity (place_id, amenity_id)
VALUES ('13840f3f-2cbc-4aeb-97a4-2930da5a3465', 'cced556f-222c-45e1-a1f9-0c509d2e7550');

INSERT OR IGNORE INTO place_amenity (place_id, amenity_id)
VALUES ('13840f3f-2cbc-4aeb-97a4-2930da5a3465', '0d1ac10f-555d-4198-a2c8-10b8316b51cf');

INSERT OR IGNORE INTO place_amenity (place_id, amenity_id)
VALUES ('1992dcc6-c608-4874-ac01-76d8c58bbd64', '0d1ac10f-555d-4198-a2c8-10b8316b51cf');

INSERT OR IGNORE INTO place_amenity (place_id, amenity_id)
VALUES ('2e039425-2acd-4b87-94de-3336ee838e7e', '0d1ac10f-555d-4198-a2c8-10b8316b51cf');


-- ### Read ###
.print '# Read all the place/amenity relationships #'
SELECT places.title, GROUP_CONCAT(amenities.name, ', ')
FROM places
JOIN place_amenity ON places.id = place_amenity.place_id
JOIN amenities ON place_amenity.amenity_id = amenities.id
GROUP BY places.id, places.title
ORDER BY places.title;

-- Retrieve all amenities in a place
.print '# Read all amenities for "Loft en bord de Mer" #'
SELECT places.title, GROUP_CONCAT(amenities.name, ', ')
FROM places
JOIN place_amenity ON places.id = place_amenity.place_id
JOIN amenities ON place_amenity.amenity_id = amenities.id
WHERE places.title = 'Loft en bord de Mer'
GROUP BY places.id, places.title
ORDER BY places.title;

-- Retrieve all places with Parking amenity
.print '# Read all the places with the amenity Parking #'
SELECT places.title
FROM places
JOIN place_amenity ON places.id = place_amenity.place_id
JOIN amenities ON place_amenity.amenity_id = amenities.id
WHERE amenities.name = 'Parking'
ORDER BY places.title;

-- ### Update ###

-- To update the table place_amenity, we have to do a delete request to erase the relation
-- between the actual place and amenity.(DELETE)
-- And then recreate a new relation between this same place and a new amenity (INSERT INTO)
.print '# Relationship for "Loft en bord de Mer" before the update #'
SELECT amenities.name
FROM places
JOIN place_amenity ON places.id = place_amenity.place_id
JOIN amenities ON place_amenity.amenity_id = amenities.id
WHERE places.title = 'Loft en bord de Mer';
DELETE FROM place_amenity
WHERE place_id = '13840f3f-2cbc-4aeb-97a4-2930da5a3465' AND amenity_id = 'cced556f-222c-45e1-a1f9-0c509d2e7550';
INSERT INTO place_amenity (place_id, amenity_id)
VALUES ('13840f3f-2cbc-4aeb-97a4-2930da5a3465', 'a84ecfd3-2039-437d-8962-9f746e12a474');
.print '# Relationship for "Loft en bord de mer" after the update #'
SELECT amenities.name
FROM places
JOIN place_amenity ON places.id = place_amenity.place_id
JOIN amenities ON place_amenity.amenity_id = amenities.id
WHERE places.title = 'Loft en bord de Mer';

-- ### Delete ###
.print '## Delete a specific relationship ##'
.print '# Relationship before the deletion #'
SELECT places.title, GROUP_CONCAT(amenities.name, ', ')
FROM places
JOIN place_amenity ON places.id = place_amenity.place_id
JOIN amenities ON place_amenity.amenity_id = amenities.id
GROUP BY places.id, places.title
ORDER BY places.title;
DELETE FROM place_amenity
WHERE place_id = '13840f3f-2cbc-4aeb-97a4-2930da5a3465' AND amenity_id = '0d1ac10f-555d-4198-a2c8-10b8316b51cf';
.print '# Relationship after the deletion #'
SELECT places.title, GROUP_CONCAT(amenities.name, ', ')
FROM places
JOIN place_amenity ON places.id = place_amenity.place_id
JOIN amenities ON place_amenity.amenity_id = amenities.id
GROUP BY places.id, places.title
ORDER BY places.title;

-- Delete all amenities from a place
.print '## Deletion of all the amenities of a place ##'
.print '# Relationship before deletion #'
SELECT places.title, GROUP_CONCAT(amenities.name, ', ')
FROM places
LEFT JOIN place_amenity ON places.id = place_amenity.place_id
LEFT JOIN amenities ON place_amenity.amenity_id = amenities.id
WHERE places.title = 'Appartement Perdu'
GROUP BY places.id, places.title;
DELETE FROM place_amenity
WHERE place_id = '2e039425-2acd-4b87-94de-3336ee838e7e';
.print '# Relationship after the deletion #'
SELECT places.title, GROUP_CONCAT(amenities.name, ', ')
FROM places
LEFT JOIN place_amenity ON places.id = place_amenity.place_id
LEFT JOIN amenities ON place_amenity.amenity_id = amenities.id
WHERE places.title = 'Appartement Perdu'
GROUP BY places.id, places.title;
