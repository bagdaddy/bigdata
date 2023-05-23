## 1. Create database

`docker exec -it mongos1 bash -c "echo 'use ships' | mongosh"`

## 2. Create the collection and enable sharding:

`bash bash/init-collection.sh`

## 2. Enable sharding:

`docker exec -it mongos1 bash -c "echo 'sh.enableSharding(\"testDB\")' | mongosh"`

## 3. Create collection:

`docker exec -it mongors1n1 bash -c "echo 'db.createCollection(\"testDB.testCollection\")' | mongosh"`

### testField here is s()

`docker exec -it mongos1 bash -c "echo 'sh.shardCollection(\"testDB.testCollection\", {\"testField\" : \"hashed\"})' | mongosh "`
