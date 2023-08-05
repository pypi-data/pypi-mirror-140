import requests
import json


def make_header(token, org_id):
    return {
        "orgId": org_id,
        "Authorization": f"Zoho-oauthtoken {token.access}"
    }


def get_agent(token, org_id, agent_id):
    url = f'https://desk.zoho.com/api/v1/agents/{agent_id}'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return get_agent(token, org_id, agent_id)

    else:
        data = json.loads(response.content.decode('utf-8'))
        return token, data


def get_agents(token, org_id, **kwargs):
    url = 'https://desk.zoho.com/api/v1/agents'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 401:
        token.generate()
        return get_agents(token, org_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get('data')


def get_agent_count(token, org_id, **kwargs):
    url = 'https://deks.zoho.com/api/v1/agents/count'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 401:
        token.generate()
        return get_agent_count(token, org_id, **kwargs)

    else:
        content = json.loads(respnse.content.decode('utf-8'))
        return token, content.get("count")


def activate_agents(token, org_id, agent_id_list):
    url = 'https://desk.zoho.com/api/v1/agents/activate'
    headers = make_header(token, org_id)

    data_object = {'agentIds': agent_id_list}
    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return activate_agents(token, org_id, agent_id_list)

    else:
        return token, response


def deactivate_agent(token, org_id, agent_id):
    url = f'https://desk.zoho.com/api/v1/agents/{agent_id}/deactivate'
    headers = make_header(token, org_id)

    response = requests.post(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return deactivate_agent(token, org_id, agent_id)

    else:
        return token, response


def add_agent(token, org_id, data_object):
    url = 'https://desk.zoho.com/api/v1/agents'
    headers = make_header(token, org_id)

    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return add_agent(token, org_id, data_object)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content


def update_agent(token, org_id, agent_id, data_object):
    url = f'https://desk.zoho.com/api/v1/agents/{agent_id}'
    headers = make_header(token, org_id)

    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return update_agent(token, org_id, agent_id, data_object)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content


def delete_unconfirmed_agents(token, org_id, agent_id_list):
    url = 'https://desk.zoho.com/api/v1/agents/deleteUnconfirmed'
    headers = make_header(token, org_id)

    data_object = {'agentIds': agent_id_list}
    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return delete_unconfirmed_agents(token, org_id, agent_id_list)
    else:
        return token, response.status_code


def delete_agent(token, org_id, agent_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/agents/{agent_id}/delete'
    headers = make_header(token, org_id)

    data = json.dumps(kwargs).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return delete_agent(token, org_id, agent_id, **kwargs)

    else:
        return token, response.status_code


def get_agent_by_email(token, org_id, email_id):
    url = f'https://desk.zoho.com/api/v1/agents/email/{email_id}'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return get_agent_by_email(token, org_id, email_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content


    
