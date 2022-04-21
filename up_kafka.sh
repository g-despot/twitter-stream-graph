echo Killing old Docker processes
docker-compose rm -fs

echo Starting Docker containers
docker-compose up -d kafka
docker-compose up -d memgraph-mage
sleep 1
docker-compose up -d stream
docker-compose up backend
docker-compose up frontend
