from pycid_dev.lib.crate.crate import Crate
from pycid_dev.lib.tree.tree import Tree


class Craft(object):
    class Cache:
        crates = []
        tree = None

        def clear(self):
            self.crates = []
            self.tree = None

    def __init__(self, name: str, id: str, components: list, tree: Tree, network_callbacks: dict):
        self._name = name
        self._id = id
        self._cache = self.Cache()
        # Note we just store the crates here as raw lists. the Crates object will be used when returning from this API
        # hrm why we dont just use the component structure in the cache??
        self._cache.crates = components
        self._cache.tree = tree
        self._network_callbacks = network_callbacks

        # Make sure the necessary network callbacks are present
        assert sorted(["component_resync_query",
                       "component_resync_execute",
                       "component_attribute_edit",
                       "component_attribute_remove",
                       ]) == sorted(
            self._network_callbacks.keys())

    def __repr__(self):
        return f"Craft({self._name}: {self._id}, {len(self._cache.crates)} crates, 1 tree)"

    #
    # Main API
    #
    def name(self):
        return self._name

    def id(self):
        return self._id

    def components(self, crate_id: str = None) -> Crate:
        """
        :param crate_id The id of the crate to get components for. If not provided, returns components for all crates.
        """
        # First check the query param exists
        possible_crate_ids = [crate["id"] for crate in self._cache.crates]
        if crate_id and crate_id not in possible_crate_ids:
            raise ValueError(
                f"Could not find crate id: {crate_id} for craft: {self.name()}")

        # Figure out which crates we should query
        requested_crate_ids = []
        if crate_id:
            requested_crate_ids = [crate_id]
        else:
            requested_crate_ids = possible_crate_ids

        # The main grab all the goodies
        nodes = []
        for crate in self._cache.crates:
            if crate["id"] not in requested_crate_ids:
                continue

            nodes_to_append = crate["nodes"]
            # Append in the crate id so the component can make network queries alone
            for n in nodes_to_append:
                n["crate_id"] = crate["id"]
            nodes += nodes_to_append

        # Make a crate with the current nodes in the craft, plus network callbacks that it needs
        return Crate(nodes, requested_crate_ids, {k: self._network_callbacks[k] for k in ["component_resync_query",
                                                                                          "component_resync_execute",
                                                                                          "component_attribute_edit",
                                                                                          "component_attribute_remove",
                                                                                          ]})

    def tree_root(self) -> Tree:
        return self._cache.tree

    #
    # Private
    #
