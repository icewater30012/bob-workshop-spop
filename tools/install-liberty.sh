#!/bin/bash
# Created: 2026-11-17 00:24:26 +0800
################################################################################
# Standalone IBM WebSphere Liberty Installation and Setup Script
#
# Requirements:
# - Liberty Version: 26.0.0.11 (Jakarta EE 11)
# - Download URL: https://public.dhe.ibm.com/ibmdl/export/pub/software/websphere/wasdev/downloads/wlp/26.0.0.11/wlp-jakartaee11-26.0.0.11.zip
# - Install Directory: /opt/ibm/wlp
# - Server Name: defaultServer
# - HTTP Port: 9080
# - HTTPS Port: 9443
# - Features: adminCenter-1.0, appSecurity-6.0, pages-4.0, servlet-6.1, restfulWS-4.0, jsonb-3.0, jsonp-2.1, monitor-1.0, transportSecurity-1.0
################################################################################

set -euo pipefail

# Configuration variables
LIBERTY_VERSION="26.0.0.11"
LIBERTY_DOWNLOAD_URL="https://public.dhe.ibm.com/ibmdl/export/pub/software/websphere/wasdev/downloads/wlp/${LIBERTY_VERSION}/wlp-jakartaee11-${LIBERTY_VERSION}.zip"
INSTALL_BASE="/opt/ibm"
WLP_HOME="${INSTALL_BASE}/wlp"
SERVER_NAME="defaultServer"
HTTP_PORT="9080"
HTTPS_PORT="9443"
ADMIN_USER="${LIBERTY_ADMIN_USER:-admin}"
ADMIN_PASSWORD="${LIBERTY_ADMIN_PASSWORD:-admin123456}"
DOWNLOAD_ZIP="/tmp/wlp-jakartaee11-${LIBERTY_VERSION}.zip"

# Color formatting
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_err()  { echo -e "${RED}[ERROR]${NC} $1"; }

# 1. Root check
if [ "$EUID" -ne 0 ]; then
    log_err "Please run as root (or with sudo)."
    exit 1
fi

log_info "=== Starting Standalone Liberty Installation ==="

# 2. Check and Install Java & Utilities
log_info "Checking Java environment..."
if ! command -v java >/dev/null 2>&1; then
    log_info "Java not found. Installing OpenJDK 21 and dependencies..."
    if command -v dnf >/dev/null 2>&1; then
        dnf install -y java-21-openjdk java-21-openjdk-devel unzip wget curl
    elif command -v yum >/dev/null 2>&1; then
        yum install -y java-21-openjdk java-21-openjdk-devel unzip wget curl
    elif command -v apt-get >/dev/null 2>&1; then
        apt-get update && apt-get install -y openjdk-21-jdk unzip wget curl
    fi
fi

log_info "Java version:"
java -version

# Ensure unzip and wget are available
for cmd in unzip wget curl; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        if command -v dnf >/dev/null 2>&1; then dnf install -y "$cmd"; fi
    fi
done

# 3. Download Liberty Runtime
log_info "Preparing Liberty ZIP..."
if [ ! -f "$DOWNLOAD_ZIP" ]; then
    log_info "Downloading Liberty from ${LIBERTY_DOWNLOAD_URL}..."
    wget -c -O "$DOWNLOAD_ZIP" "$LIBERTY_DOWNLOAD_URL"
else
    log_info "Found existing download at ${DOWNLOAD_ZIP}"
fi

# 4. Extract Liberty to /opt/ibm/wlp
log_info "Extracting Liberty to ${INSTALL_BASE}..."
mkdir -p "${INSTALL_BASE}"
if [ -d "${WLP_HOME}" ]; then
    log_warn "Existing Liberty found at ${WLP_HOME}. Backing up before extraction..."
    mv "${WLP_HOME}" "${WLP_HOME}.bak.$(date +%Y%m%d%H%M%S)"
fi

unzip -q "$DOWNLOAD_ZIP" -d "${INSTALL_BASE}"
chmod -R 755 "${WLP_HOME}"

# 5. Create Liberty Server: defaultServer
SERVER_DIR="${WLP_HOME}/usr/servers/${SERVER_NAME}"
log_info "Creating Liberty server: ${SERVER_NAME}..."
if [ ! -d "${SERVER_DIR}" ]; then
    "${WLP_HOME}/bin/server" create "${SERVER_NAME}"
fi

# 6. Configure server.xml with adminCenter, security, and ports
log_info "Configuring ${SERVER_DIR}/server.xml..."

# Encode admin password using securityUtility
ENCODED_PASSWORD=$("${WLP_HOME}/bin/securityUtility" encode "${ADMIN_PASSWORD}" 2>/dev/null || echo "{xor}Lz4sLCgwLTs=")

cat > "${SERVER_DIR}/server.xml" << 'EOF_XML'
<?xml version="1.0" encoding="UTF-8"?>
<server description="Standalone Liberty Server with AdminCenter">

    <!-- Feature Manager -->
    <featureManager>
        <feature>pages-4.0</feature>
        <feature>servlet-6.1</feature>
        <feature>restfulWS-4.0</feature>
        <feature>jsonb-3.0</feature>
        <feature>jsonp-2.1</feature>
        <feature>adminCenter-1.0</feature>
        <feature>appSecurity-6.0</feature>
        <feature>monitor-1.0</feature>
        <feature>transportSecurity-1.0</feature>
    </featureManager>

    <!-- Basic User Registry -->
    <basicRegistry id="basic" realm="customRealm">
        <user name="ADMIN_USER_PLACEHOLDER" password="ADMIN_PASSWORD_PLACEHOLDER" />
        <group name="administrators">
            <member name="ADMIN_USER_PLACEHOLDER" />
        </group>
        <group name="readers">
            <member name="ADMIN_USER_PLACEHOLDER" />
        </group>
    </basicRegistry>

    <!-- Role Bindings for AdminCenter -->
    <administrator-role>
        <user>ADMIN_USER_PLACEHOLDER</user>
        <group>administrators</group>
    </administrator-role>

    <reader-role>
        <user>ADMIN_USER_PLACEHOLDER</user>
        <group>readers</group>
    </reader-role>

    <!-- HTTP/HTTPS Endpoint Configuration -->
    <httpEndpoint id="defaultHttpEndpoint"
                  host="*"
                  httpPort="HTTP_PORT_PLACEHOLDER"
                  httpsPort="HTTPS_PORT_PLACEHOLDER" />

    <!-- Keystore / SSL Configuration -->
    <!-- Liberty automatically creates a default self-signed keystore if not explicitly defined -->
    <keyStore id="defaultKeyStore" password="${keystore.password}" />

    <ssl id="defaultSSLConfig" keyStoreRef="defaultKeyStore" />

    <!-- Application Manager -->
    <applicationManager autoExpand="true"/>

</server>
EOF_XML

# Replace placeholders in server.xml
sed -i "s/ADMIN_USER_PLACEHOLDER/${ADMIN_USER}/g" "${SERVER_DIR}/server.xml"
sed -i "s|ADMIN_PASSWORD_PLACEHOLDER|${ENCODED_PASSWORD}|g" "${SERVER_DIR}/server.xml"
sed -i "s/HTTP_PORT_PLACEHOLDER/${HTTP_PORT}/g" "${SERVER_DIR}/server.xml"
sed -i "s/HTTPS_PORT_PLACEHOLDER/${HTTPS_PORT}/g" "${SERVER_DIR}/server.xml"

# Generate server.env with default keystore password if not present
if [ ! -f "${SERVER_DIR}/server.env" ]; then
    KEYSTORE_PWD=$(openssl rand -base64 16 | tr -dc 'a-zA-Z0-9' | head -c 16)
    echo "keystore.password=${KEYSTORE_PWD}" > "${SERVER_DIR}/server.env"
    chmod 600 "${SERVER_DIR}/server.env"
fi

# Create security resources directory
mkdir -p "${SERVER_DIR}/resources/security"
chmod 755 "${SERVER_DIR}/resources/security"

# 7. Install Missing Features (e.g. adminCenter-1.0 via featureUtility)
log_info "Installing required server features via featureUtility..."
"${WLP_HOME}/bin/featureUtility" installServerFeatures "${SERVER_NAME}" --acceptLicense || true

# 8. Configure Firewall (if applicable)
log_info "Configuring firewall for ports ${HTTP_PORT} and ${HTTPS_PORT}..."
if command -v firewall-cmd >/dev/null 2>&1 && systemctl is-active --quiet firewalld; then
    firewall-cmd --permanent --add-port="${HTTP_PORT}"/tcp || true
    firewall-cmd --permanent --add-port="${HTTPS_PORT}"/tcp || true
    firewall-cmd --reload || true
fi

# 9. Start / Restart Liberty Server
log_info "Starting Liberty server ${SERVER_NAME}..."
if "${WLP_HOME}/bin/server" status "${SERVER_NAME}" 2>/dev/null | grep -q "is running"; then
    "${WLP_HOME}/bin/server" stop "${SERVER_NAME}"
    sleep 2
fi

"${WLP_HOME}/bin/server" start "${SERVER_NAME}"
sleep 5

# 10. Verify Service Status
if "${WLP_HOME}/bin/server" status "${SERVER_NAME}" | grep -q "is running"; then
    log_info "=== Liberty Server successfully started! ==="
    log_info "HTTP Endpoint:  http://localhost:${HTTP_PORT}"
    log_info "HTTPS Endpoint: https://localhost:${HTTPS_PORT}"
    log_info "AdminCenter:    https://localhost:${HTTPS_PORT}/adminCenter/"
    log_info "Admin User:     ${ADMIN_USER}"
    log_info "Admin Pass:     ${ADMIN_PASSWORD}"
else
    log_err "Liberty server failed to start. Please check ${SERVER_DIR}/logs/messages.log"
    exit 1
fi
