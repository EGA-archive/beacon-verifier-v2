import json
import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument("-url", "--url")
args = parser.parse_args()

url = args.url + '/map'

f = requests.get(url)
total_response = json.loads(f.text)
resultsets = total_response["response"]
endpoints = resultsets["endpointSets"]
list_of_endpoints=[]
def list_endpoints(list_of_endpoints, endpoints):
    for k, v in endpoints.items():
        for k2, v2 in v.items():
            if k2 == 'rootUrl':
                list_of_endpoints.append(v2)
            elif k2 == 'endpoints':
                for k3, v3 in v2.items():
                    for k4, v4 in v3.items():
                        if k4 == 'url':
                            list_of_endpoints.append(v4)
    return list_of_endpoints

endpoints_to_verify = list_endpoints(list_of_endpoints, endpoints)

