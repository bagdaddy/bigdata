docker-compose exec mongos1 sh -c "mongosh < /scripts/router.js"
docker-compose exec mongos2 sh -c "mongosh < /scripts/router.js"