# Sets up services required for running Dockerized PsyNet commands

# Ensures that the script stops on errors
set -euo pipefail


echo "Confirming that the Dallinger network exists..."
if [[ "$(docker network ls | grep dallinger)" = "" ]]
then
  echo "...no. Creating now..."
  docker network create dallinger
else
  echo "...yes."
fi

echo "Confirming that dallinger_redis is running..."
if [[ "$(docker ps | grep dallinger_redis)" = "" ]]
then
  echo "...no. Creating now..."
  docker run -d --name dallinger_redis --network=dallinger \
    -v dallinger_redis:/data \
    redis redis-server \
    --appendonly yes
else
  echo "...yes."
fi

echo "Confirming that dallinger_postgres is running..."
if [[ "$(docker ps | grep dallinger_postgres)" = "" ]]
then
  echo "...no. Creating now..."
  docker run -d --name dallinger_postgres --network=dallinger \
  -e POSTGRES_USER=dallinger \
  -e POSTGRES_PASSWORD=dallinger \
  -e POSTGRES_DB=dallinger \
  -v dallinger_postgres:/var/lib/postgresql/data \
  postgres:12
else
  echo "...yes."
fi
