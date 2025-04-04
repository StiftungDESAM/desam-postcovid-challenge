#!/bin/bash

# Waits until PostgreSQL has started.
until pg_isready -h "$SQL_HOST" -p "$SQL_PORT" -U "$SQL_USER"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "PostgreSQL has started."

# Waits until Neo4j has started.
until curl -s "http://neo4j:7474/browser/" | grep -q "Neo4j Browser"; do
    echo "Neo4j is unavailable - sleeping"
    sleep 2
done
echo "Neo4j has started."


echo "Applying relational database migrations..."
python manage.py migrate

echo "Applying graph database migrations..."
python manage.py migrate_graph_database

# Makes sure all constants like roles&scopes are created in the database.
python manage.py load_constants

echo "Collecting static files for Django..."
python manage.py collectstatic --no-input

# echo "Compiling translations file..."
# ./compilemessages.sh

if [ "$DJANGO_DEBUG_MODE" = True ]
then
    echo "Starting Django development server..."
    python manage.py runserver 0.0.0.0:8080
else
    echo "Starting gunicorn..."
    gunicorn config.wsgi -b 0.0.0.0:8080
fi
