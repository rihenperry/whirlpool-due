install:
	docker-compose -f docker-compose.build.yml run --rm install

quick-up:
	docker-compose -f docker-compose.build.yml run --rm quick-up

dev-build:
	docker build --no-cache -t whirlpool-due-dev:latest --target whirlpool-due-dev .

prod-build:
	docker build --no-cache -t whirlpool-due-prod:latest --target whirlpool-due-prod .

dev-up:
	docker-compose -f dev-docker-compose.yml up --build -d

prod-up:
	docker-compose -f prod-docker-compose.yml up --build -d

dev-logs:
	docker-compose -f dev-docker-compose.yml logs -f

prod-logs:
	docker-compose -f prod-docker-compose.yml logs -f

push-dev:
	docker push rihbyne/whirlpool-due-dev:latest

push-prod:
	docker push rihbyne/whirlpool-due-prod:latest

tag-dev:
	docker tag whirlpool-due-dev:latest rihbyne/whirlpool-due-dev:latest

tag-prod:
	docker tag whirlpool-due-prod:latest rihbyne/whirlpool-due-prod:latest
