### whirlpool-due

steps to build and push the service after pulling the repository.

`
docker build --no-cache -t whirlpool-due-dev:latest --target whirlpool-due-dev .
`

`
docker tag whirlpool-due-dev:latest rihbyne/whirlpool-due-dev:latest
`

`
docker push rihbyne/whirlpool-due-dev:latest
`

`
docker-compose -f dev-docker-compose.yml build --no-cache whirlpool-due
`

start the container with build flag in detach mode (will build all the images before starting)

`
docker-compose -f dev-docker-compose.yml up --build -d whirlpool-due
`

stop the container by removing non-running containers 
`
docker-compose -f dev-docker-compose.yml down --remove-orphans
`

Start with no dependencies
`docker-compose run --no-deps SERVICE COMMAND [ARGS...]`

test connection to postgres
`psql -h <host> -U <user> --dbname=<db>`
