#!/bin/sh -eux

# Influenced by http://plusbryan.com/my-first-5-minutes-on-a-server-or-essential-security-for-linux-servers

THIS_SCRIPT="$0"
THIS_DIR="$(dirname $0)"

. ${THIS_DIR}/config.sh

ADMIN_USER="paulfurley"
ADMIN_HOME="/home/${ADMIN_USER}"

install_file() {
  DEST_FILE=$1
  SOURCE_FILE="${THIS_DIR}/skel/${DEST_FILE}"
  mkdir -p "$(dirname ${DEST_FILE})"
  cp "${SOURCE_FILE}" "${DEST_FILE}"
}

check_root() {
  if [ "$(whoami)" != "root" ]; then
    echo "You need to run as root."
    exit 1
  fi
}

update_system() {
  apt-get update
  apt-get upgrade -y
}

enable_automatic_upgrades() {
  install_file /etc/apt/apt.conf.d/20auto-upgrades
  install_file /etc/apt/apt.conf.d/50unattended-upgrades
}

install_fail_2_ban() {
  apt-get install -y fail2ban
}

add_admin_user() {

  getent passwd "${ADMIN_USER}" > /dev/null 2>&1 && EXISTS=true || EXISTS=false
  if ! $EXISTS ; then
    useradd --create-home --home-dir "${ADMIN_HOME}" --shell /bin/bash "${ADMIN_USER}" --groups ssh,sudo
    echo
    echo "Setting sudo password for ${ADMIN_USER}:"
    echo "${ADMIN_USER}:${ADMIN_SUDO_PASSWORD}" | chpasswd
  fi

  AUTHORIZED_KEYS="/home/${ADMIN_USER}/.ssh/authorized_keys"
  mkdir -p "$(dirname ${AUTHORIZED_KEYS})"
  echo "${ADMIN_SSH_KEY}" > "${AUTHORIZED_KEYS}"

  chmod 400 "${AUTHORIZED_KEYS}"
  chown -R "${ADMIN_USER}:${ADMIN_USER}" "${ADMIN_HOME}"
}

configure_sudo() {
  install_file /etc/sudoers
}

lock_down_ssh() {
  install_file /etc/ssh/sshd_config
  service ssh restart
}

setup_firewall() {
  ufw allow 22
  ufw allow 80
  ufw allow 443
  ufw --force enable
}

check_root
update_system
enable_automatic_upgrades
install_fail_2_ban
add_admin_user
configure_sudo
lock_down_ssh
setup_firewall

