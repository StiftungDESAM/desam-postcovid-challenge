#!/bin/bash

counter=1
max_tries=12

until docker logs postcovid_neo4j --since 2m | grep -q "Bolt enabled"; do
    [[ counter -eq $max_tries ]] && echo "Neo4j isn't starting as expected..." && exit 1
    echo "Neo4j is unavailable - sleeping"
    sleep 5
    ((counter++))
done

echo "Neo4j has started!"
