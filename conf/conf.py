SERVICES_ENDPOINTS = {
    "users": {
        "url": "http://user-service:8080/users/",
    },
    "products": {
        "url": "http://product-service:8080/products/",
    },
}

RABBIT_MQ = {
    "type": "rabbit_mq",
    "parameters": {
        "host": "rabbitmq",
        "login": "hellofresh",
        "password": "food",
        "exchange": "orders",
        "port": 5672,
    },
}

DATABASE = {
    "type": "postgres",
    "username": "postgres",
    "password": "postgres",
    "host": "database",
    "database": "postgres",
}
