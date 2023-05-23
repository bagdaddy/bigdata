var config_replicaset_02 = {
    _id: "mongors2",
    version: 1,
    members:[
        { _id: 0, host : "mongors2n1:27017" },
        { _id: 1, host : "mongors2n2:27017" },
        { _id: 2, host : "mongors2n3:27017" }, 
    ]
};

var status_replicaset_02 = rs.initiate(config_replicaset_02);

printjson(status_replicaset_02);