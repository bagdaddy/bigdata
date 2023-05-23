docker-compose exec mongors1n1 sh -c "mongosh < /scripts/shard1.js"
docker-compose exec mongors2n1 sh -c "mongosh < /scripts/shard2.js"
docker-compose exec mongors3n1 sh -c "mongosh < /scripts/shard3.js"