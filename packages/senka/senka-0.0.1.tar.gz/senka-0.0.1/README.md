# senka


## docker
### for start
$ docker-compose up -d

### for access to shell in the container
$ docker-compose exec senka bash

### for end
$ docker-compose down

### for remove
$ docker-compose down --rmi all --volumes --remove-orphans

## for test

```
$ pip install -e .[test]
$ pytest --cov=src --cov-branch --cov-report=term-missing -vv
```


## for adding plugin

```
$ cd /app/
$ pip install git+https://github.com/yuma300/pancake_plugin@bdf40a07705934e01231290e1405b3e6697b2e82 -t src/plugin/
```

change plugin repository url for what you want.

## for execution from CLI

```
$ cd /app/
$ python setup.py install
# python src/main chain_name address > result.csv

ex.
$ python src/main.py bsc 0x0000000000000000000000000000000000000 > result.csv
```

change chain or address whatever you want to check.