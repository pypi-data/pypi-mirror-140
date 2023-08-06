import yaml
import requests
import json
import sys
import re

class OpsRampEnv:

    def __init__(self, envname, url, key, secret, partner_uniqueId, client_uniqueId, envfile='environments.yml', isSecure=True):
        if envname is not None:
            self.get_env(envname, envfile)
        else:
            self.getenv_nofile(url, key, secret, client_uniqueId, partner_uniqueId=None)

        self.isSecure = True
        if isinstance(isSecure, str) and (isSecure.lower() == 'false' or isSecure.lower() == 'no' or isSecure == '0'):
            self.isSecure = False
    
    def get_env(self, envname="", envfile=""):
        if hasattr(self, "env"):
            return self.env
        envstream = open(envfile, 'r')
        envs = yaml.safe_load(envstream)
        #print("Looking for environment named \"%s\" in %s." % (envname, envfile))
        filtered_envs = filter(lambda x: (x["name"] == envname), envs)
        try:
            self.env = next(filtered_envs)
            return self.env
        except StopIteration as err:
            raise Exception(f'No environment named "{envname}" found in {envfile}.')

    def getenv_nofile(self, url, key, secret, client_uniqueId, partner_uniqueId):
        if partner_uniqueId is None:
            partner_uniqueId = client_uniqueId
        if hasattr(self, "env"):
            return self.env
        else:
            self.env = {} 
            self.env['url'] = url
            self.env['partner'] = partner_uniqueId
            self.env['tenant'] = client_uniqueId
            self.env['client_id'] = key
            self.env['client_secret'] = secret
        return self.env


    def get_token(self):
        url = self.env['url'] + "/auth/oauth/token"
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.env['client_id'],
            'client_secret': self.env['client_secret']
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload, verify=self.isSecure)
        #print(response.text)
        return response.json()['access_token']

    def get_tenants(self, queryString='activeStatus=true'):
        url = f'/api/v2/tenants/{self.env["partner"]}/clients/search'
        return self.do_get(url, queryString=queryString)


    def do_get(self, urlpath, page=1, queryString=None, searchQuery=None, countonly=False, attrId=None, tenant=None, partner=None):
        headers = {
            'Content-Type'      : 'application/json',
            'Accept'            : 'application/json',
            'Authorization'     : 'Bearer ' + self.get_token()
        }

        params = {
            'pageSize': 100,
            'pageNo': page
        }

        if countonly:
            params['pageSize'] = 1

        if queryString:
            params['queryString'] = queryString

        if searchQuery:
            params['searchQuery'] = searchQuery
            params['type'] = "resources"

        url = f'{self.env["url"]}{urlpath}'

        response = requests.request("GET", url, headers=headers, verify=self.isSecure, params=params)
        try:
            responseobj = response.json()
        except Exception as e:
            print(repr(response))
            sys.exit(1)

        if countonly:
            return int(responseobj['totalResults'])

        if "results" in responseobj:
            results = responseobj['results']
        else:
            results = responseobj

        if "nextPage" in responseobj and responseobj['nextPage']:
            #print("Got %i %s from %s, proceeding to page %i" % (len(results), obtype, openv.env['name'], responseobj['nextPageNo']))
            return results + self.do_get(urlpath, page=responseobj['nextPageNo'],queryString=queryString, searchQuery=searchQuery, attrId=attrId)
        else:
            return results   