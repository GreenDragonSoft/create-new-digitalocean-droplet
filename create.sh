#!/bin/sh -eux

THIS_SCRIPT=$0
THIS_DIR="$(dirname ${THIS_SCRIPT})"

DROPLET_IP="$(./create_digitalocean_droplet.py)"
# DROPLET_IP="188.166.165.46"

sleep 15s

cat > "${THIS_DIR}/bootstrap/config.sh" << EOF
# This file is created automatically from environment variables. It should not
# be kept in source control.

export ADMIN_USERNAME="${ADMIN_USERNAME}"
export ADMIN_SUDO_PASSWORD="${ADMIN_SUDO_PASSWORD}"
export ADMIN_SSH_KEY="${ADMIN_SSH_KEY}"


EOF

SSH_COMMAND="ssh -l root -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

rsync -vaz --rsh="${SSH_COMMAND}" ./bootstrap "${DROPLET_IP}:/root"

${SSH_COMMAND} "${DROPLET_IP}" "/root/bootstrap/bootstrap.sh"
