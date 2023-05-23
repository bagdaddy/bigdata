var config_replicaset_01 = {
    _id: "mongors1",
    version: 1,
    members:[
        { _id: 0, host : "mongors1n1:27017" },
        { _id: 1, host : "mongors1n2:27017" },
        { _id: 2, host : "mongors1n3:27017" }, 
    ]
};

var status_replicaset_01 = rs.initiate(config_replicaset_01);

printjson(status_replicaset_01);