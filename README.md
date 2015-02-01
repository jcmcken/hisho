
hisho config add cluster foo
hisho config add username foo
hisho config generate password

hisho service create hdfs
hisho service create

/dev/shm/.hisho.<ppid>, ~/.hisho.<ppid>


# Cluster

cluster_name
cluster_version
cluster_full_version

hisho cluster create (name) --version CDH5 (--full-version 5.3.0)

# Services

service_name
service_cluster_name

service_type -> capitilize (hdfs -> HDFS)

hisho service 

hisho service create <name> (--cluster cluster_name)

hisho service assign <fqdn> <service> <role>

hish service assign foo.example.com zookeeper

# Hosts

hisho host list
