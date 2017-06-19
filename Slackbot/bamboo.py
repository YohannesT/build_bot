import sys
import requests
import json
import xml
import queue
import shelve
import config
import xmltodict
from requests.auth import HTTPBasicAuth

myAuth = HTTPBasicAuth(config.bamboo_uid, config.bamboo_pwd)

"""
State = [Idle, WaitingToBuild, Building]
"""
build_queue = queue.Queue()

def build(message):
    result = config.build_key_pattern.search(message)
    if result is None:
        raise BaseException("not a build message")

    project_key = result.groups()[1]

    search_key = result.groups()[1] + '-' + result.groups()[2]
    
    plans = get_plans()['plans']['plan']

    plan_key = get_plan_key(plans, project_key, search_key)

    if plan_key == None:
        raise BaseException("I couldn't find the plan. Are you sure it exists?")

    result = start_build(plan_key)
    return result

def get_plan_key(plans, project_key, search_key):
    for plan in plans:
        if plan['projectKey'] != project_key:
            continue

        for branch in plan['branches']['branch']:
            if branch.get('shortName', ' ').startswith(search_key):
                return branch['key']
    return None
            
def should_i_build(message):
    re = config.build_key_pattern.search(message)
    if re is None:
        raise BaseException("not a build message")

    project_key = re.groups()[1]

    search_key = re.groups()[1] + '-' + re.groups()[2]

    result = requests.get(config.bamboo_plans_endpoint, params = {'expand':'plans.plan.latestResult'}, auth=myAuth)
    plans = result.json()
    for p in plans['plans']['plan']:
        if p['projectKey'] != project_key:
            continue

        if not p['enabled']:
            raise BaseException('The build is disabled.')
         
        if p['isBuilding']:
            raise BaseException("Can't build now. There is another build already running.")

        return True

def get_plans():
    result = requests.get(config.bamboo_plans_endpoint, params = {'expand':'plans.plan.branches.branch.latestResult'}, auth=myAuth)
    plans = result.json()
    return plans

def start_build(plan_key):
    uri = config.bamboo_queue_build_endpoint + str(plan_key)
    result = requests.post(uri, auth=myAuth, headers={'X-Atlassian-Token':'no-check'})

    value = xmltodict.parse(result.text)

    return {
                'link': config.bamboo_browse + value['restQueuedBuild']['@buildResultKey'],
                'key': value['restQueuedBuild']['@buildResultKey']
           }

def get_build_status(key):
    uri = config.bamboo_results_endpoint + str(key)
    result = requests.get(uri, auth=myAuth)

    value = xmltodict.parse(result.text)
    state = value['result']['buildState']
    duration = value['result']['buildDurationInSeconds']
    return { 'state': state, 'duration':duration }

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("I expect something like build <Start of the build plan>")
        sys.exit(1)

    build(sys.argv[1])
    