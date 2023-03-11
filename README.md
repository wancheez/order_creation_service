# Order creating service


The service is developed with Clean architecture. Which means, it based on the 3 layers: Representation, Business, Data.

The whole project aimed to keep loose coupling. All packages depend on abstractions (DI).

1. Presentation layer is currently represented by a fast-api interface, but it might be easily extended by other technologies, for instance, with cli. It may be achieved because no layers depend on the representation one. (entrypoints package)
2. Business (service) layer performs requested use-case - to create an order. It knows how to use models to achieve use case goal. (service_layer package)
3. Data layer. It implements models. Models do not depend on concrete implementation of ORM or DB. They're just python classes. In current project I use SQLAlchemy with imperative mapping.
To store the orders I use Postgres, which is also kept behind the abstraction. The database scheme is populated by alembic migrations.
Broker and API clients, as well as repository, implemented with port/adapters pattern, which means they might be easily replaced with other technologies, without changing any client code.

To populate all dependencies over the project I created a dependency injector module, that, being a singleton, provide necessary dependencies to layers. The injector is a place, where all concrete implementations are chosen.

Service configuration stored in conf/conf.py and conf/logging.yaml.

To endure RabbitMQ's downtime and flapping, the asynchronous publishing with retries has been implemented. After inserting an order to DB, I create a coroutine, which tries to send msg to broker.
User don't have to wait it finishing it, because it might take time. So he gets order_id as response and later may check the status of the order (statuses are not implemented for now).
If the broker is down, the service keep trying to reconnect to it for a couple af attempts.

Testing is based on fake adapters implementations.
Monitoring is supposed to work with prometheus (/metrics endpoint created). It's also useful to connect Sentry to logs.

To endure high-load, it is possible to populate current service and process the requests simultaneously.

To run:
docker compose build
docker compose up