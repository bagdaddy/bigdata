## Commands:

These commands are used to initialize the whole cluster

1. `docker-compose up -d` - create docker containers
2. `bash bash/init-config-server.sh` - initialize the configuration replicas
3. `bash bash/init-shards.sh` - introduce the shard replicas to each other and make up the shards
4. `bash bash/init-router.sh` - introduce the shards to the routers
5. `docker exec -it mongos1 bash -c "echo 'use ships' | mongosh"` - create the database
6. `bash bash/init-collection.sh` - create collections, enable sharding, select shard keys, set read preferences for better fault tolerance
