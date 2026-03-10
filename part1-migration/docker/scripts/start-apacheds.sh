#!/bin/bash
set -e

FORTRESS_DIR="/opt/fortress-core-${FORTRESS_VERSION}"
MARKER_FILE="/var/lib/apacheds/.initialized"

echo "Starting ApacheDS..."

# Start ApacheDS in background
/opt/apacheds-${APACHEDS_VERSION}/bin/apacheds start default

# Wait for ApacheDS to be ready
echo "Waiting for ApacheDS to start on port 10389..."
for i in $(seq 1 60); do
    if ldapsearch -x -H ldap://localhost:10389 -D "uid=admin,ou=system" -w secret -b "ou=system" "(objectClass=*)" dn 2>/dev/null | grep -q "dn:"; then
        echo "ApacheDS is ready."
        break
    fi
    echo "  Attempt $i/60 - waiting..."
    sleep 3
done

# Import Fortress schema and data on first run
if [ ! -f "$MARKER_FILE" ]; then
    echo "First run: importing Fortress schema into ApacheDS..."

    cd "$FORTRESS_DIR"

    # Import the ApacheDS Fortress schema
    if [ -f "ldap/schema/apacheds-fortress.ldif" ]; then
        echo "Importing Fortress LDIF schema..."
        ldapmodify -x -H ldap://localhost:10389 -D "uid=admin,ou=system" -w secret -a -f ldap/schema/apacheds-fortress.ldif 2>/dev/null || true
    fi

    # Load Fortress LDAP data using Maven
    echo "Loading Fortress LDAP data..."
    mvn install -DskipTests -Dload.file=./ldap/setup/refreshLDAPData.xml -q 2>/dev/null || true

    # Load delegated admin data
    echo "Loading Delegated Admin data..."
    mvn install -DskipTests -Dload.file=./ldap/setup/DelegatedAdminManagerLoad.xml -q 2>/dev/null || true

    touch "$MARKER_FILE"
    echo "Fortress schema and data import complete."
else
    echo "ApacheDS already initialized, skipping import."
fi

# Set up port forwarding from 389 to 10389 (ApacheDS default)
echo "Setting up port forwarding 389 -> 10389..."
apt-get update -qq && apt-get install -y -qq socat > /dev/null 2>&1 || true
socat TCP-LISTEN:389,fork TCP:localhost:10389 &

echo "ApacheDS is running. LDAP available on ports 389 and 10389."

# Keep container running, follow ApacheDS logs
tail -f /var/lib/apacheds-${APACHEDS_VERSION}/default/log/*.log 2>/dev/null || tail -f /dev/null
