metricrelay
===========

Python implementation of the statsd server by Etsy.

Installing dependencies
-----------------------
```shell
$ ./init.sh
```

Configuring the backends
------------------------
Create core/settings.py with contents similar to the following:
```python
backends = (
    #'backends.stdout',
    'backends.http',
)

http_servers = (
    'http://m1.example.com/publish',
    'http://m2.example.com/publish',
    'http://m3.example.com/publish',
)
```

Running the server
------------------
```shell
$ . bin/activate
$ python app.py
```
