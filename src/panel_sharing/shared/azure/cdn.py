"""Functionality to work with the Azure CDN"""
import logging
import threading
from typing import List

import param
from azure.identity import ClientSecretCredential
from azure.mgmt.cdn import CdnManagementClient
from codetiming import Timer

from panel_sharing import config

logger = logging.getLogger("AzureCDN")


class AzureCDN(param.Parameterized):
    """Functionality to work with the Azure CDN"""

    subscription_id = param.String(config.AZURE_SUBSCRIPTION_ID)
    resource_group_name = param.String(config.AZURE_RESOURCE_GROUP_NAME)
    profile_name = param.String(config.AZURE_CDN_PROFILE_NAME)
    endpoint_name = param.String(config.AZURE_CDN_ENDPOINT_NAME)

    def purge(self, content_paths: List[str]):
        """

        Example:

        .. code-blob:

            from panel_sharing.shared.azure.cdn import AzureCDN
            content_paths=["/MarcSkovMadsen/videostream-interface/*"]
            AzureCDN().purge(content_paths)
        """
        with Timer(name="purge"):
            thread = threading.Thread(
                target=self._purge_core, kwargs=dict(content_paths=content_paths)
            )
            thread.start()

    def _purge_core(self, content_paths: List[str]):
        credential = ClientSecretCredential(
            tenant_id=config.AZURE_TENANT_ID,
            client_id=config.AZURE_APP_CLIENT_ID,
            client_secret=config.AZURE_APP_CLIENT_SECRET,
        )
        client = CdnManagementClient(
            credential=credential,
            subscription_id=self.subscription_id,
        )
        logger.info("purge")
        with Timer(name="purge core"):
            client.endpoints.begin_purge_content(
                resource_group_name=self.resource_group_name,
                profile_name=self.profile_name,
                endpoint_name=self.endpoint_name,
                content_file_paths={"contentPaths": content_paths},
            )


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
    logger.info("start")
    paths = ["/MarcSkovMadsen/videostream-interface/*"]
    AzureCDN().purge(content_paths=paths)
    logger.info("end")
