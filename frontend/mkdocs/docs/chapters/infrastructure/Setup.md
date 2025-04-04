## Setup

Requirements: **[Docker](https://www.docker.com/get-started/)**, **[Docker Compose plugin](https://docs.docker.com/compose/)**

1. Clone the full git repository into a local directory.
2. Create a copy of `template.env` and rename it to `.env`.
3. (Optional) Open the file and adjust the project settings.
4. Build the project:
    - Dev mode: `docker-compose -f docker-compose.dev.yml build`
    - Prod mode: `docker compose build`
5. Launch container:
    - Dev mode: `docker-compose -f docker-compose.dev.yml up`
    - Prod mode: `docker compose up`
6. (optional, only in Dev mode) Create test users:
    - `docker exec -it postcovid_backend python manage.py mock_users --verified`