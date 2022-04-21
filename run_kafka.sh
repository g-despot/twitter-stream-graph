echo Killing old Docker processes
docker-compose rm -fs

echo Building Docker images
docker-compose build kafka
docker-compose build memgraph-mage
docker-compose build stream
docker-compose build backend
docker-compose build frontend

echo Starting Docker containers
docker-compose up -d kafka
docker-compose up -d memgraph-mage
sleep 1
docker-compose up -d stream
docker-compose up backend
