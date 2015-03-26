# Copyright 2015 Avi Networks Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import absolute_import

import collections
import logging
import warnings
import json
import requests

from django.conf import settings
from horizon.utils.memoized import memoized  # noqa


logger = logging.getLogger(__name__)


class AviSession():
    sess = None
    prefix = ""
    username = None
    password = None
    tenant = None
    keystone_token = None
    controller_ip = None

    def __init__(self, controller_ip, username, password=None, token=None, tenant=None):
        self.sess = requests.Session()
        self.controller_ip = controller_ip
        self.username = username
        self.password = password
        self.keystone_token = token
        self.tenant = tenant

        self.prefix = "https://%s/" % controller_ip
        self.authenticate_session()
        return

    def authenticate_session(self):
        resp = self.sess.get(self.prefix, verify=False, timeout=5)
        logger.info("resp cookies: %s", requests.utils.dict_from_cookiejar(resp.cookies))
        self.sess.headers.update({"X-CSRFToken": requests.utils.dict_from_cookiejar(resp.cookies)['csrftoken'],
                                  "Referer": self.prefix})
        body = {"username": self.username}
        if not self.keystone_token:
            body["password"] = self.password
        else:
            body["token"] = self.keystone_token
        json_resp = self.post("login", body,timeout=5, verify=False)
        if len(json_resp) <= 0:
            raise Exception("Did not get any response during authentication")
        # switch to a different tenant if needed
        if self.tenant:
            self.sess.headers.update({"X-Avi-Tenant": "%s" % self.tenant})
        self.sess.headers.update({"Content-Type": "application/json"})
        logger.info("sess headers: %s", self.sess.headers)
        return

    def update_csrf_token(self, resp):
        csrftoken = requests.utils.dict_from_cookiejar(resp.cookies).get('csrftoken', None)
        if csrftoken:
            self.sess.headers.update({"X-CSRFToken": csrftoken})
        return

    def get(self, url, *args, **kwargs):
        return self.call_api("get", self.prefix + url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self.call_api("post", self.prefix + url, *args, **kwargs)

    def call_api(self, method, *args, **kwargs):
        resp = getattr(self.sess, method)(*args, **kwargs)
        self.update_csrf_token(resp)
        if resp.status_code >= 300:
            raise Exception("URL: %s (kwargs=%s) bad response code %s content %s" %
                            (args[0], kwargs, resp.status_code, resp.content))
        logger.info("resp cookies ------ %s", resp.cookies)
        json_resp = []
        if len(resp.content) > 0:
            json_resp = json.loads(resp.content)
        logger.info("URL: %s (kwargs=%s), Status: %s, Resp: %s", args[0], kwargs, resp.status_code, json_resp)
        return json_resp


def avisession(request, tenant = None):
    controller = getattr(settings, 'AVI_CONTROLLER_IP', None)
    token = request.user.token.id
    username = request.user.username
    if not tenant:
        tenant = request.user.tenant_name
    # username = "operator"
    # password = "avi123"
    # token = None
    # tenant = None
    # session = AviSession(controller, username=username, password=password, token=token, tenant=tenant)
    session = AviSession(controller, username=username, token=token, tenant=tenant)
    return session

Cert = collections.namedtuple("Cert", ["id", "name", "cname", "iname", "algo", "self_signed", "expires"])


def certs_list(request, tenant_name):
    sess = avisession(request, tenant_name)
    certs = sess.get("/api/sslkeyandcertificate")
    certificates = []
    for cert in certs.get('results', []):
        certificates.append(Cert(id=cert["uuid"],
                                 name=cert["name"],
                                 cname=cert["certificate"]["subject"]["common_name"],
                                 iname=cert["certificate"]["issuer"].get("organization", ""),
                                 algo=cert["certificate"]["signature_algorithm"],
                                 self_signed=(cert["certificate"]["issuer"].get("organization", "") ==
                                             cert["certificate"]["subject"].get("organization", "")),
                                 expires=cert["certificate"]["not_before"]))
    return certificates


def add_cert(request, **kwargs):
    # def add_ssl_key_and_cert(sess, certname, key_str, cert_str, passphrase):
    sess = avisession(request, request.user.tenant_name)
    logger.info("sess headers: %s", sess.sess.headers)
    resp = sess.post("/api/sslkeyandcertificate/importkeyandcertificate",
                     data=json.dumps({"name": kwargs["name"],
                                      "certificate": kwargs["cert_data"],
                                      "key": kwargs["key_data"],
                                      "key_passphrase": kwargs["passphrase"]}),
                     verify=False, timeout=5)
    print "resp: %s" % resp
    return {"id": "hah"}