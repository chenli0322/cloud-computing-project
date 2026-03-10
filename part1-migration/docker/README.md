# ArchNav Docker Containerization

Containerized deployment of the ArchNav legacy Java application using Docker Compose.

## Architecture

| Service | Container | Port | Description |
|---------|-----------|------|-------------|
| MySQL 5.7 | archnav-mysql | 3306 | Relational database (archemy schema) |
| ApacheDS 2.0.0-M23 | archnav-apacheds | 389, 10389 | LDAP directory service |
| Tomcat 8.5 | archnav-tomcat | 8080 | Fortress REST + Fortress Web |
| Glassfish 3.1.2 | archnav-glassfish | 9999, 4848 | ArchNav ADF application |

## Prerequisites

- Docker & Docker Compose installed
- Place the following files in the `packages/` directory:

```
packages/
├── jdk-7u80-linux-x64.zip
├── adf-essentials.zip
├── adfutils.jar
├── mysql-connector-java-5.1.40-bin.jar
├── glassfish.jstl_1.2.0.1.jar
├── archemy-security-1.0-SNAPSHOT-jar-with-dependencies.jar
└── archemy.ear
```

## Setup

### 1. Prepare packages directory

```bash
# From the docker/ directory, run:
./setup-packages.sh
```

Or manually copy the required files (see setup-packages.sh for sources).

### 2. Build and start all services

```bash
docker-compose up --build -d
```

### 3. Check service status

```bash
docker-compose ps
docker-compose logs -f
```

### 4. Wait for initialization

On first run, ApacheDS needs time to import Fortress schema and LDAP data. Check progress:

```bash
docker-compose logs -f apacheds
```

## Access URLs

| Application | URL | Credentials |
|-------------|-----|-------------|
| ArchNav App | http://localhost:9999/archemy/faces/login.jspx | (create users via archemy-security jar) |
| Fortress Web | http://localhost:8080/fortress-web | test / password |
| Glassfish Admin | https://localhost:4848 | admin / Claude1960% |

## Creating ArchNav Users

After all services are running, create users via the archemy-security JAR:

```bash
# Enter the glassfish container
docker exec -it archnav-glassfish bash

# Create admin user
java -jar /opt/glassfish3/glassfish/domains/domain1/lib/archemy-security-1.0-SNAPSHOT-jar-with-dependencies.jar \
  -cuser -u tom@oracle.com -p oracle123 -r Admin -utype admin

# Create normal user
java -jar /opt/glassfish3/glassfish/domains/domain1/lib/archemy-security-1.0-SNAPSHOT-jar-with-dependencies.jar \
  -cuser -u john@oracle.com -p oracle123 -r NormalUser -utype normal
```

## Stopping Services

```bash
docker-compose down          # Stop and remove containers
docker-compose down -v       # Also remove volumes (data will be lost)
```

## Troubleshooting

- **MySQL not ready**: Check `docker-compose logs mysql` - initialization may take 30-60 seconds
- **LDAP connection issues**: Ensure ApacheDS is healthy before starting Tomcat/Glassfish
- **Glassfish deployment fails**: Check `docker-compose logs glassfish` for JDBC pool errors
- **Port conflicts**: Edit `.env` to change port mappings
