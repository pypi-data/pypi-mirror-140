import base64
import json
import logging
import os

from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape

from wkfs_wrapper.APIHandler import APIHandler
from wkfs_wrapper.Utils import clean_transaction_xml

LOGGER = logging.getLogger("root")


class WKFSAdapter:
    def __init__(
        self,
        host,
        auth_host,
        logging=False,
        wkfs_config=None,
        template_name=None,
        timeout=None
    ):
        DEFAULT_TIMEOUT = 60
        self._api_handler = APIHandler(host, headers={}, logging=logging, timeout=timeout if timeout else DEFAULT_TIMEOUT)
        self.template_name = template_name

        self.wkfs_config = wkfs_config
        self.host = host
        self.auth_host = auth_host

    def generate_package(
        self,
        transaction_data_json_input: str,
        e_sign: bool = False,
        package_name: str = None,
        log_config: dict = None,
        access_token: str = None,
    ) -> dict:
        """
        Call the `send` API for generating the document.

        :param
            transaction_data_json_input: Json input from the calling application to generate the transaction xml
            e_sign: Indicating whether e signature co-ordinates should be part of response
            package_name: The package for which documents are generated.
            access_token: The access token required to authenticate the caller.
        """

        # TODO: Plug in the Json Schema validator here?

        # If the template_package_name is not specified, then pick from the templates folder in the application
        if self.template_name is None:
            env = Environment(
                loader=FileSystemLoader(f"{os.getcwd()}/templates"),
                autoescape=select_autoescape(),
                trim_blocks=True,
                lstrip_blocks=True,
            )
        else:
            # Pick the templates folder from the specified package.
            env = Environment(
                loader=PackageLoader(self.template_name),
                autoescape=select_autoescape(),
                trim_blocks=True,
                lstrip_blocks=True,
            )
        wkfs_id = self.wkfs_config["wkfs_id"]
        packages = self.wkfs_config["packages"]
        account_id = self.wkfs_config["account_id"]
        ezConfig = self.wkfs_config["ezConfig"]

        wkfs_package = None
        wkfs_package_name = None
        wkfs_xml = None
        for package in packages:
            wkfs_package_name = package.get("name")
            if wkfs_package_name == package_name:
                wkfs_package = package.get("package_or_packet")
                wkfs_xml = package.get("template_xml")
                break

        if None in [wkfs_package, wkfs_xml]:
            raise Exception("Unable to read product configuration!")
        payload = {}
        generate = {}
        request = {}

        request["documentFormat"] = "PDF"
        ancillaryOutput = []
        if e_sign:
            esign_data = {}
            esign_data["outputType"] = "ESignatureAndFieldSupport"
            eSignatureAndFieldSupport = {
                "eSignatureCoordinatesOnly": True,
                "eSignatureDateSupport": True,
                "eSignatureTooltip": "Kindly Sign here",
                "eSignatureInitialsTooltip": "Kindly put your initials here",
                "nonSignatureFieldCoordinatesOnly": True,
                "eSignatureWKES": False,
            }

            esign_data["eSignatureAndFieldSupport"] = eSignatureAndFieldSupport
            ancillaryOutput.append(esign_data)
            request["ancillaryOutput"] = ancillaryOutput

        template = env.get_template(wkfs_xml)

        data_dict = json.loads(transaction_data_json_input)
        transaction_xml_payload = template.render(**data_dict)

        cleaned_transaction_xml_payload = clean_transaction_xml(transaction_xml_payload)

        # file1 = open("./clean_final_code.xml", "wb")
        # file1.write(cleaned_transaction_xml_payload)

        transaction_xml_payload_bytes = cleaned_transaction_xml_payload

        base64_bytes = base64.b64encode(transaction_xml_payload_bytes)
        transaction_data_base64 = base64_bytes.decode("utf-8")

        request["transactionData"] = transaction_data_base64
        request["contentIdentifier"] = f"expere://{wkfs_id}/{wkfs_package}"
        if ezConfig is not None:
            request["ezConfig"] = ezConfig
        generate["request"] = request
        payload["generate"] = generate

        headers = self._api_handler._headers
        headers["Authorization"] = f"Bearer {access_token}"
        headers["Content-Type"] = "application/json"

        self._api_handler._host = self.host
        response = self._api_handler.send_request(
            "POST",
            f"/DocumentService/api/v1/Document/account/{account_id}/generate-synchronous",
            payload=json.dumps(payload),
            log_config=log_config,
            headers=headers
        )

        LOGGER.debug(f"generate_package from wkfs wrapper completed")
        return json.loads(response)

    def get_access_token(self):
        """
        Call the `send` API for getting the access token
        """

        headers = self._api_handler._headers
        grant_type = self.wkfs_config["grant_type"]
        client_id = self.wkfs_config["client_id"]
        scope = self.wkfs_config["scope"]
        wkfs_client_certificate = self.wkfs_config["wkfs_client_certificate"]

        # Updating the host here as host for authorization is different.
        self._api_handler._host = self.auth_host
        payload = {"grant_type": grant_type, "client_id": client_id, "scope": scope}
        headers["WKFS-ClientCertificate"] = wkfs_client_certificate
        response = self._api_handler.send_request(
            "POST", f"/STS/connect/token", payload=payload, headers=headers
        )
        LOGGER.debug(f"get_access_token from wkfs wrapper completed!")
        return response
