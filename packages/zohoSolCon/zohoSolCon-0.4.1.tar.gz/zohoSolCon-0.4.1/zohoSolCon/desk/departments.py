import requests
import json


def make_header(token, org_id):
    return {
        'orgId': org_id,
        'Authorization': 'Zoho-oauthtoken {token.access}'
    }


def get_department(token, org_id, department_id):
    url = f'https://desk.zoho.com/api/v1/departments/{department_id}'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return get_department(token, org_id, department_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content


def get_departments(token, org_id, **kwargs):
    url = 'https://desk.zoho.com/api/v1/departments'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 401:
        token.generate()
        return get_departments(token, org_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("data")


def get_agents_by_department(token, org_id, department_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/departments/{department_id}/agents'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 401:
        token.generate()
        return get_agents_by_department(token, org_id, departmend_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get('data')


def get_role_count(token, org_id, is_enabled=True):
    url = 'https:///desk.zoho.com/api/v1/departments/count'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers, params={"isEnabled":is_enabled})

    if response.status_code == 401:
        token.generate()
        return get_role_count(token, org_id, is_enabled=is_enabled)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get('count')


def create_department(token, org_id, data_object):
    url = 'https://desk.zoho.com/api/v1/departments'
    headers = make_header(token, org_id)

    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return create_department(token, org_id, data_object)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content


def update_department(token, org_id, department_id, data_object):
    url = f'https://desk.zoho.com/api/v1/departments/{department_id}'
    headers = make_header(token, org_id)

    data = json.dumps(data_object).encode('utf-8')

    response = requests.patch(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return update_department(token, org_id, data_object)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content


def disable_department(token, org_id, department_id, transfer_to_id, email_to_id=None):
    url = f'https://desk.zoho.com/api/v1/departments/{department_id}/disable'
    headers = make_header(token, org_id)

    data_object = {
        'emailNewDepartment': email_to_id,
        'agentNewDepartment': transfer_to_id
    }

    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return disable_department(token, org_id, department_id, transfer_to_di, email_to_id=email_to_id)

    else:
        return token, response.status_code


def enable_department(token, org_id, department_id):
    url = f'https://desk.zoho.com/api/v1/departments/{department_id}/enable'
    headers = make_header(token, org_id)

    response = requests.post(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return enable_department(token, org_id, departmend_id)

    else:
        return token, response.status_code


def associate_to_department(token, org_id, department_id, agent_id_list):
    url = f'https://desk.zoho.com/api/v1/departments/{department_id}/associateAgents'
    headers = make_header(token, org_id)

    data_object = {'agentIds': agent_id_list}

    data = json.dumps(data_object).encode('utf-8')

    

