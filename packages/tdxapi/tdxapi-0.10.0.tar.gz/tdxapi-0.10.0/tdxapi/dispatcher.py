import json
import logging
import mimetypes
import os
import time
from json.decoder import JSONDecodeError
from typing import Optional

import requests
from dateutil import parser
from requests import Session

from tdxapi.models import TdxModelEncoder


class Dispatcher(object):
    def __init__(
        self,
        organization: str,
        beid: Optional[str] = None,
        wskey: Optional[str] = None,
        use_sandbox: Optional[bool] = False,
    ) -> None:
        """Initialize dispatcher backend."""
        if beid is not None and wskey is not None:
            self.auth_mode = "admin"
            self.beid = beid
            self.wskey = wskey

        else:
            raise RuntimeError("beid and wskey are required")

        if use_sandbox:
            api_base = "SBTDWebApi"
        else:
            api_base = "TDWebApi"

        self.base_url = f"https://{organization.lower()}.teamdynamix.com/{api_base}"
        self.token = None
        self.session = None

        self.init_session()
        self.logger = logging.getLogger("tdxapi-dispatcher")

    def init_session(self) -> None:
        if self.auth_mode == "admin":
            response = requests.post(
                self.base_url + "/api/auth/loginadmin",
                json={"BEID": self.beid, "WebServicesKey": self.wskey},
            )

            if response.ok:
                self.token = response.text

        if self.token is None:
            raise RuntimeError("unable to obtain bearer token")

        self.session = Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            }
        )

    def send(
        self,
        method,
        path,
        params=None,
        data=None,
        file=None,
        filename=None,
        mimetype=None,
        rclass=None,
        rlist=False,
        rpartial=True,
    ):
        if data is not None:
            data = json.dumps(data, cls=TdxModelEncoder)

        if file is not None:
            if filename is None:
                filename = os.path.basename(file)

            if mimetype is None:
                mimetype = mimetypes.guess_type(file)[0]

            # Override session Content-Type to let requests handle it
            headers = {"Content-Type": None}

            files = {"file": (filename, open(file, "rb"), mimetype)}
        else:
            headers = None
            files = None

        self.logger.debug(
            f"Sending {method} to {self.base_url + path}"
            f"\n\tParams: {params}"
            f"\n\tData: {data}"
        )

        response = self.session.request(
            method,
            self.base_url + path,
            params=params,
            data=data,
            headers=headers,
            files=files,
        )

        self.logger.debug(f"Response ({response.status_code}): {response.text}")

        return self._process_response(response, rclass, rlist, rpartial)

    def _process_response(self, response, rclass, rlist, rpartial, retry=True):
        if response.ok:
            if rclass is None:
                return

            class_result = rclass.from_data(response.json(), partial=rpartial)

            if rlist and not isinstance(class_result, list):
                return [class_result]
            else:
                return class_result

        elif response.status_code == 429:
            if retry:
                # Get datetime when requests can begin again
                reset_utc = parser.parse(response.headers["X-RateLimit-Reset"])

                # Get datetime of last request
                now_utc = parser.parse(response.headers["Date"])

                # Sleep for the seconds between last request and the reset time (+5s)
                time.sleep(int((reset_utc - now_utc).total_seconds()) + 5)

                # Retry request
                return self._process_response(
                    self.session.send(response.request),
                    rclass,
                    rlist,
                    rpartial,
                    retry=False,
                )
            else:
                self._raise_error(response)

        elif response.status_code == 404:
            if response.request.method == "GET":
                return
            else:
                self._raise_error(response)

        elif response.status_code == 401:
            if retry:
                # Try starting a new session with a fresh token
                self.init_session()

                # Update auth header on prepared request before retrying
                response.request.headers.update(
                    {"Authorization": self.session.headers["Authorization"]}
                )

                # Retry request
                return self._process_response(
                    self.session.send(response.request),
                    rclass,
                    rlist,
                    rpartial,
                    retry=False,
                )
            else:
                self._raise_error(response)

        else:
            self._raise_error(response)

    def _raise_error(self, response):
        try:
            msg = response.json()

            raise RuntimeError(
                f"{response.status_code}: {msg['Message']} (ID: {msg.get('ID', 'N/A')})"
            )
        except (JSONDecodeError, KeyError, TypeError):
            raise RuntimeError(f"{response.status_code}: {response.text}") from None
