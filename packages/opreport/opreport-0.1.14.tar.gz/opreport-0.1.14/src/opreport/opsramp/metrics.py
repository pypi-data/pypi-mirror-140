import requests
import sys
def get_metricdatasets(openv, tenant, resource, metric, startTime, endTime):
    if tenant is None:
        tenant = openv.env['tenant']
    url = f'/api/v2/metric/search?tenant={tenant}&resource={resource}&timeseries_type=RealTime&metric={metric}&startTime={str(startTime)}&endTime={str(endTime)}'
    return openv.do_get(url)

def query_metrics(openv, tenant, resource, metric, startTime, endTime):
    url = f'/metricsql/api/v3/tenants/{tenant}/metrics&resource={resource}&timeseries_type=RealTime&metric={metric}&startTime={str(startTime)}&endTime={str(endTime)}'
    return openv.do_get(url)

def promql_instance_search(openv, tenant=None, query=None):
    if tenant is None:
        tenant = openv.env['tenant']
    headers = {
        'Content-Type'      : 'application/json',
        'Accept'            : 'application/json',
        'Authorization'     : 'Bearer ' + openv.get_token()
    }

    url = f'{openv.env["url"]}/metricsql/api/v7/tenants/{tenant}/metrics/latest'
    data = {
        "query": query
    }

    response = requests.request("POST", url, headers=headers, verify=openv.isSecure, json=data)
    
    try:
        responseobj = response.json()
    except Exception as e:
        print(repr(response))
        return None

    if 'status' in responseobj and responseobj['status'] == 'success':
        return responseobj['data']['result']

    return None