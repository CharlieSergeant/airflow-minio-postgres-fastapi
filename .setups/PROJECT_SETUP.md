# Project Setup

1. Copy the `.sample-env` file to `.env` and set the appropriate values for all environment variables used in the stack.

2. Configure the docker network and volumes:
   1. Run ```chmod +x ./.setups/project_init.sh```
   2. Run ```./.setups/project_init.sh```

3. Select the appropriate Docker Compose file based on your deployment environment:

   - For local development (localhost), use `local.docker-compose.yml`:

     ```bash
     docker compose -f local.docker-compose.yml up -d
     ```
   - For dev deployment with SSL/TLS configured, use `dev.docker-compose.yml`:

     ```bash
     docker compose -f dev.docker-compose.yml up -d
     ```
   - For production deployment with SSL/TLS configured, use `prod.docker-compose.yml`:

     ```bash
     docker compose -f prod.docker-compose.yml up -d
     ```
4. Configure Minio
   1. Create a new user from the minio console ```s3console.HOSTNAME``` (```MINIO_SUPERUSER_USERNAME```, ```MINIO_SUPERUSER_PASSWORD```)
   2. Create a new group called admins and add that super user to the group
   3. Create a new service account for that super user (```MINIO_ACCESS_KEY```, ```MINIO_SECRET_KEY```)
   4. Lake setup. Create buckets (datalake-raw, datalake-stage, datalake-processed, datalake-artifacts, datalake-output)

5. Access the services:
   - Traefik Dashboard: ```https://admin.HOSTNAME``` (Login using the credentials set in `TRAEFIK_ADMIN`)
   - API Service: ```https://fastapi.HOSTNAME``` (API service with FastAPI)
   - MinIO Console: ```https://s3console.HOSTNAME``` (MinIO web-based console)
   - PostgreSQL: Connect to `DB_HOSTNAME` on port `5432` with the credentials set in `.env`
   - Airflow Web Server: ```https://scheduler.HOSTNAME``` (Apache Airflow Web Server) (Login using `POSTGRES_USERNAME`:`POSTGRES_PASSWORD`)

6. Manage your data in the project using the API service, MinIO, PostgreSQL, and Apache Airflow for workflow tasks.



