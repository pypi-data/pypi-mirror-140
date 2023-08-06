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

import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)


# Documentação da click sign
#  - https://ajuda.clicksign.com/category/106-documentos
#  - https://developers.clicksign.com/docs/assinar-documentos-via-api
def hmac_sha256_hash(secret, request_signature_key):
    """
    See: https://stackoverflow.com/a/53911060/2887989
    See:
    See: https://www.freeformatter.com/hmac-generator.html#ad-output

    :param secret:
    :param request_signature_key:
    :return:
    """
    return hmac.new(
        secret.encode("utf-8"), request_signature_key.encode("utf-8"),
        hashlib.sha256
    ).hexdigest().encode("utf-8").decode("utf-8")
