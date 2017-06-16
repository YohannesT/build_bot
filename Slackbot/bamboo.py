import sys, requests, json, xml, queue, config
from requests.auth import HTTPBasicAuth

myAuth = HTTPBasicAuth('test', 'test')


build_queue = queue.Queue();

def build(message):
    result = globals.build_key_pattern.search(message)
    if result is None:
        raise BaseException("not a build message")

    project_key = result.groups()[1]

    search_key = result.groups()[1] + '-' + result.groups()[2]
    
    plans = get_plans()['plans']['plan']

    plan_key = get_plan_key(plans, search_key)

    if plan_key == None:
        raise 'Plan not found'

    result = start_build(plan_key)

def get_plan_key(plans, search_key):
    for plan in plans:
        if plan['projectKey'] != project_key:
            continue

        for branch in plan['branches']['branch']:
            if branch.get('shortName', ' ').startswith(search_key):
                return branch['key']
    return None
            

def get_plans():
    result = requests.get(config.bamboo_plans_endpoint, params = {'expand':'plans.plan.branches.branch.latestResult'}, auth=myAuth)
    plans = result.json()
    return plans

def start_build(plan_key):
    result = requests.post(config.bamboo_queue_build_endpoint + '/' + str(plan_key), auth=myAuth, headers={'X-Atlassian-Token':'no-check'})
    result.text()

if __name__ == '__main__':
    build('build S2S-896')