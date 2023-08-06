#!/usr/bin/python3
import pyrebase
import os
import time
import datetime
import json

import requests

# Local imports
from pycid_dev.lib.tree.tree import Tree, deserialize
from pycid_dev.lib.craft.craft import Craft
from pycid_dev.lib.authentication.authentication import Authentication


class QueryException(Exception):
    """
    If query to the backend fails
    """

    def __init__(self, message="Unknown", errors={}):
        super().__init__(message)
        self.errors = errors


class LocalAuthenticationException(Exception):
    """
    If local auth stuffs fails
    """

    def __init__(self, message="Unknown", errors={}):
        super().__init__(message)
        self.errors = errors


class CidClient:

    kPublicConfig = {
        "apiKey": "AIzaSyDKAuaWu9qPNHU0Y9gACRDv3Esj6T8w3kE",
        "authDomain": "canarid-621aa.firebaseapp.com",
        "databaseURL": "https://canarid-621aa.firebaseio.com",
        "storageBucket": ""
    }

    def __init__(self, backend_url, path_to_auth=None):
        """
        Constructor
        """
        self._backend_url = backend_url

        self.firebase = pyrebase.initialize_app(self.kPublicConfig)

        # Note: we skip the refresh on init, instead we manually call refresh, if it actually needed to refresh,
        #       then we will sleep a second to make sure the new token propogates through the CID backend infra.
        self._authentication = Authentication(
            verbose=True, skip_refresh_on_init=True, auth_path=path_to_auth)

        if self._authentication.refresh():
            time.sleep(0.2)  # sleeping is not ideal but should do the trick

        self._user_info = self._fetch_user_info()

    # ##############################################################################
    # Public API
    # ##############################################################################

    def refresh_auth(self):
        self._authentication.refresh()

    #
    # User information queries
    #
    def crafts_info(self):
        """
        Gets the crafts available and the elements that it is composed of.
        """
        return self._user_info["instances_v0_1"]

    def fetch_craft(self, craft_id):
        """
        Pull all data for a craft from the network. Push it into a new Craft

        :returns A Craft object

        NOTE: this performs a network query
        """
        # Find the elements that the craft is composed of
        craft = None
        for craft_info in self.crafts_info():
            if craft_info["id"] == craft_id:
                craft = craft_info
        if not craft:
            raise ValueError("Provided craft id could not be found")

        # Pull down all the crates associated with the craft
        # TODO might want to keep these separated? or at a minimum store a mapping from node guid to crate guid that it belongs to
        aggregate_crate = []
        for crate in craft["instance_nodes"]:
            aggregate_crate += self._fetch_instance_crate(crate)["payload"]

        # Pull down and create the tree associated with the craft
        the_tree = self._fetch_instance_tree(craft["tree"])

        return Craft(craft["name"], craft["id"], aggregate_crate, the_tree,
                     {"component_resync_query": self._component_resync_query,
                      "component_resync_execute": self._component_resync_execute,
                      "component_attribute_edit": self._component_attribute_edit,
                      "component_attribute_remove": self._component_attribute_remove,
                      })

    def get_account_info(self):
        """
        Just return the raw firebase information for the user. Maybe its a lot of info but it is not obscured anyway at the moment so just show 'em.
        """
        return self.firebase.auth().get_account_info(self._authentication.get_secret_token_id())

    # ##############################################################################
    # Underlying client network requests
    # ##############################################################################

    #
    # Resync stuff
    #
    def _component_resync_query(self, guid, detailed_nodes_id):
        """
        :param payload: The payload to attach while requesting
        """
        return self._smart_post("/v1/instance/node/resync/query", payload={
            "guid": guid,
            "detailed_nodes_id": detailed_nodes_id
        })

    def _component_resync_execute(self, guid, detailed_nodes_id):
        """
        :param payload: The payload to attach while requesting
        """
        return self._smart_post("/v1/instance/node/resync/execute", payload={
            "guid": guid,
            "detailed_nodes_id": detailed_nodes_id
        })

    #
    # Attribute stuff
    #
    def _component_attribute_edit(self,
                                  guid,
                                  attribute_name,
                                  attribute_id,
                                  value,
                                  traits,
                                  aux,
                                  detailed_nodes_id):
        """
        :param payload: The payload to attach while requesting
        """
        # We must note that the trait has been overridden if it was inherited.
        if traits["cid::trait::v1::type"] != "custom":
            OVERRIDDEN_KEY = "cid::trait::v1::overridden"
            traits[OVERRIDDEN_KEY] = True

        return self._smart_post("/v1/instance/node/attribute/edit", payload={
            "guid": guid,
            "name": attribute_name,
            "attribute_id": attribute_id,
            "value": value,
            "traits": traits,
            "aux": aux,
            "detailed_nodes_id": detailed_nodes_id
        })

    def _component_attribute_remove(self, guid, attribute_id, detailed_nodes_id):
        """
        :param payload: The payload to attach while requesting
        """
        return self._smart_post("/v1/instance/node/attribute/remove", payload={
            "guid": guid,
            "attribute_id": attribute_id,
            "detailed_nodes_id": detailed_nodes_id
        })

    # ##############################################################################
    # Private Helpers
    # ##############################################################################

    def _smart_post(self, end_point, payload={}):
        payload.update({"username": "test_user",  # TODO remove this trash
                        "password": "test_password",
                        "isThirdParty": True})

        result = requests.post(f"{self._backend_url}{end_point}",
                               headers={
                                   "Authorization": "Bearer "+self._authentication.get_secret_token_id()},
                               json=payload
                               )
        if result.status_code != 200:
            raise QueryException(
                f"Failed to post {end_point}: {str(result.status_code)}: {result.text}")

        return result.json()

    def _fetch_user_info(self):
        return self._smart_post("/v1/user/information")

    def _fetch_instance_crate(self, crate_id):
        # TODO this api is named funy}
        return self._smart_post("/v1/instance/nodes", payload={"detailed_nodes_collection": [crate_id], })

    def _fetch_instance_tree(self, tree_id):
        # TODO this api is named funy}
        return self._smart_post("/v1/instance/tree", payload={"tree_id": tree_id, })
