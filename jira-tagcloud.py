# -*- coding: utf-8 -*-

from requests.auth import HTTPBasicAuth
import urllib3
import requests
import logging
import json
import re
import string

JIRA_API = "https://jirasoftware.catho.com.br/rest/api/2/" 
SEARCH = "search/"

FIELDS = "description"
MAX_RESULTS = 50
JQL = "project = Incidentes AND \"Equipe Responsável\" in (Thunderfighter, Thunderbolts)"

logging.basicConfig(level=logging.INFO)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

COMMON_WORDS = ['que', 'verificar', 'poderiam', 'favor', 'casos', 'sendo', 'foram', 'dia', 'sistema', 'porém', 'anexo', 'tarde', 'pois', 'nos', 'temos', 'correto', 'número', 'Jose', 'José', 'algumas', 'podem' , 'isso', 'Anexo','clientes', 'existem', 'seja', 'Brito', 'problema', 'erro', 'pessoal', 'favor', 'possível', 'estamos', 'gentileza', 'já', 'leandro', 'anexo', 'obrigada', 'apenas', 'esse', 'essa', 'esses', 'essas', 'identificamos', '-', 'segue', 'obrigada', 'prezados']

def strip_common_words(s):
    for word in COMMON_WORDS:
        regex = '[ |\W]' + word.lower() + '[ |\W]'
        s = re.sub(regex, ' ', s)
    return s

def load_data(jql, fields, project = None):
    result = {"data":[]}
    
    params = {
        "fields": fields,
        "maxResults": MAX_RESULTS,
        "Content-Type": "application/json",
        "startAt": 0,
        "jql": jql
    }

    if project != None:
        params['jql'] = params['jql'].replace("%PROJ%", project)
    total = 2


    while params['startAt'] < total:
        json = requests.get(JIRA_API + SEARCH, params = params, auth = load_auth_info(".auth.info"), verify=False).json()
        total = json['total']
        logging.info("Read from " + str(params['startAt']) + " to " + str(params['startAt'] + params['maxResults']) + " of " + str(total))
        params['maxResults'] = json['maxResults'] 
        params['startAt'] += params['maxResults']
        result['data'].extend(json['issues'])

    return result

def load_auth_info(path):
    with open(path) as f:
        credentials = f.readline()
    user, password = credentials.split(":")

    return HTTPBasicAuth(user, password)

if __name__ == "__main__":
    data_array = load_data(JQL, FIELDS).get('data')
    data = ''
    for d in data_array:
        data = data + d.get('fields').get(FIELDS)
        data = data + '\n'
    data = data.lower()
    data = re.sub('\s+', ' ', data)
    data = strip_common_words(data)
    print(data.encode('utf-8'))
#print(json.dumps(data, indent=4))