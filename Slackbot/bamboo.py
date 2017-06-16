import sys, requests, json, xml, queue, shelve, config
from requests.auth import HTTPBasicAuth

myAuth = HTTPBasicAuth(config.bamboo_uid, config.bamboo_pwd)

"""
State = [Idle, WaitingToBuild, Building]
"""
build_queue = queue.Queue();

def build(message):
    result = config.build_key_pattern.search(message)
    if result is None:
        raise BaseException("not a build message")

    project_key = result.groups()[1]

    search_key = result.groups()[1] + '-' + result.groups()[2]
    
    plans = get_plans()['plans']['plan']

    plan_key = get_plan_key(plans, project_key, search_key)

    if plan_key == None:
        raise "I couldn't find the plan. Are you sure it exists?"

    result = start_build(plan_key)
    print(result)

def get_plan_key(plans, project_key, search_key):
    for plan in plans:
        if plan['projectKey'] != project_key:
            continue

        for branch in plan['branches']['branch']:
            if branch.get('shortName', ' ').startswith(search_key):
                return branch['key']
    return None
            
def is_build_running():
    #implement
    return True

def is_someone_testing():
    #implement
    return True

def get_plans():
    result = requests.get(config.bamboo_plans_endpoint, params = {'expand':'plans.plan.branches.branch.latestResult'}, auth=myAuth)
    plans = result.json()
    return plans

def start_build(plan_key):
    uri = config.bamboo_queue_build_endpoint + str(plan_key)
    result = requests.post(uri, auth=myAuth, headers={'X-Atlassian-Token':'no-check'})
    #result.text()
    
if __name__ == '__main__':
    build('build S2S-896')
    