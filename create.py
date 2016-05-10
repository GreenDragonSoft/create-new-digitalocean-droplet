#!/usr/bin/env python

import os
import json
from pprint import pprint

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
    admin_user_key = os.environ.get('ADMIN_SSH_KEY_FINGERPRINT', '')

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
    print(payload)

    headers = {
        'content-type': 'application/json',
        'authorization': 'Bearer {}'.format(get_api_token())
    }

    response = requests.post(
        "https://api.digitalocean.com/v2/droplets",
        headers=headers,
        data=payload
    )

    pprint(response.json())

    response.raise_for_status()


if __name__ == '__main__':
    main()
