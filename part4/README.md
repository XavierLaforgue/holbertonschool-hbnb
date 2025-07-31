# HBNB Project - Partie 4 : 

## Table of Contents
- [Introduction](#introduction)
- [Objectives](#objectives)
- [Features](#features)
- [Structure](#structure)
- [Authors](#authors)

### Introduction
This part focuses on the devlopment of the application's front-end using HTML5, CSS3 and JavaScript ES6. This phase is dedicated to the design and implementation of an interactive user interface connecting with the back-end services developed in previous parts of the project.

### Objectives
The main objectives of this last part of the project include:
- User-friendly interface: Develop a user-friendly interface following
  approppriate design specifications in concordance with the
  application functionalities.
- Client-side functionalities: Implement client-side functionality to
  interact with the back-end API.
- Efficient data handling: Ensure secure and efficient data handling
  using JavaScript.
- Modern dynamic we application: Apply modern web development practices to create a dynamic web application.

### Features
In addition to the functionalities from Part 3, this phase introduces:
- A home page where to examine all the places registered in the system.
- A filter to reduce the list in function of the price per night of the
  places.
- A Login button to be redirected to a login form.
- A cookie based authentiation system.
- A Place details page found via a view details button of which each place
  card disposes.
- A create review form to create reviews for places (as long as the user
  is logged-in and is not the owner of the place).
- A dynamic graphical interface offering all the previous functionalities.

### Structure
The project structure evolves to accommodate the new layers and functionalities:

```
hbnb/
├── app/
│   ├── __init__.py
│   ├── api/                            # Contains RESTful API definitions (Flask-RESTX)
│   │   ├── __init__.py
│   │   |__ v1/                         # API version 1
│   │       ├── __init__.py
│   │       ├── users.py
│   │       ├── places.py
│   │       ├── reviews.py
│   │       ├── amenities.py
|   |       |__ auth.py                 # New: Authentication endpoints (login)
|   |       |__ apiResources.py         # Containts functions to validate input datas
│   ├── models/                         # Defining object classes (User, Amenity, Place, Review)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── place.py
│   │   ├── review.py
│   │   ├── amenity.py
|   |   |__ baseEntity.py
│   ├── services/                       # Business logic layer / facade
│   │   ├── __init__.py
│   │   ├── facade.py
|   |   |__ AmenityService.py
|   |   |__ PlaceService.py
|   |   |__ ReviewService.py
|   |   |__ UserService.py
|   |── static/                         # Non-template files for web client
|   |   |── images/
|   |   |   |── icon.png
|   |   |   |__ logo.png
|   |   |── add_review.css
|   |   |── footer.css
|   |   |── header.css
|   |   |── home.css
|   |   |── login.css
|   |   |── place_details.css
|   |   |── script.js
|   |   |__ styles.css
|   |── templates/
|   |   |── add_review.html
|   |   |── base.html
|   |   |── footer.html
|   |   |── header.html
|   |   |── index.html
|   |   |── login.html
|   |   |── place.html
|   |   |__ styles.html
│   ├── persistence/                    # Persistence layer (InMemoryRepository)
│   |   ├── __init__.py
│   |   ├── repository.py               # Updated: interacts with DB instead of in-memory
|   |__ images
|   |   |__ ER Diagram.png              # Diagram illustrating the different relationships
|   |   |__ ER Diagram_extra.png        # Diagram illustrating the different relationships with an extra table
|   |__ tests                           # Folder for different tests
|       |__ scripts
|       |   |__ populate_data.sh
|       |   |__ tests_api.sh
|       |__testSQL
|       |   |__ test_sql_crud.sql       # Tests of CRUD operations
|       |__ test_amenity.py
|       |__ test_relationships.py
|       |__ test_reviews.py
|       |__ test_user.py
├── run.py                              # Flask application entry point
├── config.py
├── requirements.txt
|__ create_tables.sql                   # Create a DB with some elements
|__ README.md
```
### Authors
- [Xavier Laforgue](https://github.com/XavierLaforgue)
