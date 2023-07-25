# Docker Compose Stack for chs-datastore

This Docker Compose stack sets up a complete data storage solution for the **chs-datastore** project. It includes Traefik as a reverse proxy for handling HTTPS connections and SSL certificates, PostgreSQL as the relational database, MinIO as the blob storage server, a FastAPI-based API service, and Apache Airflow for workflow orchestration. Data will be stored in MinIO and accessed through the API service or passed to PostgreSQL for further analysis. Apache Airflow will handle task scheduling and workflow management.

## Prerequisites

- Docker and Docker Compose are installed on the host machine.

## Usage

Checkout ```./setups/PROJECT_SETUP.md``` and ```./setups/SERVER_SETUP.md``` 

## Services

### Traefik

- Acts as a reverse proxy to handle HTTPS connections and SSL certificates.
- Provides a web dashboard for managing the services at ```https://admin.HOSTNAME```.
- Automatically fetches and renews SSL certificates using Let's Encrypt.

### PostgreSQL

- The PostgreSQL database service for storing relational data.
- Data is persisted in the `./postgres-data` directory on the host machine.

### MinIO

- The MinIO blob storage service for storing unstructured data.
- The web-based console is available at ```https://s3console.HOSTNAME```.
- Data is persisted in the `./file-storage` directory on the host machine.

### API

- A FastAPI-based API service for interacting with the data stored in MinIO and Postgres.
- Public and Private routing via API_KEY header
- ```https://fastapi.HOSTNAME```

### Apache Airflow

- Apache Airflow for workflow orchestration and task scheduling.
- Provides a web interface for managing and monitoring workflows.
- Custom DAGs can be added in the `./airflow_data/dags` directory.

## Volumes

- `file-storage`: The volume to store MinIO data.
- `postgres-data`: The volume to store PostgreSQL data.
- `traefik-public-certificates`: The volume to store Traefik SSL certificates.
- `downloads`: The volume for Apache Airflow downloads (e.g., Selenium drivers).

## Networks

- `STACK_NETWORK_NAME`: The network shared by all services that need to be publicly available via Traefik.

## Notes

- Ensure that your DNS records point to your server's IP address to access the services via the defined domain names. To set up on a local server:
  - Setup port forwarding for ports 22, 80, 443, and 5432
  - Check out [DuckDNS](https://www.duckdns.org/) for free DNS.

- The `.env` file should be kept private and never committed to version control, as it contains sensitive information.

- Extend the functionality of the stack by building upon the FastAPI-based API service, Apache Airflow for more complex workflows, and implementing data pipeline executions.

## Resources

- [FastAPI-Traefik-Postgres](https://github.com/tiangolo/full-stack-fastapi-postgresql)
- [FastAPI-Traefik](https://github.com/tiangolo/blog-posts/tree/master/deploying-fastapi-apps-with-https-powered-by-traefik/app)
- [Minio-Traefik](https://community.traefik.io/t/minio-and-traefik/18570/7)
- [Postgres-SSL](https://github.com/infrastructure-as-code/docker-postgres)
- [Traefik](https://traefik.io/)
- [Apache Airflow](https://airflow.apache.org/)
- [Data Pipelines with Apache Airflow](https://github.com/BasPH/data-pipelines-with-apache-airflow/tree/master)
- [SSH Server](https://www.digitalocean.com/community/tutorials/ssh-essentials-working-with-ssh-servers-clients-and-keys)
- [GitHub Actions](https://docs.github.com/en/actions)