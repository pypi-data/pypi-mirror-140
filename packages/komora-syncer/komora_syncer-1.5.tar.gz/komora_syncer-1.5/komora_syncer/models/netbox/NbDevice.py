from komora_syncer.models.netbox.NetboxBase import NetboxBase
from komora_syncer.config import get_config
from komora_syncer.connections.NetboxConnection import NetboxConnection

import logging
logger = logging.getLogger(__name__)


class NbDevice(NetboxBase):
    def __init__(self, komora_obj):
        NetboxBase.__init__(self)
        self.name = komora_obj.name
        self.komora_id = komora_obj.id
        self.site_name = komora_obj.siteName
        self.komora_url = f"{get_config()['komora']['KOMORA_URL']}/app/device/{self.komora_id}"
        self.api_object = None

    def find(self):
        # 1. lookup Device by KOMORA_ID
        if self.komora_id:
            try:
                netbox_device = self.netbox.connection.dcim.devices.get(
                    cf_komora_id=self.komora_id)
                if netbox_device:
                    self.api_object = netbox_device
                    return self.api_object
            except Exception as e:
                logger.exception(
                    f"Unable to get Device by komora_id: {self.komora_id}")

        # 2. Lookup device by name, if komora id is not preseted
            # - log a problem, when the name exists, but komora_id was not found
        try:
            netbox_site = self.netbox.connection.dcim.sites.get(
                name__ie=self.site_name)
            netbox_device = self.netbox.connection.dcim.devices.get(
                name__ie=self.name, site_id=netbox_site.id)

            if netbox_device:
                logger.warning(
                    f"komora_id: {str(self.komora_id)} was not found, but Device {self.name} at site {self.site_name} already exists")
                self.api_object = netbox_device
                return self.api_object

        except Exception as e:
            logger.exception(f"Unable to get Device by name: {self.name}")

        return self.api_object

    def update(self, nb_device):
        try:
            if nb_device.update(self.get_params()):
                self.api_object = nb_device
                logger.info(f"Device: {self.name} updated successfuly")
        except Exception as e:
            logger.exception(f"Unable to update device {self.name}")

    def synchronize(self):
        device = self.find()

        if device:
            self.update(device)
        else:
            logger.info(
                f"Device {self.name} - komora_id: {self.komora_id} not found in netbox")

    def get_params(self):
        params = {}

        if self.api_object:
            if type(self.api_object.custom_fields) is dict:
                params['custom_fields'] = self.api_object.custom_fields
                params['custom_fields']['komora_id'] = self.komora_id
                params['custom_fields']['komora_url'] = self.komora_url
        else:
            params['custom_fields'] = {"komora_id": self.komora_id,
                                       "komora_url": self.komora_url}

        return params

    def get_nb_devices_data():
        import requests
        import json

        # TODO: WORKAROUND
        pynetbox = NetboxConnection()
        pynetbox.open()

        # FILTER OUT Passive Components, etc.
        # - device roles which aren't pass to Komora
        # TODO: move to config file
        filter_device_roles = pynetbox.connection.dcim.device_roles.filter(
            name=["Passive component", "unknown", "DWDM"])

        # json.dumps - IT will replace ' with " (single quotes aren't supported in graphql)
        filter_device_role_ids = json.dumps(
            [str(role.id) for role in filter_device_roles])

        # pass IDS to graphql query
        query = """
          {
            device_list(role_id__n: %s) {
              id,
              name,
              primary_ip4 {
                id,
                address
              },
              comments,
              serial,
              custom_fields,
              location {
                id,
                name,
                custom_fields
              },
              tenant {
                id,
                name,
                custom_fields
              }
              site {
                id,
                name,
                custom_fields,
                tenant{
                  id,
                  name,
                  custom_fields
                }
              },
              interfaces {
                id,
                name,
                description
              }
            }
          }
        """ % filter_device_role_ids

        try:
            url = get_config()['netbox']['NETBOX_GRAPHQL_URL']
            req = requests.post(url, json={'query': query}, headers={
                'Authorization': f"Token {get_config()['netbox']['NETBOX_API_TOKEN']}"})
            json_data = json.loads(req.text)
            return json_data
        except Exception as e:
            logger.exception(e)
            raise(e)
