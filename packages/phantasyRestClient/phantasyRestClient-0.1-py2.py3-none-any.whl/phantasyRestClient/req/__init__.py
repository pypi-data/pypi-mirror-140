import requests
from phantasyRestClient.config import read_config
from phantasyRestClient.req.mp import MachinePortalResources

conf = read_config()
session = requests.Session()
# mp resources
MachinePortalResources.SESSION = session
MachinePortalResources.URL = conf['bind']
