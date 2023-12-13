Steps to reproduce:

* Install poetry as required
* Configure venv:

      poetry install

* Run mariadb in a new shell

      docker run --rm --env MARIADB_ROOT_PASSWORD=root -p3306:3306 mariadb

* Connect to containerised DB server (keep this open):
   
      mysql -uroot -proot -h 127.0.0.1

* Create project database:

      mysql> create database django_asgi;

* Set up DB:

      poetry run python manage.py migrate

* Run web server with uvicorn

      poetry run uvicorn --reload --port 8000 django_asgi.asgi:application

* Hammer the server with a decent number of request (ZSH script:)

      for i in {0..100}; do curl "http://localhost:8000" & ; done

* In the mysql terminal, run `show processlist` - note that even after
  the requests have completed, connections hang around. The exact number
  of connections seems non-deterministic, but re-running the 
  load script will generally add stale connections here (they never die).

        mysql> show processlist;
        +------+------+------------------+-------------+---------+------+----------+------------------+----------+
        | Id   | User | Host             | db          | Command | Time | State    | Info             | Progress |
        +------+------+------------------+-------------+---------+------+----------+------------------+----------+
        |    3 | root | 172.17.0.1:37720 | NULL        | Query   |    0 | starting | show processlist |    0.000 |
        |  819 | root | 172.17.0.1:47148 | django_asgi | Sleep   |   82 |          | NULL             |    0.000 |
        |  825 | root | 172.17.0.1:47210 | django_asgi | Sleep   |   82 |          | NULL             |    0.000 |
        |  832 | root | 172.17.0.1:47280 | django_asgi | Sleep   |   82 |          | NULL             |    0.000 |
        |  935 | root | 172.17.0.1:38490 | django_asgi | Sleep   |    1 |          | NULL             |    0.000 |
        |  937 | root | 172.17.0.1:38502 | django_asgi | Sleep   |    1 |          | NULL             |    0.000 |
        |  950 | root | 172.17.0.1:38628 | django_asgi | Sleep   |    1 |          | NULL             |    0.000 |
        |  996 | root | 172.17.0.1:39132 | django_asgi | Sleep   |    1 |          | NULL             |    0.000 |
        | 1001 | root | 172.17.0.1:39174 | django_asgi | Sleep   |    1 |          | NULL             |    0.000 |
        +------+------+------------------+-------------+---------+------+----------+------------------+----------+

* This can be confirmed as a regression by downgrading to 4.2.8:

        poetry run pip install django==4.2.8

  (Restart the uvicorn server, and re-run the request load script, once
  the requests are complete, all the connections go away).


This does not seem to be affected by setting `'CONN_MAX_AGE': 0` in the
database settings.

