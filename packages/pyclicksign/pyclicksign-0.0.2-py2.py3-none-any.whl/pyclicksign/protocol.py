# -*- coding: utf-8 -*-
#
# Copyright 2021-2022 Flávio Gonçalves Garcia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from . import get_version
from .sign import hmac_sha256_hash
import base64
from cartola import fs
import copy
from datetime import datetime, timedelta
from firenado import get_version as firenado_get_version
from firenado.tornadoweb import get_request
import logging
import magic
import os
from peasant import get_version as peasant_get_version
from peasant.client import AsyncPeasant, PeasantTransport
from tornado import version
from tornado import escape
from tornado.httpclient import AsyncHTTPClient, HTTPClientError, HTTPResponse
from uuid import uuid4

logger = logging.getLogger(__name__)


class ClicksignApiTransport(PeasantTransport):

    def __init__(self, **kwargs):
        super(ClicksignApiTransport, self).__init__()
        self._client = AsyncHTTPClient()
        self._access_token = kwargs.get("access_token")
        self._bastion_address = kwargs.get("address",
                                           "app.clicksign.com")
        if "https://" not in  self._bastion_address:
            self._bastion_address = "https://%s" % self._bastion_address
        self._directory = None
        self.user_agent = ("PyClicksign/%s Peasant/%s Firenado/%s "
                           "Tornado/%s" %
                           (
                               get_version(),
                               peasant_get_version(),
                               firenado_get_version(),
                               version
                           ))
        self._basic_headers = {
            'User-Agent': self.user_agent
        }

    async def get(self, path, **kwargs) -> HTTPResponse:
        headers = kwargs.get('headers')
        request = get_request(path)
        if headers:
            request.headers.update(headers)
        return await self._client.fetch(request)

    async def head(self, path, **kwargs):
        headers = kwargs.get('headers')
        request = get_request(path, method="HEAD")
        _headers = copy.deepcopy(self._basic_headers)
        if headers:
            _headers.update(headers)
        request.headers.update(_headers)
        return await self._client.fetch(request)

    async def post(self, path, **kwargs):
        headers = kwargs.get('headers')
        form_data = kwargs.get("form_data", {})
        request = get_request(path, method="POST")
        _headers = copy.deepcopy(self._basic_headers)
        if headers:
            _headers.update(headers)
        request.headers.update(_headers)
        if "Content-Type" in request.headers and request.headers[
           'Content-Type'] == "application/json":
            form_data = escape.json_encode(form_data)
        request.body = form_data
        try:
            result = await self._client.fetch(request)
        except HTTPClientError as error:
            result = error.response
        return result

    def set_directory(self):
        self.peasant.directory_cache = {
            "account_test": "%s/%s?access_token=%s" % (
                self._bastion_address,
                "api/v1/accounts",
                self._access_token
            ),
            "upload_document": "%s/%s?access_token=%s" % (
                self._bastion_address,
                "api/v1/documents",
                self._access_token
            ),
            "create_signer": "%s/%s?access_token=%s" % (
                self._bastion_address,
                "/api/v1/signers",
                self._access_token
            ),
            "create_list": "%s/%s?access_token=%s" % (
                self._bastion_address,
                "/api/v1/lists",
                self._access_token
            ),
            "sign": "%s/%s?access_token=%s" % (
                self._bastion_address,
                "/api/v1/sign",
                self._access_token
            )
        }


class ClicksignPeasant(AsyncPeasant):

    def __init__(self, transport: ClicksignApiTransport):
        super(ClicksignPeasant, self).__init__(transport)

    @property
    def user_agent(self):
        return self.transport.user_agent

    async def test_account(self) -> HTTPResponse:
        directory = await self.directory()
        return await self.transport.get(directory['account_test'])

    async def upload_file(self, filename, **kwargs) -> HTTPResponse:
        if not filename:
            raise HTTPClientError(400, "É necessário informar o parametro "
                                       "filename com o endereço do arquivo"
                                       "local que será enviado para a"
                                       "ClickSign.")
        path = kwargs.get("path")
        deadline = kwargs.get("deadline", (
                datetime.now() + timedelta(days=30)
        ).strftime("%Y-%m-%dT%H:%M:%S"))

        document_data = {
            'document': {
                'path': "/%s",
                'content_base64': "data:%s;base64,%s",
                'deadline_at': "%s",
                'auto_close': True,
                'locale': "pt-BR",
                'sequence_enabled': False
            }
        }

        mime = None
        file_base46 = None
        if os.path.exists(filename):
            with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
                mime = m.id_filename(filename)
                extension = mime.split("/")[-1]
            file_base46 = base64.b64encode(fs.read(filename, True))
            if not path:
                path = "%s.%s" % (uuid4(), extension)
        document_data['document']['content_base64'] = "data:%s;base64,%s" % (
            mime, file_base46.decode())
        document_data['document']['path'] = "/%s" % path
        document_data['document']['deadline_at'] = "%s-03:00" % deadline
        directory = await self.directory()
        headers = {'Content-Type': "application/json"}
        return await self.transport.post(
            directory['upload_document'], headers=headers,
            form_data=document_data)

    async def create_signer(self, auth, name,
                            **kwargs) -> HTTPResponse:
        if not auth:
            raise HTTPClientError(400, "É necessário informar o tipo de "
                                       "autenticação de assinatura no "
                                       "parâmetro auth para a criação do "
                                       "signatário.")
        if not name:
            raise HTTPClientError(400, "É necessário informar o nome "
                                       "(parâmetro name) para a criação do "
                                       "signatário.")

        email = kwargs.get("email", None)
        phone = kwargs.get("phone", None)

        if auth in ["email", "api"] and not email:
            raise HTTPClientError(400, "O email do signatário é obrigatório "
                                       "quando nos tipos de autenticação("
                                       "parâmetro auth) contiverem email e/ou"
                                       " api.")

        if auth in ["sms", "whatsapp"] and not phone:
            raise HTTPClientError(400, "O telefone do signatário(parâmetro "
                                       "phone) é obrigatório quando nos tipos "
                                       "de autenticação(parâmetro auth) "
                                       "contiverem sms e/ou whatsapp.")

        has_documentation = kwargs.get("has_documentation", False)
        selfie_enabled = kwargs.get("selfie_enabled", False)
        handwritten_enabled = kwargs.get("handwritten_enabled", False)
        official_document_enabled = kwargs.get(
            "official_document_enabled", False)
        liveness_enabled = kwargs.get("liveness_enabled", False)
        facial_biometrics_enabled = kwargs.get("facial_biometrics_enabled",
                                               False)
        documentation = kwargs.get("documentation")
        birthday = kwargs.get("birthday")
        delivery = kwargs.get("delivery")

        signer_data = {
            'signer': {
                'auths': [auth],
                'has_documentation': has_documentation,
                'selfie_enabled': selfie_enabled,
                'handwritten_enabled': handwritten_enabled,
                'official_document_enabled': official_document_enabled,
                'liveness_enabled': liveness_enabled,
                'facial_biometrics_enabled': facial_biometrics_enabled
            }
        }

        if email:
            signer_data['signer']['email'] = email
        if phone:
            signer_data['signer']['phone_number'] = phone
        if delivery:
            signer_data['signer']['delivery'] = delivery
        if name:
            signer_data['signer']['name'] = name
        if documentation:
            signer_data['signer']['documentation'] = documentation
        if birthday:
            signer_data['signer']['birthday'] = birthday
        directory = await self.directory()
        headers = {'Content-Type': "application/json"}
        return await self.transport.post(
            directory['create_signer'], headers=headers,
            form_data=signer_data)

    async def create_list(self, document_key, signer_key, sign_as="sign",
                          **kwargs) -> HTTPResponse:
        if not document_key:
            raise HTTPClientError(400, "É necessário informar a chave do "
                                       "documento(parâmetro document_key) "
                                       "para adicionar um signatário a um "
                                       "documento.")
        if not signer_key:
            raise HTTPClientError(400, "É necessário informar a chave do "
                                       "signatário(parâmetro signer_key) "
                                       "para adicionar um signatário a um "
                                       "documento.")

        if not sign_as:
            raise HTTPClientError(400, "É necessário informar a que título "
                                       "será realizada a assinatura do "
                                       "signatário(parâmetro sign_as) "
                                       "para adicionar um signatário a um "
                                       "documento.")

        group = kwargs.get("group", None)
        message = kwargs.get("message", None)

        list_data = {
            'list': {
                'document_key': document_key,
                'signer_key': signer_key,
                'sign_as': sign_as
            }
        }

        if group:
            list_data['list']['group'] = group
        if message:
            list_data['list']['message'] = message

        directory = await self.directory()
        headers = {'Content-Type': "application/json"}
        return await self.transport.post(
            directory['create_list'], headers=headers,
            form_data=list_data)

    async def sign(self, request_signature_key, secret,
                   **kwargs) -> HTTPResponse:
        if not request_signature_key:
            raise HTTPClientError(400, "É necessário informar a chave da "
                                       "requisição da assinatura("
                                       "parâmetro request_signature_key) "
                                       "para assinar um documento.")
        if not secret:
            raise HTTPClientError(400, "É necessário informar segredo("
                                       "parâmetro secret) para assinar um "
                                       "documento.")

        list_data = {
            'request_signature_key': request_signature_key,
            'secret_hmac_sha256': hmac_sha256_hash(secret,
                                                   request_signature_key)
        }

        directory = await self.directory()
        headers = {'Content-Type': "application/json"}
        return await self.transport.post(
            directory['sign'], headers=headers,
            form_data=list_data)
