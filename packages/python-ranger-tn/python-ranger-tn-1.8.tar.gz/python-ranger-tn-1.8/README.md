# Python Ranger

[![PyPI version](https://img.shields.io/pypi/v/serviceprovider?style=for-the-badge)](https://pypi.org/project/serviceprovider)
[![Docker Image](https://img.shields.io/docker/v/tusharknaik/python-ranger-daemon?style=for-the-badge)](https://hub.docker.com/repository/docker/tusharknaik/python-ranger-daemon)

Before you start, you might wanna check [Ranger](https://github.com/appform-io/ranger) for more details. You'll need it
to follow some jargon being used in this readme.

There are 3 sections in here.

1. [Ranger Service Finder](#ranger-service-finder)
1. [Ranger Service Provider](#ranger-service-provider)
2. [Ranger Daemon](#ranger-daemon-setup)

## Ranger Service Finder

A service finder in Ranger is something can be used to discover individual host:port pairs of a distributed service which allows
clients to connect and request for services (make http calls). This finding is done using zookeeper. The following
python class helps you do the same for any python based service/tool. It follows the same data models as present in the
main ranger java library. (which is paramount for this to work across languages).
Similar details can be found at [PyPi](https://pypi.org/project/python-ranger-tn/)

### Installation

```shell
python3.9 -m pip install python-ranger-tn
```

### Usage

```python
from rangermodels.ranger_models import *
from servicefinder import RangerServiceFinder, RoundRobinNodeSelector

# Create the ranger service provider
ranger = RangerServiceFinder(cluster_details=ClusterDetails(zk_string='localhost:2181', update_interval_in_secs=1),
                             namespace="org",
                             services=["serviceA", "serviceB"],
                             selector=RoundRobinNodeSelector()) # optional

## Start the updates in background (this will update from zookeeper at regular intervals)
ranger.start()


node = ranger.get_node("serviceA")

nodes = ranger.get_all_nodes("serviceB")  ## to get the full list of healthy nodes

## When you wish to clean up
ranger.stop()
```

### Details

The above sample shows how to set up a background thread, that does the job of publishing regular updates to zk. You can
optionally provide a healthcheck url, which will receive a ping at regular intervals. A HEALTHY broadcast will only be
done if the ping check was successful. You can check HealthCheck to customize the URL to your needs.
The difference between the java implementation - the list of services being discovered needs to be

---

## Ranger Service Provider

A service provider in Ranger does the opposite. It can a way to broadcast that a service is available at some host:
port, where clients can connect and request services (make http calls). This broadcast is essentially done using
zookeeper. The following python class helps you do the same for any python based service/tool. Again, it follows the
same data models as present in the main ranger java library.

### Usage

```python
from rangermodels.ranger_models import *
from serviceprovider import RangerServiceProvider, HealthCheck

# Create the ranger service provider
ranger = RangerServiceProvider(cluster_details=ClusterDetails(zk_string='localhost:2181', update_interval_in_secs=1),
                               service_details=ServiceDetails(host='localhost', port=12211, environment='stage',
                                                              namespace='myorg',
                                                              service_name='python-test'),
                               health_check=HealthCheck(url='localhost:12211/health', scheme=UrlScheme.GET))

## Start the updates in background (this will update zookeeper at regular intervals)
ranger.start()

## You may also start the updates and block your current thread (until we hit an interrupt)
ranger.start(block=True)

## When you wish to stop updates
ranger.stop()
```

### Details

The above sample shows how to set up a background thread, that does the job of publishing regular updates to zk. You can
optionally provide a healthcheck url, which will receive a ping at regular intervals. A HEALTHY broadcast will only be
done if the ping check was successful. You can check HealthCheck to customize the URL to your needs.

---

## Ranger Daemon setup

This section deals with using the code as a simple light daemon that can run alongside your software (but outside it) to
provide regular service discovery updates to zookeeper. As usual, check [Ranger](https://github.com/appform-io/ranger)
for more details.

### Intent

Ideally, you would directly use the standard Ranger java client to deeply integrate the service's health updates with
ranger.<br>  
In scenarios where you can't do the above, you can rely on this daemon. Say you need discovery updates to be published
for a service written in a langauge other than java, or you are unable to add the ranger dependency directly, in your
java application.

The intent of this daemon is to run along-side your software and publish updates, as long as your software is up and
healthy. Currently, support has been added for a dockerized setup, as well as an import based custom setup. Currently,
Support has been provided for the following:

1. Simple usage
2. Import based usage
3. Docker multi-container setup

### 1. Simple usage

If you just wish to invoke the script directly, clone the project and follow along the helper. You command will look
like so

```shell
python3.9 serviceprovider/ranger_daemon.py -zk localhost:2181 -s myapp -host localhost -p 12211 -n org -e stage -hcu 'http://localhost:12211/healthcheck?pretty=true'
```

### 2. Import Based Usage

You can also choose to run the daemon from within another python file, by forwarding the command line arguments. Install
the package first, as shown below

```shell
python3.9 -m pip install serviceprovider
```

```python
import sys
from serviceprovider.ranger_daemon import ranger_daemon_trigger

ranger_daemon_trigger(sys.argv[1:])
```

### 3. Docker Based

Imagine a scenario where you already have a docker application, but you want to run this daemon alongside the container,
to make the existing container discoverable, without having to code up an integration with ranger. The following is a
solution to this problem. You can use docker compose to run your service and this daemon as a multi container docker
application.<br>
After this, your existing container should be ready for service discovery.

Docker containers are available on
the [DockerHub](https://hub.docker.com/repository/docker/tusharknaik/python-ranger-daemon).

The following docker command can be used to start the daemon, using environment variables. The table below explains the
various environment variables required to run the script

| Env Variable | Description                                         |
|--------------|-----------------------------------------------------|
| HOST         | Hostname                                            |
| PORT         | Port                                                |
| RANGER_ZK    | Zookeeper connection string                         |
| SERVICE_NAME | Name of service                                     |
| ENV          | Environment (stage/prod)                            |
| NAMESPACE    | Namespace in zookeeper                              |
| HEALTH_CHECK | [optional] GET healthcheck URL to be used for pings |
| REGION       | [optional] Region value                             |
| TAGS         | [optional] Comma separated tags                     |

```shell
docker run --rm -d -e RANGER_ZK=<zookeeper_info> -e SERVICE_NAME=<name_of_service> -e HOST=<host_of_machine> -e PORT=<port> -e ENV=<environment> -e NAMESPACE=<namespace> -e HEALTH_CHECK=<health_check_url> --name python-ranger-daemon tusharknaik/python-ranger-daemon:1.8
```

Here is an example for running it on a Mac machine, assuming your zookeeper is already running on `localhost:2181` (
notice the network being set to `host` and zookeeper being sent as `host.docker.internal` for connecting to localhost
from within docker)

```shell
docker run --rm -d --network host -e RANGER_ZK=host.docker.internal:2181 -e SERVICE_NAME=python-test -e HOST=localhost -e PORT=12211 -e ENV=stage -e NAMESPACE=myorg -e HEALTH_CHECK="localhost:12211/health" --name python-ranger-daemon tusharknaik/python-ranger-daemon:1.8
```

---

## Under the hood

The daemon/thread will write data to zookeeper in the following format (datamodel from ranger):

```json
{
  "host": "localhost",
  "port": 12211,
  "nodeData": {
    "environment": "stage",
    "tags": [
      "identity",
      "auth"
    ],
    "region": "IN-nm"
  },
  "healthcheckStatus": "healthy",
  "lastUpdatedTimeStamp": 1639044989841
}
```

Updates will be published in the path: /$NAMESPACE/$SERVICE_NAME at a periodic intervals of --interval (default: 1
second)

**The following will be taken care of:**

- Infinite retry and connection reattempts in case of zk connection issues
- Proper cleanup of zk connections to get rid of ephemeral nodes
- Proper logging
- Does continuous health check pings on a particular health check url if required [optional]
