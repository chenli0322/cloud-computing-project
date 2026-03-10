#!/bin/bash
# Setup script: copies required packages from installer directory to Docker build context
# Run this script from the docker/ directory before building

set -e

INSTALLER_DIR="${1:-F:/Cloud Progress/JDK1-7-0-80}"
ARCHNAV_DIR="${2:-F:/Cloud Progress/ArchNav-extracted/itp}"
PACKAGES_DIR="./packages"

echo "Creating packages directory..."
mkdir -p "$PACKAGES_DIR"

echo "Copying JDK 7..."
cp "$INSTALLER_DIR/jdk-7u80-linux-x64.zip" "$PACKAGES_DIR/"

echo "Copying ADF Essentials..."
cp "$INSTALLER_DIR/adf-essentials.zip" "$PACKAGES_DIR/"

echo "Copying adfutils.jar..."
cp "$ARCHNAV_DIR/App/adfutils.jar" "$PACKAGES_DIR/"

echo "Copying MySQL connector..."
cp "$INSTALLER_DIR/mysql-connector-java-5.1.40-bin.jar" "$PACKAGES_DIR/"

echo "Copying JSTL jar..."
cp "$INSTALLER_DIR/glassfish.jstl_1.2.0.1.jar" "$PACKAGES_DIR/"

echo "Copying archemy-security jar..."
cp "$ARCHNAV_DIR/App/archemy-security-1.0-SNAPSHOT-jar-with-dependencies.jar" "$PACKAGES_DIR/"

echo "Copying ArchNav EAR..."
cp "$ARCHNAV_DIR/App/deploy/archemy.ear" "$PACKAGES_DIR/"

echo ""
echo "All packages copied to $PACKAGES_DIR/"
echo "You can now run: docker-compose up --build -d"
