#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import urllib.request

EXHIBITOR = os.environ.get('ZK_HOST')
if not EXHIBITOR:
    print("ERROR Environment variable ZK_HOST not set.")
    sys.exit(1)

SOLR_BASE_URL = os.environ.get('SOLR_BASE_URL')
if not SOLR_BASE_URL:
    print("ERROR Environment variable SOLR_BASE_URL not set.")
    sys.exit(1)

ENV = os.environ.get('ENVIRONMENT')

SOLR_API = SOLR_BASE_URL + '/admin/collections'

ZK_CLI = '/opt/solr/server/scripts/cloud-scripts/zkcli.sh'
CONFIG_DIR = os.path.join(os.getcwd(), 'configs')

for config in os.listdir(CONFIG_DIR):
    no_remote_version = False

    print("INFO Check version of configuration for [{}].".format(config))
    local_version_file = open(os.path.join(CONFIG_DIR, config, 'version'))
    local_version = local_version_file.read()
    print("INFO Local version is [{}].".format(local_version))
    try:
        output = subprocess.check_output([ZK_CLI, '-zkhost', EXHIBITOR, '-cmd', 'getfile', '/configs/' +
                                          config.replace('_', '') + '/version', config +
                                          '_version'], universal_newlines=True)
        print("DEBUG " + str(output))
    except subprocess.CalledProcessError as err:
        no_remote_version = True
        print("WARN Could not get version for [{}] from Exhibitor, will try to update configuration anyway."
              .format(config))

    if not no_remote_version and os.path.isfile(config + '_version'):
        remote_version_file = open(config + '_version')
        remote_version = remote_version_file.read()
        print("INFO Remote version is [{}].".format(local_version))

    if no_remote_version or (remote_version is not None and local_version != remote_version):
        print("INFO Update configuration for [{}].".format(config))
        try:
            output = subprocess.check_output([ZK_CLI, '-zkhost', EXHIBITOR, '-cmd', 'upconfig', '-confdir',
                                              os.path.join(CONFIG_DIR, config), '-confname',
                                              config.replace('_', '')], universal_newlines=True)

            # Reload collections after configuration update
            collection_name = config
            url = SOLR_API + '?action=RELOAD&name=' + collection_name + '&wt=json'
            try:
                request = urllib.request.Request(url)
                response = urllib.request.urlopen(request)
                code = response.getcode()
                response.close()
                if code != 200:
                    print('ERROR Could not reload collection [{}], unexpected status code from Solr: [{}]'
                          .format(collection_name, code))
                    sys.exit(1)
            except Exception as e:
                print('ERROR Could not reload collection [{}], failed sending request to Solr [{}]: {}'
                      .format(collection_name, url, e))
                sys.exit(1)

        except subprocess.CalledProcessError as err:
            print("ERROR Configuration [{}] could not be updated.".format(config))
            sys.exit(1)
