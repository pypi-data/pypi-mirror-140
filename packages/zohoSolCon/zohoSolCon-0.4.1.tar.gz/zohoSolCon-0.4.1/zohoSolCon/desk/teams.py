import requests
import json


def make_header(token, org_id):
    return {
        'orgId': org_id,
        'Authorization': 'Zoho-oauthtoken {token.access}'
    }



def create_team(token, org_id, data_object):
    url = 'https://desk.zoho.com/api/v1/teams'
    headers = make_header(token, org_id)

    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return create_team(token, org_id, data_object)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content



def update_team(token, org_id, team_id, data_object):
    url = f'https://desk.zoho.com/api/v1/teams/{team_id}'
    headers = make_header(token, org_id)

    data = json.dumps(data_object).encode('utf-8')

    response = requests.patch(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return update_team(token, org_id, team_id, data_object)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content


def delete_team(token, org_id, team_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/teams/{team_id}/deleteTeam'
    headers = make_header(toke, org_id)
    data_obj = kwargs
    data = json.dumps(data_obj).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)
    if response.status_code == 401:
        token.generate()
        return delete_team(token, org_id, team_id, **kwargs)

    else:
        return token, response.status_code


def get_team(token, org_id, team_id):
    url = f'https://desk.zoho.com/api/v1/teams/{team_id}'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return get_team(token, org_id, team_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content


def get_teams(token, org_id):
    url = 'https://desk.zoho.com/api/v1/teams'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return get_teams(token, org_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("teams")


def get_team_members(token, org_id, team_id):
    url = f'https://desk.zoho.com/api/v1/teams/{team_id}/members'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return get_team_members(token, org_id, team_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("members")


def get_associable_teams(token, org_id, team_id):
    url = f'https://desk.zoho.com/api/v1/teams/{team_id}/associables'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return get_associable_teams(token, org_id, team_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get('teams')


def get_teams_by_agent(token, org_id, agent_id):
    url = f'https://desk.zoho.com/api/v1/agents/{agent_id}/teams'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return get_teams_by_agent(token, org_id, agent_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get('teams')


def get_teams_by_role(token, org_id, role_id):
    url = f'https://desk.zoho.com/api/v1/roles/{role_id}/teams'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return get_teams_by_role(token, org_id, role_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get('teams')


def get_teams_by_department(token, org_id, department_id):
    url = f'https://desk.zoho.com/api/v1/departments/{department_id}/teams'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return get_teams_by_department(token, org_id, department_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("teams")



