#!/bin/bash
set -e

GLASSFISH_HOME=/opt/glassfish3/glassfish
PWDFILE=/tmp/pwdfile
MARKER_FILE=/opt/.glassfish_configured

echo "AS_ADMIN_PASSWORD=${AS_ADMIN_PASSWORD:-Claude1960%}" > $PWDFILE

echo "Starting Glassfish domain..."
${GLASSFISH_HOME}/bin/asadmin start-domain domain1

# Configure JDBC and deploy app on first run
if [ ! -f "$MARKER_FILE" ]; then
    echo "First run: configuring JDBC connection pool and deploying ArchNav..."

    # Wait for MySQL to be available
    echo "Waiting for MySQL to be ready..."
    for i in $(seq 1 60); do
        if ${GLASSFISH_HOME}/bin/asadmin --user admin --passwordfile $PWDFILE ping-connection-pool MySQLConnPool 2>/dev/null; then
            break
        fi
        # Try creating the pool after a few seconds
        if [ $i -eq 5 ]; then
            # Create JDBC Connection Pool
            ${GLASSFISH_HOME}/bin/asadmin --user admin --passwordfile $PWDFILE \
                create-jdbc-connection-pool \
                --datasourceclassname com.mysql.jdbc.jdbc2.optional.MysqlXADataSource \
                --restype javax.sql.XADataSource \
                --property "portNumber=${MYSQL_PORT:-3306}:databaseName=${MYSQL_DATABASE:-archemy}:serverName=${MYSQL_HOST:-mysql}:user=${MYSQL_USER:-archemy}:password=${MYSQL_PASSWORD:-archemydb1960%}" \
                MySQLConnPool 2>/dev/null || true

            # Create JDBC Resource
            ${GLASSFISH_HOME}/bin/asadmin --user admin --passwordfile $PWDFILE \
                create-jdbc-resource \
                --connectionpoolid MySQLConnPool \
                jdbcMySQLDataSource 2>/dev/null || true
        fi
        sleep 3
    done

    # Deploy ArchNav application
    if [ -f /opt/archemy.ear ]; then
        echo "Deploying ArchNav application..."
        ${GLASSFISH_HOME}/bin/asadmin --user admin --passwordfile $PWDFILE \
            deploy --force=true --name archemy /opt/archemy.ear || true
    fi

    touch "$MARKER_FILE"
    echo "Glassfish configuration complete."
else
    echo "Glassfish already configured."
fi

echo "========================================"
echo "ArchNav is available at:"
echo "  http://localhost:9999/archemy/faces/login.jspx"
echo "Glassfish Admin Console:"
echo "  https://localhost:4848"
echo "========================================"

# Keep container running - tail Glassfish logs
tail -f ${GLASSFISH_HOME}/domains/domain1/logs/server.log
