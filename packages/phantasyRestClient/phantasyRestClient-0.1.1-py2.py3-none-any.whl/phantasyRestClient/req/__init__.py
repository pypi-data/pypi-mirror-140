import requests
from phantasyRestClient.config import conf_dict
from phantasyRestClient.req.mp import MachinePortalResources

session = requests.Session()
# mp resources
MachinePortalResources.SESSION = session
MachinePortalResources.URL = conf_dict['bind']
