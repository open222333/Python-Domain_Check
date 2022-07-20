from genral.function import ICP, create_result
from genral import TARGET_FILE

with open(TARGET_FILE, 'r') as f:
    domains = f.read().split('\n')


for domain in domains:
    icp = ICP()
    print(icp.get_icp_check_result(domain))
