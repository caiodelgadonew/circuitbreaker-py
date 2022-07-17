# Circuit Breaker implementation in Python

Implementation of the CircuitBreaker Pattern in Python, popularized by Michael T. Nygard in his book [Release It!](https://www.amazon.com/gp/product/0978739213/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=0978739213&linkCode=as2&tag=martinfowlerc-20)

## Requisites

This app is intended to run at minimum Python version 3.6.
Extra requirements can be seen in [requirements.txt](requirements.txt) file.

## Application Customization

It is possible to customize the application to set custom values for the application by the environment variables.

Environment Variables usages as following:

|   ENV                  |  Default Value  | TYPE     |                        Description                                       |
|------------------------|-----------------|----------|--------------------------------------------------------------------------|
| `HTTP_CLIENT`          | `sqlite`        | `string` | Address to be tested by circuitbreaker. Format `<HOST>:<PORT>`             |
| `ERROR_THRESHOLD`      | `3`             | `int`    | Treshold in seconds of failed attempts to identify the circuit as opened | 
| `TIME_WINDOW`          | `10`            | `int`    | Time in seconds between remote calls                                     | 
| `ACCEPT_CLIENT_ERRORS` | `False`         | `bool`   | `True` to Accept 3XX and 4XX return codes, `False` to accept 3XX         |
| `LOG_LEVEL`            | `INFO`          | `string` | Verbosity of log. Values: `INFO`, `DEBUG`, `WARNING`, `ERROR`            |


## Application Deployment

### Local

To deploy it locally its suggested to set up a [venv](https://docs.python.org/3.9/library/venv.html).

Clone the repository:
```bash
$ git clone git@github.com:caiodelgadonew/circuitbreaker-py.git
``` 

Create a Virtual Environment and source it:
```bash
$ python3 -m venv circuitbreakerpy 
$ source circuitbreakerpy/bin/activate
``` 

After initializing your Virtual Environment install all dependencies
```bash
$ pip3 install -r app/requirements.txt
``` 

Execute the application 
```bash
$ HTTP_CLIENT=<HOST>:<PORT> python3 circuitbreaker.py
``` 

### Docker Container 

A [docker-compose](https://docs.docker.com/compose/install/) file is available which will run an nginx server and also the circuitbreaker application, in that way it is possible to simulate the http errors with it.

To run the application as a Docker Container you can use the provided [docker-compose.yml](docker-compose.yml)

> Be sure to have [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/) installed before proceeding

Clone the repository:
```bash
$ git clone git@github.com:caiodelgadonew/circuitbreaker-py.git
``` 

Run `docker-compose up` to create the environment:
```bash
$ docker-compose up
``` 
> You can add `-d` to the `docker-compose` command to start detached

Attach to the logs of the `circuitbreaker` container:
```bash
$ docker-compose logs -f circuitbreaker
```

#### Simulating OpenCircuitError with Docker

To simulate the `OpenCircuitError`, open a new terminal and stop the `nginx` container 

```bash
$ docker-compose stop nginx
``` 

The circuitbreaker will start to show the `CircuitOpenError`, the circuit will be opened until the `HTTP_CLIENT` is available again.

```log
circuitbreaker-py | 2022-07-17 09:33:23 INFO __main__:         Remote Call Succeded
circuitbreaker-py | 2022-07-17 09:33:30 ERRO __main__:         CircuitOpenError - Remote Call has failed for 1 consecutive times.
circuitbreaker-py | 2022-07-17 09:33:37 ERRO __main__:         CircuitOpenError - Remote Call has failed for 2 consecutive times.
circuitbreaker-py | 2022-07-17 09:33:44 ERRO __main__:         CircuitOpenError - Remote Call has failed for 3 consecutive times.
circuitbreaker-py | 2022-07-17 09:33:44 INFO __main__:         Circuit changed from closed to open
circuitbreaker-py | 2022-07-17 09:33:51 ERRO __main__:         CircuitOpenError - Remote Call has failed for 4 consecutive times.
circuitbreaker-py | 2022-07-17 09:33:58 ERRO __main__:         CircuitOpenError - Remote Call has failed for 5 consecutive times.
```

Now you can start again the nginx container
```bash
$ docker-compose start nginx
``` 

The circuitbreaker will start the recovering process, going from `open` to `half_open` state, and as soon as the `ERROR_THRESHOLD` is less than the success rate, it will change to `closed` state again.

```log
circuitbreaker-py | 2022-07-17 09:35:22 ERRO __main__:         CircuitOpenError - Remote Call has failed for 17 consecutive times.
circuitbreaker-py | 2022-07-17 09:35:26 INFO __main__:         Circuit changed from open to half_open
circuitbreaker-py | 2022-07-17 09:35:26 INFO __main__:         Remote Call has succeeded for 1 consecutive times.
circuitbreaker-py | 2022-07-17 09:35:28 INFO __main__:         Remote Call has succeeded for 2 consecutive times.
circuitbreaker-py | 2022-07-17 09:35:30 INFO __main__:         Remote Call has succeeded for 3 consecutive times.
circuitbreaker-py | 2022-07-17 09:35:32 INFO __main__:         Remote Call has succeeded for 4 consecutive times.
circuitbreaker-py | 2022-07-17 09:35:32 INFO __main__:         Circuit changed from half_open to closed
circuitbreaker-py | 2022-07-17 09:35:34 INFO __main__:         Remote Call Succeded
circuitbreaker-py | 2022-07-17 09:35:36 INFO __main__:         Remote Call Succeded
``` 
