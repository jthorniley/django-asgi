Steps to reproduce:

* Install poetry as required
* Configure venv:

      poetry install

* Run mariadb in a new shell

      docker run --rm --env MARIADB_ROOT_PASSWORD=root -p3306:3306 mariadb:11.2.2

* Connect to containerised DB server (keep this open):
   
      mysql -uroot -proot -h 127.0.0.1

* Create project database:

      mysql> create database django_asgi;

* Set up DB:

      poetry run python manage.py migrate

* Run web server with uvicorn

      poetry run uvicorn --port 8000 django_asgi.asgi:application

* Hammer the server with a decent number of request (ZSH script:)

      for j in {0..10}; do for i in {0..150}; do curl "http://localhost:8000" & ; done; sleep 1; done 

* A substantial number of the requests will return 500 due to a database
  "too many connections" error. Running show processlist in mysql will
  show that a number of stale connections have been left open even after
  the requests have finished processing:

      mysql> show processlist;
      +------+------+------------------+-------------+---------+------+----------+------------------+----------+
      | Id   | User | Host             | db          | Command | Time | State    | Info             | Progress |
      +------+------+------------------+-------------+---------+------+----------+------------------+----------+
      |    3 | root | 172.17.0.1:48698 | NULL        | Query   |    0 | starting | show processlist |    0.000 |
      | 5669 | root | 172.17.0.1:57664 | django_asgi | Sleep   |    7 |          | NULL             |    0.000 |
      | 5744 | root | 172.17.0.1:58308 | django_asgi | Sleep   |    6 |          | NULL             |    0.000 |
      | 5773 | root | 172.17.0.1:58588 | django_asgi | Sleep   |    6 |          | NULL             |    0.000 |
      | 5794 | root | 172.17.0.1:58790 | django_asgi | Sleep   |    6 |          | NULL             |    0.000 |
      | 5814 | root | 172.17.0.1:59002 | django_asgi | Sleep   |    7 |          | NULL             |    0.000 |
      | 5815 | root | 172.17.0.1:59010 | django_asgi | Sleep   |    7 |          | NULL             |    0.000 |
      | 5816 | root | 172.17.0.1:59024 | django_asgi | Sleep   |    7 |          | NULL             |    0.000 |
      | 5817 | root | 172.17.0.1:59034 | django_asgi | Sleep   |    7 |          | NULL             |    0.000 |
      | 5818 | root | 172.17.0.1:59046 | django_asgi | Sleep   |    7 |          | NULL             |    0.000 |
      +------+------+------------------+-------------+---------+------+----------+------------------+----------+

* This can be confirmed as a regression by downgrading to 4.2.8:

        poetry run pip install django==4.2.8

  - Then re-run the uvicorn server and the load script. There are no failures,
    and `show processlist` should not show any stale connections.


This does not seem to be affected by setting `'CONN_MAX_AGE': 0` in the
database settings.

