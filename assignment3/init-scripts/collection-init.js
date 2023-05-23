db.createCollection('ship_positions')
sh.enableSharding('ships')
sh.shardCollection('ships.ship_positions', {'id': 'hashed'});

db.createCollection('filtered_positions')
sh.enableSharding('ships')
sh.shardCollection('ships.filtered_positions', {'id': 'hashed'});
db.filtered_positions.createIndex({'id': 1}, {'name': 'id', 'unique': true});
db.filtered_positions.createIndex({'timestamp': 1}, {'name': 'timestamp', 'unique': false});