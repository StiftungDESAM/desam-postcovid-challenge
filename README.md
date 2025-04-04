# Postcovid Challenge

This is the working project for the Postcovid Challenge Stage 3.

## Setup

Requirements: **[Docker](https://www.docker.com/get-started/)**, **[Docker Compose plugin](https://docs.docker.com/compose/)**

1. Create a copy of `template.env` and rename it to `.env`.
2. (Optional) Open the file and adjust the project settings.
3. Build the project:
    - Dev mode: `docker-compose -f docker-compose.dev.yml build`
    - Prod mode: `docker compose build`
4. Launch container:
    - Dev mode: `docker-compose -f docker-compose.dev.yml up`
    - Prod mode: `docker compose up`
5. (optional, only in Dev mode) Create test users:
    - `docker exec -it postcovid_backend python manage.py mock_users --verified`

## System architecture

The system uses a classical three-layer architecture consisting of a frontend layer, backend layer and database layer. The entrypoint into the system is nginx which routes incoming requests and serves files to the user.

### Frontend (Vue.js)

The `frontend` folder contains the Vue.js project. When the Docker project is built, the frontend is automatically built. The resulting static files are served by nginx. This means that no standalone webserver is required for the frontend.

### Backend (Django)

The `backend` folder contains a [Django](https://www.djangoproject.com/start/overview/) project. It defines an API that can be accessed from the webpages of the frontend. In addition, it contains the data model and mappers to access the database layer. All business logic is defined here, including but not limited to:

-   Creating or changing the ontology
-   Importing data into the knowledge graph
-   Processing data requests to the data model

### Database (Neo4j, PostgreSQL)

The core database of the data model is a [Neo4j graph database](https://neo4j.com/docs/getting-started/). It contains both the ontology and all the imported medical data. The Python module [neomodel](https://neomodel.readthedocs.io/en/latest/) is used to access the graph database. <br>
[PostgreSQL](https://www.postgresql.org/) is used as a secondary database for Django's base functionality, for example to store user credentials and permissions. The in-built ORM of Django is used to access this database.

## Development notes

After launching the project, you can open the website under the IP and port you've set in `.env`. By default, this is `172.12.0.1:8010`.

You can verify if everything is working correctly for each component by visiting the following URLs:

-   **Frontend (Production)**: <http://172.12.0.1:8010/page/> or <http://localhost:8010/page/>
-   **Frontend (Development)**: <http://172.12.0.1:5173/dev/> or <http://localhost:5173/dev/>
-   **Frontend (Documentation)**: <http://172.12.0.1:8010/frontend/docs/> or <http://localhost:8010/frontend/docs/>
-   **Backend**: <http://172.12.0.1:8010/ontology/hello-world/> or <http://localhost:8010/ontology/hello-world/>
-   **Backend (Documentation)**: <http://172.12.0.1:8010/api/docs> or <http://localhost:8010/api/docs>
-   **Backend connection to Neo4j**: <http://172.12.0.1:8010/ontology/test/> or <http://localhost:8010/ontology/test/>
    -   after opening it, check using the Neo4j browser if nodes have been created in the database.
-   **Neo4j Browser**: <http://172.12.0.1:7474/> or <http://localhost:7474/>

When you make changes to the Django project while everything is running, it automatically reloads. This is not yet the case for the frontend, so the project must be re-built to apply changes.

## MkDocs Documentation

How to use this documentation (<a>https://www.mkdocs.org/getting-started/</a>):

1. Install python (3.x) and pip

2. Install mkdocs

```pip
pip install mkdocs
```

3. Install dependencies of this project

```pip
pip install mkdocs-include-markdown-plugin
```

4. Serve the documentation (for development)

```mkdocs
mkdocs serve
```

5. Build the documentation (for production)

```mkdocs
mkdocs build
```
