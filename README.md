# HBnB Evolution
This repository has as objective to recreate ann Airbnb-like application.

It will be composed of four parts:
- Technical documentation (UML)
- Business Logic and API
- Authentification and Database
- [current stage of development] Simple Web Client

## Technical documentation
This documentation will help understand the overall architecture, behavior and responsibilities of the system models, design of the business logic, and the interactions between the different application components.
This documentation will help understand the overall architecture, behavior and responsibilities of the system models, design of the business logic, and the interactions between the different application components.

The first part of this project is the production of selected UML diagrams and their explanatory notes, the included diagrams are:
- A high-Level package diagram showing a three-layer architecture and the communication between these layers via the facade pattern
- A class diagram showing the different relationships between the classes
- Some sequence diagrams (User Registration, Place Creation, Review Submission, Fetching a list of Places, User Login) for API calls showing the interaction between the layers and the flow of information.

## Implementation of Business Logic and API Endpoints
This phase of the HBnB project focuses on building the core functionality of the application using Python and Flask. We'll bring the documented architecture to life by implementing the Presentation and Business Logic layers, defining essential classes, methods, and API endpoints.

The goal is to create a functional and scalable foundation for the application. This involves:

- Business Logic Layer: Developing the core models and logic that drive the application's functionality. This includes defining relationships, handling data validation, and managing interactions between different components.
- Presentation Layer: Defining the services and API endpoints using Flask and Flask-RESTx. We'll structure the endpoints logically, ensuring clear paths and parameters for each operation.

## Authentication and Database Integration
This part of the HBnB project marks a significant step towards a robust and production-ready application. This phase is dedicated to securing the API through user authentication and authorization, and transitioning from in-memory storage to a persistent database solution.

Key Objectives:
- JWT-based Authentication: Implementing JSON Web Token (JWT) authentication using Flask-JWT-Extended to secure API endpoints, ensuring that only authenticated users can access protected resources and manage their sessions effectively.

- Role-Based Access Control (RBAC): Introducing granular authorization based on user roles (e.g., distinguishing between regular users and administrators) to restrict access to specific functionalities or data.

- Database Integration with SQLAlchemy: Replacing the temporary in-memory data storage with a persistent database.

- SQLite will be utilized for development environments, offering a lightweight and file-based solution.

- The application will be prepared for seamless configuration with MySQL for robust production deployments.

- Database Schema Design: Designing a comprehensive relational database schema using SQLAlchemy's ORM to accurately map existing entities (Users, Places, Reviews, Amenities) and define their relationships.

- Persistent CRUD Operations: Refactoring all Create, Read, Update, and Delete (CRUD) operations to interact directly with the database, ensuring data consistency, validation, and reliable storage.

This part of the project will significantly enhance the application's security, scalability, and data integrity, making it ready for real-world scenarios.

## Simple Web Client

This part focuses on the devlopment of the application's front-end
using HTML5, CSS3 and JavaScript ES6.
This phase is dedicated to the design and implementation of an
interactive user interface connecting with the back-end services
developed in previous parts of the project.

Key objectives:
- User-friendly interface: Develop a user-friendly interface following
  approppriate design specifications in concordance with the
  application functionalities.
- Client-side functionalities: Implement client-side functionality to interact with the back-end API.
- Efficient data handling: Ensure secure and efficient data handling using JavaScript.
- Modern dynamic we application: Apply modern web development practices to create a dynamic web application.

## Authors
- [Delphine Coutouly-Laborda](https://github.com/Delphes1980) (up to **Authentification and Database**)
- [Xavier Laforgue](https://github.com/XavierLaforgue)
