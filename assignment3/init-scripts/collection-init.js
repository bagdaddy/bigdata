db.createCollection('ship_positions_2')
sh.enableSharding('ships')
sh.shardCollection('ships.ship_positions_2', {'mmsi': 'hashed'});

db.createCollection('filtered_positions_2')
sh.enableSharding('ships')
sh.shardCollection('ships.filtered_positions_2', {'mmsi': 'hashed'});

db.filtered_positions_2.createIndex({'id': 1}, {'name': 'id', 'unique': true});
db.filtered_positions_2.createIndex({'timestamp': 1}, {'name': 'timestamp', 'unique': false});

db.getMongo().setReadPref("primaryPreferred")
db.adminCommand({setDefaultRWConcern: 1, defaultReadConcern: {level: "available"}, defaultWriteConcern: {w: 1}})