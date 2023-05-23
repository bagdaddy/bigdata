## 1. Create database

`docker exec -it mongos1 bash -c "echo 'use ships' | mongosh"`

## 2. Create the collection and enable sharding:

`bash bash/init-collection.sh`
