# -*- coding: utf-8 -*-
# MIT License
#
# Copyright (c) 2022 honam song
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import json
import time
import urllib3
import threading
import multiprocessing
from queue import Queue
from urllib.parse import urlparse
try:
    from .base import *
except:
    from base import *
try:
    from .__version__ import __version__
except:
    from __version__ import __version__

class IconNodeGetInfo:
    def __init__(self, url='http://localhost', port='9000', showlog=False):
        self.url = url
        self.port = port
        self.pool = multiprocessing.Pool(processes=3)

        self.logging = Logging(log_mode='print')
        self.showlog = showlog

        self.chain_url_path = "admin/chain/icon_dex"
        self.system_url_path = "admin/system"
        self.data_q = Queue()
        self.m_field_name = None

        if "http://" not in self.url:
            self.url = f'http://{self.url}'

        # URL에 port 포함 여부 확인
        self.url_match = "(http|https)\\:\\/\\/([a-z]|[0-9]).*:([0-9]){1,5}"
        if re.match(self.url_match, self.url):
            url_args = urlparse(self.url)
            self.url = f'{url_args.scheme}://{url_args.hostname}'
            self.port = url_args.port

        self.logging.log_print(f'++ URL : {self.url}', 'green', is_print=self.showlog)

    def get_requests(self, url, conn_timeout=5):
        if "http://" not in url:
            url = f'http://{url}'

        try:
            # self.logging.log_print(f'requests URL : {url}', 'green')
            with requests.session() as s:
                res = s.get(url, verify=False, timeout=conn_timeout)
                res_state = res.status_code
                res_json = res.json()
            s.close()
        except urllib3.exceptions.ConnectTimeoutError as e:
            self.logging.log_print(f'{e}, {url}', 'red', 'error', is_print=self.showlog)
        except requests.exceptions.ConnectionError:
            self.logging.log_print(f'-- Connection Fail!! => {url}', 'red', 'error', is_print=self.showlog)
            res_state = 599
            res_json = None

        return res_state, res_json

    def get_node(self, url=None, port=None, get_local=False,
                 get_chain=False, get_inspect=False, get_system=False, get_all=False, no_trunc=False):
        field_name = []

        if not url:
            url = self.url
        if not port:
            port = self.port

        self.logging.log_print(f'Check Node Address : {url}', 'green', is_print=self.showlog)

        node_info = {
            "ip_addr": urlparse(url).hostname,
        }

        res_state, res_json = self.get_requests(f'{url}:{port}/{self.chain_url_path}')
        if get_local and res_state != 200:
            self.logging.log_print(f'Connection Fail!! : {url}', 'red', 'error')
            sys.exit(1)

        sys_res_state, sys_res_json = self.get_requests(f'{url}:{port}/{self.system_url_path}')
        if res_state == 200:
            sys_res_json['sys_config'] = sys_res_json.pop('config')

        if res_json and sys_res_json:
            node_res_json = dict(res_json, **sys_res_json)
            chain_res_config = node_res_json.get('config')
            sys_res_setting = node_res_json.get('setting')
            sys_res_config = node_res_json.get('sys_config')
        else:
            node_res_json = None
            chain_res_config = f'599 error'
            sys_res_setting = f'599 error'
            sys_res_config = f'599 error'

        if get_chain or get_inspect or get_all:
            if node_res_json:
                if len(node_res_json.get('lastError')) == 0:
                    lasterror_value = '-'
                else:
                    lasterror_value = node_res_json.get('lastError')

                cid_value = node_res_json.get('cid')
                nid_value = node_res_json.get('nid')
                state_value = node_res_json.get('state')
                height_value = node_res_json.get('height')
            else:
                lasterror_value = f'-'
                cid_value = f'599 error'
                nid_value = f'-'
                state_value = f'-'
                height_value = f'-'

            node_chain = {
                'cid': cid_value,
                'nid': nid_value,
                'state': state_value,
                'height': height_value
            }

            if no_trunc:
                node_chain['lastError'] = lasterror_value

            node_info = dict(node_info, **node_chain)

        if get_inspect or get_all:
            if node_res_json:
                if len(chain_res_config.get("seedAddress")) >= 30:
                    seedaddress_value = f'{chain_res_config.get("seedAddress")[0:30]}...'
                else:
                    seedaddress_value = f'{chain_res_config.get("seedAddress")}'

                channel_value = node_res_json.get('channel')
                role_value = chain_res_config.get('role')
                dbtype_value = chain_res_config.get('dbType')
                address_value = sys_res_setting.get('address')[0:8]
            else:
                channel_value = f'-'
                role_value = f'-'
                dbtype_value = f'-'
                address_value = f'-'
                seedaddress_value = f'-'

            node_inspect = {
                "channel": channel_value,
                "role": role_value,
                "dbType": dbtype_value,
                "address": address_value,
                "seedAddress": seedaddress_value
            }

            if no_trunc:
                node_inspect['address'] = sys_res_setting.get('address') if node_res_json else f'-'
                node_inspect['seedAddress'] = chain_res_config.get("seedAddress") if node_res_json else f'-'
                node_inspect['autoStart'] = chain_res_config.get('autoStart') if node_res_json else f'-'

            node_info = dict(node_info, **node_inspect)

        if get_system or get_all:
            if node_res_json:
                if len(sys_res_config.get('rpcDefaultChannel')) == 0:
                    rpcdefaultchannel_value = f'-'
                else:
                    rpcdefaultchannel_value = sys_res_config.get('rpcDefaultChannel')

                buildversion_value = node_res_json.get('buildVersion')
                p2p_value = sys_res_setting.get('p2p')
                rpcdump_value = sys_res_setting.get('rpcDump')
                rpcincludedebug_value = sys_res_config.get('rpcIncludeDebug')
                rpcbatchlimit_value = sys_res_config.get('rpcBatchLimit')
                eeinstances_value = sys_res_config.get('eeInstances')
                buildtags_value = node_res_json.get('buildTags')
            else:
                if node_info.get('cid') == '599 error':
                    buildversion_value = f'-'
                else:
                    buildversion_value = f'599 error'

                rpcdefaultchannel_value = f'-'
                p2p_value = f'-'
                rpcdump_value = f'-'
                rpcincludedebug_value = f'-'
                rpcbatchlimit_value = f'-'
                eeinstances_value = f'-'
                buildtags_value = f'-'

            node_system = {
                "buildVersion": buildversion_value,
                "p2p": p2p_value,
                "rpcDump": rpcdump_value,
                "rpcIncludeDebug": rpcincludedebug_value,
                "rpcBatchLimit": rpcbatchlimit_value
            }

            if no_trunc:
                node_system['rpcDefaultChannel'] = rpcdefaultchannel_value
                node_system['eeInstances'] = eeinstances_value
                node_system['buildTags'] = buildtags_value

            node_info = dict(node_info, **node_system)

        for key in node_info.keys():
            field_name.append(key)

        if get_local:
            node_value = []
            for value in node_info.values():
                node_value.append(value)
            node_info = node_value

        self.logging.log_print(f'++ field name : {field_name}', 'green', is_print=self.showlog)
        self.logging.log_print(f'++ field data : {node_info}', 'green', is_print=self.showlog)

        return node_res_json, field_name, node_info

    def get_all_node_ip(self,):
        res_json_data, field_name, node_info = self.get_node(get_inspect=True)
        if node_info.get('role') == 0:
            seeds_ips = list(res_json_data.get('module').get('network').get('p2p').get('seeds').keys())
            for seed_ip in seeds_ips:
                node_url = f'http://{seed_ip.replace(":7100", "")}'
                res_json, field_name, node_info = self.get_node(url=node_url, get_inspect=True)
                if node_info.get('role') == 1 or node_info.get('role') == 3:
                    res_json_data = res_json
                    break
        roots_ips = list(res_json_data.get('module').get('network').get('p2p').get('roots').keys())
        seeds_ips = list(res_json_data.get('module').get('network').get('p2p').get('seeds').keys())
        nodes_ip = set(roots_ips + seeds_ips + [f'{urlparse(self.url).hostname}:7100'])

        self.logging.log_print(f'++ get_all_node_ip : {nodes_ip}', 'magenta', is_print=self.showlog)

        return nodes_ip

    def get_node_multi(self, node_ip, field_name, get_type, no_trunc=False):
        get_info = []
        node_info = None
        node_url = f'http://{node_ip.replace(":7100", "")}'

        self.logging.log_print(f'++ get_node_multi| Check URL = {node_url} , get_type = {get_type}',
                               color='magenta', is_print=self.showlog)

        if get_type == 'chain':
            res_json, field_name, node_info = self.get_node(url=node_url, get_chain=True, no_trunc=no_trunc)

        if get_type == 'chain_inspect':
            res_json, field_name, node_info = self.get_node(url=node_url, get_chain=True,
                                                            get_inspect=True, no_trunc=no_trunc)

        if get_type == 'system':
            res_json, field_name, node_info = self.get_node(url=node_url, get_system=True, no_trunc=no_trunc)

        if get_type == 'all' or not get_type:
            res_json, field_name, node_info = self.get_node(url=node_url, get_all=True, no_trunc=no_trunc)

        for field in field_name:
            if field == "ip_addr" and urlparse(self.url).hostname == node_ip.replace(":7100", ""):
                get_info.append(f'{node_ip.replace(":7100", "")}(local)')
            else:
                get_info.append(node_info.get(field))

        self.data_q.put(get_info)
        self.m_field_name = field_name

        self.logging.log_print(f'++ now queue size : {self.data_q.qsize()}', 'yellow', 'debug', is_print=self.showlog)

    def get_all_node(self, get_type='all', no_trunc=False):

        node_result = []
        thread_list = []

        field_name = ["ip_addr", "cid", "nid", "channel", "state", "role", "address", "height"]

        all_node_ip = self.get_all_node_ip()
        self.logging.log_print(f'++ get_all_node_ip : {all_node_ip}', 'green', is_print=self.showlog)

        for node_ip in all_node_ip:
            t = threading.Thread(target=self.get_node_multi, args=(node_ip, field_name, get_type, no_trunc))
            t.start()
            thread_list.append(t)

        for t in thread_list:
            t.join()

        while True:
            if self.data_q.qsize() == 0:
                self.data_q.queue.clear()
                break
            else:
                node_result.append(self.data_q.get())

        field_name = self.m_field_name
        self.logging.log_print(f'++ get_all_node | field name = {field_name}', 'green', is_print=self.showlog)
        self.logging.log_print(f'++ get_all_node | field data \n {json.dumps(node_result)}',
                               color='green', is_print=self.showlog)

        return field_name, node_result

