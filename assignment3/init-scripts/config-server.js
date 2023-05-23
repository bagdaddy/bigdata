var config_server = {
    _id: "mongors1conf",
    configsvr: true,
    version: 1,
    members: [ 
        { _id: 0, host : 'mongocfg1:27017' },
        { _id: 1, host : 'mongocfg2:27017' },
        { _id: 2, host : 'mongocfg3:27017' }
    ]
};

var status_config_server = rs.initiate(config_server);

printjson(status_config_server);