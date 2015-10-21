
The `armada-bind` service can be used to connect armada services with non-armada ones.

It can work in two directions:

1. Bind specific armada service to chosen port on the machine where the legacy (non-armada) code is running.
2. Register legacy service running at specific address(es) in armada catalog,
so that armada services can discover it in armada way.


## Case 1. Bind specific armada service to chosen port.

The intended usage is for legacy code that doesn't have native access to armada tools,
but want to connect to armada services in reliable way.

Let's suppose we have a service called `ab-tests-backend` that is run in armada cluster.
Now we want to reliably connect to it from our old web code that is not yet armada-aware.
There are already some ways to do it:

* Use `magellan` + `main-haproxy` to make `ab-tests-backend` service available at some
dns address like `ab-tests-backend.initech.com`.
The downside here is that sometimes we may not be able to point such domain at armada ships.
E.g. when our armada cluster is behind ELB in AWS EC2 classic which doesn't support local IPs.

* Connect to one of armada ships and use armada `/list` API (available on port 8900)
to find `ab-tests-backend` service address.
The downside here is that we have to know one of the ship's address in advance.
This solution is also not good for cases where we connect to some service on every request.
The cost of querying for its address can add up quickly.

`armada-bind` introduces yet another method:

* Install armada on the web machine, connect it to your main armada cluster and run `armada-bind` locally:

        armada run armada-bind -e SERVICE_NAME=ab-tests-backend -p 3000:80

This will bind service `ab-tests-backend` running on armada to the address `localhost:3000`.
Moreover by connecting to this address you get loadbalancing "for free" if there are multiple instances
of the service running. It can be especially useful for stateless PHP code that establishes connection
to some distributed service at every request.

#### Choosing specific armada service to bind.

Additional parameters can be specified with `-e`:

* __SERVICE_ENV__ - Bind service run with specific `--env`.
It defaults to the value of `MICROSERVICE_ENV` used by `armada-bind`.

* __SERVICE_APP_ID__ - Bind service run with specific `--app_id`.
It defaults to the value of `MICROSERVICE_APP_ID` used by `armada-bind`.

E.g.:

    armada run armada-bind -e SERVICE_NAME=badguys -e SERVICE_ENV=dev -e SERVICE_APP_ID=slots -p 3000:80


## Case 2. Register legacy (non-armada) service running at specific address in armada catalog.

On the other hand the need may arise to access some non-armada services using traditional armada way.
E.g. we may want to connect to the service by a URL configured with `magellan` + `main-haproxy` duo.
The other use case may be accessing some external MySQL database just like any other service - by using only
its well-known name like `mysql-games-slave`.

To do it we can run:

    armada run armada-bind --rename mysql-games-slave -e SERVICE_ADDRESS=10.10.10.11:3306,mysql.initech.com:3306

`--rename` or `-r` parameter is used to give the service some meaningful name instead of just `armada-bind`.
Now we can connect to `mysql-games-slave` from within our armada services. The easy way would be to
use local_magellan, by putting lines like these below in the supervisor configuration:

    [program:require_mysql_games_slave]
    directory=/opt/microservice/src/local_magellan
    command=python require_service.py 3001 mysql-games-slave

That way, we can connect to our MySQL by using address `localhost:3001`.
What's more, every new connection to it is established in a load-balanced manner between the 2 supplied addresses.
We can easily add and/or remove MySQL slave instances just by restarting `mysql-games-slave` with another `SERVICE_ADDRESS` variable.

We've used external MySQL database as an example, but the same reasoning applies to other
not-yet-armadized services.

Using `armada-bind` like this can also provide more visibility to the legacy services and let them
act as proper armada-citizens without changing their code.


## Health check for HTTP services.

In case the service pointed by armada-bind is HTTP server, you may want to reflect the status of that server in the
status of `armada-bind` service.

To do that, add `-e HTTP_CHECK` to `armada run` arguments.

It will set `armada-bind`'s status as `passing` as long as the pointed service returns HTTP response, and `crticial`
otherwise.


# Installing as a service on Amazon Linux.

    sudo cp ./init.d/armada-bind /etc/init.d/armada-bind
    sudo chmod +x /etc/init.d/armada-bind
    sudo vim /etc/init.d/armada-bind
    # Add/remove services as shown under start) section:
    #     armada run armada-bind...
    sudo chkconfig --level 2345 armada-bind on
