#!/bin/bash
docker compose -f docker-compose.tests.yml up -d &> /dev/null

docker compose exec api pytest .

docker compose -f docker-compose.tests.yml down &> /dev/null