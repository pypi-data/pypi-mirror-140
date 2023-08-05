import requests
import json


def make_header(token, org_id):
    return {
        'orgId': org_id,
        'Authorization': 'Zoho-oauthtoken {token.access}'
    }


def get_roles(token, org_id, **kwargs):
    url = 'https://desk.zoho.com/api/v1/roles'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 401:
        token.generate()
        return get_roles(token, org_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("data")

    
def get_agents_by_role(token, org_id, role_id):
    url = f'https://desk.zoho.com/api/v1/roles/{role_id}/agents'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return get_agents_by_role(token, org_id, role_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("associatedAgents")



def create_role(token, org_id, role_name, share_with_peers=False, **kwargs):
    url = 'https://desk.zoho.com/api/v1/roles'
    headers = make_header(token, org_id)

    data_object = {
        'name': role_name,
        'shareDataWithPeers': share_with_peers
    }

    data_object['description'] = kwargs.get("description")
    data_object['reportsTo'] = kwargs.get("reportsTo")

    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return create_role(token, org_id, role_name, share_with_peers=share_with_peers, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content


def update_role(token, org_id, role_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/roles/{role_id}'
    headers = make_header(token, org_id)

    data_object = kwargs
    data = json.dumps(data_object).encode('utf-8')

    response = requests.patch(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return update_role(token, org_id, role_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content



def delete_role(token, org_id, role_id, transfer_to_id):
    url = f'https://desk.zoho.com/api/v1/roles/{role_id}/delete'
    headers = make_header(token, org_id)

    data_object = {'transferToRoleId': transfer_to_id}
    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return delete_role(token, org_id, role_id, transfer_to_id)

    else:
        return token, response.status_code


def get_role(token, org_id, role_id):
    url = f'https://desk.zoho.com/api/v1/roles/{role_id}'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return get_role(token, org_id, role_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content


def get_role_count(token, org_id, **kwargs):
    url = 'https://desk.zoho.com/api/v1/roles/count'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 401:
        token.generate()
        return get_role_count(token, org_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("count")


