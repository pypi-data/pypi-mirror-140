# python-nosql-logger

## Installation steps if using MongoDB

```
  pip install pymongo #"pymongo[srv]" or "pymongo[aws]"
  pip install python-nosql-logger
```

### Initialize
#### For synchronous mongo logger
```
  from pynosql_logger.loggers import MongoLogger

  connection_string = 'your_mongodb_connection_string'
  logger = MongoLogger(connection_string)
```
#### For asynchronous mongo logger
```
  from pynosql_logger.async_loggers import AsyncMongoLogger
  
  connection_string = 'your_mongodb_connection_string'
  logger = AsyncMongoLogger(connection_string)
```

## Installation steps if using ElasticSearch

```
  pip install requests
  pip install python-nosql-logger
```

### Initialize
#### For synchronous elastic logger
```
  from pynosql_logger.loggers import ElasticLogger
  
  elastic_url = 'http://127.0.0.1:9200'
  logger = ElasticLogger(elastic_url)
```
#### For asynchronous elastic logger
```
  from pynosql_logger.async_loggers import AsyncElasticLogger
  
  elastic_url = 'http://127.0.0.1:9200'
  logger = AsyncElasticLogger(elastic_url)
```

### Add Log
```
  req_json = {
      'users': {
          'first_name': 'Hitesh',
          'last_name': 'Mishra',
          'email': 'hiteshmishra708@gmail.com'
      }
  }
  resp = logger.add_log(req_json)
```

### Add Bulk Log
```
  req_json = {
      'users': [{
          'first_name': 'Test',
          'last_name': 'User 1',
          'email': 'testuser1@mailnesia.com'
      }, {
          'first_name': 'Test',
          'last_name': 'User 2',
          'email': 'testuser2@mailnesia.com'
      }]
  }
  resp = logger.add_log(req_json)
```

### Get Log
You can pass mongo query or elastic query to get the logs
```
  req_json = {
      'users': {
        'first_name': 'Hitesh'
      }
  }
  resp = logger.get_log(req_json)
```

### Get All Logs
```
  req_json = {
      'collection': 'users'
  }
  resp = logger.get_all_logs(req_json)
```