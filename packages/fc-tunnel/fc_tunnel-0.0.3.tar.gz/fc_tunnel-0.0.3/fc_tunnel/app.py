# -*- coding: utf-8 -*-

from alibabacloud_tunnel_service20210509.client import Client as tsClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tunnel_service20210509 import models as ts_models
import os, json, random, string, time
import fc2
import signal
import subprocess
from retry import retry
import argparse

import logging
logging.basicConfig(
    format='%(asctime)s  %(filename)s  %(levelname)s: %(message)s', level=logging.INFO)

class ServerlessVPN:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.initFcClt()
        self.initTsClt()
        self.session = {}

    @property
    def tsEndpoint(self):
        return 'tunnel-service.cn-hangzhou.aliyuncs.com'

    @property
    def localImage(self):
        return 'registry.cn-beijing.aliyuncs.com/aliyunfc/vpn-local-proxy:v0.0.1'

    @property
    def fcImage(self):
        return 'registry.cn-beijing.aliyuncs.com/aliyunfc/vpn-fc-proxy:v0.0.1'

    def initTsClt(self):
        ak_id = self.config['akId']
        ak_secret = self.config['akSecret']
        config = open_api_models.Config(
            access_key_id=ak_id,
            access_key_secret=ak_secret
        )
        # 访问的域名
        config.endpoint = self.tsEndpoint
        self.tsClt = tsClient(config)


    def initFcClt(self):
        ak_id = self.config['akId']
        ak_secret = self.config['akSecret']
        fc_endpoint= "http://{}.{}.fc.aliyuncs.com".format(self.config['accountId'], self.config['region'])
        self.fcClt = fc2.Client(endpoint=fc_endpoint, accessKeyID=ak_id, accessKeySecret=ak_secret)


    def create_session(self):
        sessionName = "SESSION-" + ''.join(random.sample(string.ascii_letters + string.digits, 8))
        req = ts_models.CreateSessionRequest(sessionName)
        r = self.tsClt.create_session(req)
        ret = r.body.to_map()
        logging.info("create session result = \n {}".format(ret))

        self.session = {
            'sessionId': ret['data']['sessionId'],
            'sessionName': ret['data']['sessionName'],
            'localInstanceId': ret['data']['localInstanceId'],
            'remoteInstanceId': ret['data']['remoteInstanceId'],
        }


    def create_helper_function(self):
        serviceName = self.session['sessionName']
        logging.info("create_helper_function, service={}, function=helper".format(serviceName))
        vpcId = self.config['vpcId']
        vSwitchIds = self.config['vSwitchIds']
        securityGroupId = self.config['securityGroupId']
        self.fcClt.create_service(serviceName,
            description="Auto generated proxied session: {}".format(self.session['sessionId']),
            internetAccess=True, role='acs:ram::1986114430573743:role/aliyunfcdefaultrole',
            vpcConfig={
              "vpcId": vpcId,
              "vSwitchIds": [vSwitchIds],
              "securityGroupId": securityGroupId
            }
        )
        functionName = "helper"
        self.fcClt.create_function(serviceName, functionName,
            runtime='custom-container', handler='index.handler',
            memorySize=128, timeout=900,
            customContainerConfig={
               'image': self.fcImage,
               'accelerationType': 'Default'
            },
            environmentVariables={
               'TUNNEL_SERVICE_HOST': self.tsEndpoint,
               'TUNNEL_SERVICE_INSTANCE_ID': self.session['remoteInstanceId'],
               'TUNNEL_SERVICE_SESSION_ID': self.session['sessionId'],
               'TUNNEL_SERVICE_AK_ID': self.config['akId'],
               'TUNNEL_SERVICE_AK_SECRET': self.config['akSecret']
            }
        )

        alias = "LATEST"
        # 预留直到预留的实例启动成功
        logging.info("wait for provision success ...")
        self.fcClt.put_provision_config(serviceName, alias, functionName, 1)
        while 1:
            r = self.fcClt.get_provision_config(serviceName, alias, functionName).data
            # print("current = {}".format(r['current']))
            if r['current'] == 1:
                break
            time.sleep(1)

        # 设置弹性实例个数为 0，确保 FC 端只会启动一个 容器
        api_version = "2016-08-15"
        method = 'PUT'
        path = '/{0}/services/{1}.{2}/functions/{3}/on-demand-config'.format(api_version, serviceName, alias, functionName)
        headers = self.fcClt._build_common_headers(method, path, {})
        payload = {"maximumInstanceCount": 0}
        r = self.fcClt._do_request(method, path, headers, body=json.dumps(payload).encode('utf-8'))
        logging.info("on-demand-config put result = {}".format(r.json()))

    def start_local_proxy(self):
        logging.info("start local  proxy container ...")
        sessionId = self.session['sessionId']
        ak_id = self.config['akId']
        ak_secret = self.config['akSecret']
        localInstanceId = self.session['localInstanceId']
        remote_ip = self.config['remoteIP']
        remote_ports = [x.strip() for x in  self.config['remotePorts'].split(",")]
        vol = " ".join(["-p {}:{}".format(x,x) for x in remote_ports])

        env = '-e TUNNEL_SERVICE_SESSION_ID={0} -e TUNNEL_SERVICE_INSTANCE_ID={1} -e TUNNEL_SERVICE_AK_ID={2} -e TUNNEL_SERVICE_AK_SECRET={3} -e CFG_REMOTE_IP={4} -e CFG_REMOTE_PORTS={5}'.format(
            sessionId, localInstanceId,  ak_id, ak_secret, remote_ip, self.config['remotePorts'])

        cmd = 'docker run --rm  --privileged -d {0} {1} --name VPN-Local-{2} {3}'.format(
            vol, env, sessionId, self.localImage)

        print(cmd)
        subprocess.check_call(cmd, shell=True)
        logging.info("waiting util Session is OK ...")
        while 1:
            r = self.tsClt.get_session(sessionId)
            ret = r.body.to_map()
            # print(ret)
            if ret['data']['status'] == 'ESTABLISHED':
                break
            time.sleep(1)
        logging.info("Session is OK! now you can remote debug")

        while 1:
            time.sleep(10)
            r = self.tsClt.get_session(sessionId)
            ret = r.body.to_map()
            if ret['data']['status'] != 'ESTABLISHED':
                break
        logging.info("Session is abnormal exit")

    def setup(self):
        self.create_session()
        self.create_helper_function()
        self.start_local_proxy()

    def cleanup(self):
        sessionId = self.session['sessionId']
        try:
            r = self.tsClt.delete_session(sessionId)
            logging.info(r.body)
        except Exception as e:
            print(str(e))

        serviceName = self.session['sessionName']
        functionName = 'helper'
        alias = "LATEST"
        try:
            self.fcClt.put_provision_config(serviceName, alias, functionName, 0)
            while 1:
                r = self.fcClt.get_provision_config(serviceName, alias, functionName).data
                # print("target = {}".format(r['target']))
                if r['target'] == 0:
                    break
                time.sleep(1)
        except Exception as e:
            print(str(e))

        try:
            # 删除设置弹性实例个数为0， 目前 python sdk 不支持 ...
            api_version="2016-08-15"
            method = 'DELETE'
            path = '/{0}/services/{1}.{2}/functions/{3}/on-demand-config'.format(api_version, serviceName, alias, functionName)
            headers = self.fcClt._build_common_headers(method, path, {})
            r = self.fcClt._do_request(method, path, headers)
            logging.info("on-demand-config delete result = {}".format(r.status_code))
        except Exception as e:
            print(str(e))

        time.sleep(2)
        self._cleanServiceFunction()
        cmd = '''docker kill VPN-Local-{} && docker rm VPN-Local-{}'''.format(sessionId, sessionId)
        print(cmd)
        subprocess.call(cmd, shell=True)
        logging.info("cleanup success!!!")

    @retry((Exception), tries=3, delay=1, backoff=2, max_delay=8)
    def _cleanServiceFunction(self):
        serviceName = self.session['sessionName']
        functionName = 'helper'
        self.fcClt.delete_function(serviceName, functionName)
        self.fcClt.delete_service(serviceName)


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(
        "-c",
        "--config",
        default="config.json",
        help="Config file path, Defaults to 'config.json'"
    )
    args = parser.parse_args()

    vpn = ServerlessVPN(args.config)

    def clean(sig, frame):
        logging.info("stop by signal {}, auto cleanup ...".format(sig))
        try:
            vpn.cleanup()
        except:
            pass

    signal.signal(signal.SIGTERM, clean)
    signal.signal(signal.SIGINT, clean)
    signal.signal(signal.SIGQUIT, clean)
    signal.signal(signal.SIGILL, clean)

    try:
        vpn.setup()
    except:
        pass