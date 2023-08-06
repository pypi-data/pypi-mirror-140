from typing import Dict, Any, List

import requests
from http import HTTPStatus
from requests import Response
from gigapipe.exceptions import GigapipeServerError
from gigapipe.api_client.api import Base
from gigapipe.api_client.gigapipe_api import GigapipeApi


class Clusters(Base):
    """
    Clusters Class
    """

    def __init__(self, api):
        """
        Clusters Constructor
        :param api: The API instance
        """
        super(Clusters, self).__init__(api)

    @GigapipeApi.autorefresh_access_token
    def get_clusters(self) -> Response:
        """
        Obtains all the clusters for the organization the user belongs to
        :return: A list containing the clusters
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters"

        try:
            response: Response = requests.get(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def get_cluster(self, cluster_slug: str) -> Response:
        """
        Obtains a single cluster according to the passed slug
        :param cluster_slug: the cluster slug
        :return: A dictionary containing the cluster info
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}"

        try:
            response: Response = requests.get(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def create_cluster(self, cluster_payload: Dict[str, Any]) -> Response:
        """
        Creates a new cluster
        :param cluster_payload: the dictionary containing the necessary info to create a cluster
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters"

        try:
            response: Response = requests.post(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            }, json=cluster_payload)
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def query_cluster(self, cluster_slug: str, query: str) -> Response:
        """
        Obtains all the clusters for the organization the user belongs to
        :param cluster_slug: the cluster slug
        :param query: the clisckhose query
        :return: A dictionary containing the clickhouse response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}/query?query={query}"

        try:
            response: Response = requests.get(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def get_metadata(self, cluster_slug: str) -> Response:
        """
        Obtains the metadata of the cluster
        :param cluster_slug: the cluster slug
        :return: A dictionary containing the metadata
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}/metadata"

        try:
            response: Response = requests.get(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def stop_cluster(self, cluster_slug: str) -> Response:
        """
        Stops the cluster but doesn't get rid of it
        :param cluster_slug: the cluster slug
        :return: A message response
        """
        return self._cluster_stop_resume(cluster_slug=cluster_slug, action="stop")

    @GigapipeApi.autorefresh_access_token
    def resume_cluster(self, cluster_slug: str) -> Response:
        """
        Starts a cluster that had been stopped
        :param cluster_slug: the cluster slug
        :return: A message response
        """
        return self._cluster_stop_resume(cluster_slug=cluster_slug, action="resume")

    def _cluster_stop_resume(self, cluster_slug: str, action: str):
        """
        Cluster start/stop
        :param cluster_slug: the cluster slug
        :param action: whether to start or stop
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}/{action}"
        try:
            response: Response = requests.patch(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def get_costs(self) -> Response:
        """
        Obtains the list of costs of all the clusters of the organization
        :return: A list containing the cost per cluster
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/costs/all"

        try:
            response: Response = requests.get(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def transfer_cluster(self, cluster_slug: str, email: str) -> Response:
        """
        Transfers the cluster to another user of the organization as long as they have permission to hold it
        :param cluster_slug: the cluster slug
        :param email: the email of the target user
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}/transfer?email={email}"

        try:
            response: Response = requests.patch(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def scale_nodes(self, cluster_slug: str, *, payload: dict) -> Response:
        """
        Adds shards and replicas to an existing cluster
        :param cluster_slug: the cluster slug
        :param payload: the scaling payload
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}/scale/nodes"

        try:
            response: Response = requests.post(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            }, json=payload)
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def add_disks(self, cluster_slug: str, *, payload: List[dict]) -> Response:
        """
        Adds shards and replicas to an existing cluster
        :param cluster_slug: the cluster slug
        :param payload: the scaling payload
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}/disks"

        try:
            response: Response = requests.post(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            }, json=payload)
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def change_machine(self, cluster_slug: str, machine_id: int) -> Response:
        """
        Changes the machine of a cluster
        :param cluster_slug: the cluster slug
        :param machine_id: the id og the new machine
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}/machine"

        try:
            response: Response = requests.patch(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            }, json={"machine_id": machine_id})
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def autoscale_disk(self, cluster_slug: str, payload: Dict[str, Any]) -> Response:
        """
        Sets the disk autoscaling for a given disk and cluster
        :param cluster_slug: the cluster slug
        :param payload: the autoscale payload
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}/disks/autoscale"

        try:
            response: Response = requests.patch(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            }, json=payload)
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def get_autoscaling(self, cluster_slug: str, *, disk_id: int) -> Response:
        """
        Obtains the disk autoscaling for a given disk and cluster
        :param disk_id: the id of the disk
        :param cluster_slug: the cluster slug
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}/disks/{disk_id}/autoscale"

        try:
            response: Response = requests.get(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def delete_autoscaling(self, cluster_slug: str, *, disk_id: int) -> Response:
        """
        Does away with the autoscaling for a given disk
        :param disk_id: the id of the disk
        :param cluster_slug: the cluster slug
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}/disks/{disk_id}/autoscale"

        try:
            response: Response = requests.delete(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def delete_cluster(self, cluster_slug: str) -> Response:
        """
        Creates a new cluster
        :param cluster_slug: the cluster slug
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}"

        try:
            response: Response = requests.delete(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

