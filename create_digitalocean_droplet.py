#!/usr/bin/env python

import os
import json
import logging
import time
import sys

from pprint import pformat

import requests


def get_hostname():
    return os.environ['DROPLET_HOSTNAME']


def get_region():
    region = os.environ['DIGITALOCEAN_REGION']
    assert region in set(['lon1', 'fra1']), region
    return region


def get_size():
    size = os.environ['DIGITALOCEAN_SIZE']
    assert size in set(['512mb', '1gb', '2gb', '4gb'])
    return size


def get_image():
    return os.environ['DIGITALOCEAN_IMAGE']


def get_ssh_keys():
    jenkins_key = os.environ.get('JENKINS_SSH_KEY_FINGERPRINT', '')
    admin_user_key = os.environ.get('ADDITIONAL_SSH_KEY_FINGERPRINT', '')

    ssh_keys = list(filter(None, [jenkins_key, admin_user_key]))
    return ssh_keys if ssh_keys else None


def get_make_backups():
    make_backups = os.environ['MAKE_BACKUPS']
    if make_backups.lower() in ('true', 'yes', 't', '1'):
        return True

    elif make_backups.lower() in ('false', 'no', 'f', '0'):
        return False

    else:
        raise ValueError("Can't interpret MAKE_BACKUPS='{}'".format(
            make_backups))


def get_api_token():
    return os.environ['DIGITALOCEAN_API_TOKEN']


def main():
    payload = json.dumps({
        "name": get_hostname(),
        "region": get_region(),
        "size": get_size(),
        "image": get_image(),
        "ssh_keys": get_ssh_keys(),
        "backups": get_make_backups(),
        "ipv6": True,
        "user_data": None,
        "private_networking": True
    }, indent=4)
    logging.info(pformat(payload))

    headers = {
        'content-type': 'application/json',
        'authorization': 'Bearer {}'.format(get_api_token())
    }

    response = requests.post(
        "https://api.digitalocean.com/v2/droplets",
        headers=headers,
        data=payload
    )

    logging.info(response.json())
    response.raise_for_status()

    droplet_id = response.json()['droplet']['id']

    for attempt in range(10):
        logging.info('Waiting for droplet to be "active"')
        time.sleep(10)
        response = requests.get(
            "https://api.digitalocean.com/v2/droplets/{}".format(droplet_id),
            headers=headers)
        response.raise_for_status()
        logging.info(response.json())

        if response.json()['droplet']['status'] == 'active':
            networks = response.json()['droplet']['networks']
            logging.info('networks: {}'.format(networks))

            sys.stdout.write(find_public_ip(networks))
            break


def find_public_ip(networks):
    #   networks: {u'v4': [{
    #       u'type': u'private',
    #       u'netmask': u'255.255.0.0',
    #       u'ip_address': u'10.135.19.43',
    #       u'gateway': u'10.135.0.1'
    #   },
    #   {
    #       u'type': u'public',
    #       u'netmask': u'255.255.248.0',
    #       u'ip_address': u'188.166.165.46',
    #       u'gateway': u'188.166.160.1'
    #   }],
    #   u'v6': [{u'type': u'public', u'netmask': 64,
    #   u'ip_address': u'2A03:B0C0:0003:00D0:0000:0000:06E4:D001', u'gateway':
    #   u'2A03:B0C0:0003:00D0:0000:0000:0000:0001'}]}

    for network in networks['v4']:
        if network['type'] == 'public':
            return network['ip_address']

    raise ValueError("Couldn't find public IPv4 address in: {}".format(
        networks))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    main()
