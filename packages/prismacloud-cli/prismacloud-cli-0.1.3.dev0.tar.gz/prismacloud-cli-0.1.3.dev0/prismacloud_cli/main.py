import json
import os
from pydoc import Helper
from jsondiff import JsonDiffer
import requests
import pandas as pd
from IPython.display import display
import logging
import sys
from argparse import ArgumentParser
from tabulate import tabulate
import warnings
from importlib import util
from os import path

cli = ArgumentParser()
subparsers = cli.add_subparsers(dest="subcommand")

import prismacloud_cli.version
global version 
version = prismacloud_cli.version.version

# Set defaults
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', 4)
pd.set_option('display.width', 100)
pd.set_option('display.colheader_justify', 'center')
pd.set_option('display.precision', 3)
requests.packages.urllib3.disable_warnings()
warnings.simplefilter(action='ignore', category=FutureWarning)


def subcommand(args=[], parent=subparsers):
    def decorator(func):
        parser = parent.add_parser(func.__name__, description=func.__doc__)

        # Add global parameters
        parser.add_argument("--debug", "-d", help="Show debug output", action='store_true')
        parser.add_argument("--config", help="Select config file in ~/.prismacloud (without .json extension, e.g.: local)")
        parser.add_argument("--columns", help="Select columns to show", nargs='+')
        parser.add_argument("--limit", "-l", help="Number of rows to show")
        parser.add_argument("--output", "-o", help="Output mode (json/csv/html/markdown/columns)")
        parser.add_argument("--custom", help="Add custom parameters to REST API call")

        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)

    return decorator

def argument(*name_or_flags, **kwargs):
    return ([*name_or_flags], kwargs)

@subcommand()
def users(args):
    api('users', args=args)

@subcommand()
def scans(args):
    api('scans', args=args)

@subcommand()
def registry(args):
    api('registry', args=args)

@subcommand()
def policies(args):
    api('policies/compliance/ci/serverless', args=args)

@subcommand()
def images(args):
    api('images', args=args)

@subcommand()
def tags(args):
    api('tags', args=args)

@subcommand()
def containers(args):
    api('containers', args=args)


@subcommand()
def groups(args):
    api('groups', args=args)

@subcommand()
def version(args):
    api('version', args=args)


@subcommand([argument("--type", "-t", help="Type (app-firewall, compliance, daily, dashboard, events, license, vulnerabilities")])
def stats(args):
    command = ''
    if args.type == 'app-firewall': command = 'stats/app-firewall/count'
    if args.type == 'compliance': command = 'stats/compliance'
    if args.type == 'daily': command = 'stats/daily'
    if args.type == 'dashboard': command = 'stats/dashboard'
    if args.type == 'events': command = 'stats/events'
    if args.type == 'license': command = 'stats/license'
    if args.type == 'vulnerabilities': command = 'stats/vulnerabilities'
    api(command, args=args)

### CSPM Commands
@subcommand([argument("--compact", "-c", help="Compact output mode (true/false)", action='store_true')])
def cloud(args):
    if args.compact:
        api('cloud/name', type='cspm', args=args)
    else:
        api('cloud', type='cspm', args=args)

@subcommand()
def reports(args):
    api('report', type='cspm', args=args)

@subcommand()
def audit(args):
    api('audit/redlock', type='cspm', args=args)



def login(base_url, access_key, secret_key, type='cwpp'):
    global token 
    
    try:
        logging.debug("Token exists")
        return token
    except:
        logging.debug("Logging in to %s" % type)
        if type == 'cwpp':
            url = "https://%s/api/v1/authenticate" % ( base_url )
        elif type == 'cspm':
            base_url = API_ENDPOINT
            url = "https://%s/login" % ( base_url )

        payload = json.dumps({
            "username": access_key,
            "password": secret_key
        })
        headers = {"content-type": "application/json; charset=UTF-8"}
        response = requests.post(url, headers=headers, data=payload, verify=False)
        return response.json()["token"]

def getParamFromJson(config_file):
    logging.debug('Retrieving configuration')
    f = open(config_file,)
    params = json.load(f)
    try:
        api_endpoint = params["api_endpoint"]
        pcc_api_endpoint = params["pcc_api_endpoint"]
        access_key_id = params["access_key_id"]
        secret_key = params["secret_key"]
        # Closing file
        f.close()
        return api_endpoint, pcc_api_endpoint, access_key_id, secret_key
    except:
        api_endpoint = False
        pcc_api_endpoint = params["pcc_api_endpoint"]
        access_key_id = params["access_key_id"]
        secret_key = params["secret_key"]
        # Closing file
        f.close()
        return api_endpoint, pcc_api_endpoint, access_key_id, secret_key

def api(command, output='json', type='cwpp', args=''):
    global token
    if type == 'cwpp':
        base_url = PCC_API_ENDPOINT
        url = "https://%s/api/v1/" % ( base_url )
        token = login(PCC_API_ENDPOINT, ACCESS_KEY_ID, SECRET_KEY)
    elif type == 'cspm':
        base_url = API_ENDPOINT
        url = "https://%s/" % ( base_url )
        token = login(API_ENDPOINT, ACCESS_KEY_ID, SECRET_KEY, type='cspm')

    logging.debug('API call to: %s' % type)
    logging.info('Connecting to console and fetching data')

    # Add endpoint
    endpoint = url + command + '?'

    # See if we need to add global parameters
    logging.debug('Parameters: {}'.format(args))

    if hasattr(args, 'limit') and args.limit != None:
        print(args.limit)
        logging.debug('Limit has been set')
        endpoint += 'limit={}'.format(args.limit)

    # Add custom parameters
    if hasattr(args, 'custom' ) and args.custom != None:
        logging.debug('Add custom query parameters: {}'.format(args.custom))
        endpoint += '&{}'.format(args.custom)

    headers = {"content-type": "application/json; charset=UTF-8", 'Authorization': 'Bearer ' + token }

    ### Solve default limit of 50. 
    ### Keep pulling data with offset = 0, offset = 50, offset = 100 etc.
    ### So, added to endpoint: &offset=iterator

    data = []

    stop_iteration = False

    for i in range(0, 5000, 50):
        url = endpoint+'&offset={}'.format(i)
        response = requests.get(url, headers=headers, verify=False)
        
        
        if (response.status_code == 200):
            logging.debug('HTTP Response [{}]'.format(response.status_code))
            r = response.json()
            if not r:
                logging.debug("Resultset empty")
                stop_iteration = True
            # If our response is small, we don't need to iterate
            elif len(response.content) < 1000:
                stop_iteration = True
            else:
                data += response.json()
                stop_iteration = False
            if stop_iteration:
                break
        elif (response.status_code != 200): 
            try:
                error = json.loads(response.text)['err']
            except:
                error = 'unknown'
            logging.error('HTTP Response [{}]: {}'.format(response.status_code, error))
            exit(1)

    # Read and normalize data
    try:
        df = pd.json_normalize(data)
    except:
        print(data)
        exit(0)

    # Modify fields
    try:
        df['time'] = pd.to_datetime(df.time)
    except:
        logging.debug('No time field')
    df.fillna('', inplace=True)


    ## Check args.columns to see if we need to drop all but certain columns
    if hasattr(args, 'columns') and args.columns != None:
        df.drop(columns=df.columns.difference(args.columns), axis=1, inplace=True, errors='ignore')

    
    ### If we have a list of scans and want to select last scans for images:
    try:    
        df = df.sort_values(by='entityInfo.id').drop_duplicates(subset=['entityInfo.id'], keep='last')
        df = df.sort_values(by='time')
        #print(df.sum(numeric_only=True))
        #df = pd.concat(df.sum(numeric_only=True))
        d = df.dtypes
        df.loc['Total'] = df.sum(numeric_only=True)
        df.fillna('', inplace=True)
        df.astype(d)

        logging.debug("Trying to group by entityInfo.id and select latest scans.")
    except Exception as e:
        logging.debug('{} not found, not grouping data'.format(e))
        pass



    output = args.output

    if output == 'json':
        print(df.to_json(orient='records'))
    elif output == 'csv':
        print(df.to_csv())
    elif output == 'html':
        print(df.to_html())
    elif output == 'markdown':
        print(df.to_markdown(tablefmt='grid'))
    elif output == 'columns':
        print(df.columns)
    else:
        print(tabulate(df, headers = 'keys', tablefmt = 'psql'))


def connect():
    global API_ENDPOINT, PCC_API_ENDPOINT, ACCESS_KEY_ID, SECRET_KEY, token

    import prismacloud_cli.version
    global version 
    version = prismacloud_cli.version.version

    logging.info('Running prismacloud-cli version {}'.format(version))
    PRISMA_CLOUD_DIRECTORY = os.environ['HOME'] + "/.prismacloud/"
    
    if os.path.exists(PRISMA_CLOUD_DIRECTORY):
        # If args.config has been set, load ~/.prismacloud/[args.config].json    
        if hasattr(args, 'config') and os.path.exists(os.environ['HOME'] + "/.prismacloud/{}.json".format(args.config)):
            try:
                CONFIG_FILE = PRISMA_CLOUD_DIRECTORY + "{}.json".format(args.config)   
                API_ENDPOINT, PCC_API_ENDPOINT, ACCESS_KEY_ID, SECRET_KEY = getParamFromJson(CONFIG_FILE)
            except Exception as e:
                logging.info(e)
        else:
            args.config = 'credentials'
            CONFIG_FILE = os.environ['HOME'] + "/.prismacloud/credentials.json"    
            API_ENDPOINT, PCC_API_ENDPOINT, ACCESS_KEY_ID, SECRET_KEY = getParamFromJson(CONFIG_FILE)

        logging.debug("Config loaded: {}".format(args.config))

    else:
        logging.info('Prisma cloud directory does not exists, let\'s create one in your $HOME/.prismacloud')
        os.makedirs(PRISMA_CLOUD_DIRECTORY)
        CONFIG_FILE = PRISMA_CLOUD_DIRECTORY + "credentials.json" 
        API_ENDPOINT = input("Enter CSPM API Endpoint (OPTIONAL if PCCE), eg: api.prismacloud.io: ")
        PCC_API_ENDPOINT = input("Enter CWPP API Endpoint, eg: us-east1.cloud.twistlock.com/<tenant-id>: ")
        ACCESS_KEY_ID = input("Enter the access key ID: ")
        SECRET_KEY = input("Enter the secret key: ")
        API_FILE = {
            "api_endpoint": API_ENDPOINT,
            "pcc_api_endpoint": PCC_API_ENDPOINT,
            "access_key_id": ACCESS_KEY_ID,
            "secret_key": SECRET_KEY
        } 

        json_string = json.dumps(API_FILE, sort_keys=True, indent=4)

        with open(CONFIG_FILE, 'w') as outfile:
            outfile.write(json_string)
            
        API_ENDPOINT, PCC_API_ENDPOINT, ACCESS_KEY_ID, SECRET_KEY = getParamFromJson(CONFIG_FILE) 

    token = login(PCC_API_ENDPOINT, ACCESS_KEY_ID, SECRET_KEY)
    logging.info('Done')

    
            

if __name__ == "__main__":
    args = cli.parse_args()

    if hasattr(args, 'debug') and args.debug == True:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
    else:
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')

    connect()

    if args.subcommand is None:
        cli.print_help()
    else:
        args.func(args)
