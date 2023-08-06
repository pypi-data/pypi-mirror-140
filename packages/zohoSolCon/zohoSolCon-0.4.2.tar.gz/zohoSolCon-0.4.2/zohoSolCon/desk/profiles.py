import requests
import json


def make_header(token, org_id):
    return {
        'orgId': org_id,
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }


def get_profiles(token, org_id, **kwargs):
    url = 'https://desk.zoho.com/api/v1/profiles'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 401:
        token.generate()
        return get_profiles(token, org_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))

        return token, content.get("data")


def get_profile_count(token, org_id, **kwargs):
    url = 'https://desk.zoho.com/api/v1/profiles/count'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 401:
        token.generate()
        return get_profile_count(token, org_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("count")


def get_profile(token, org_id, profile_id):
    url = f'https://desk.zoho.com/api/v1/profiles/{profile_id}'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return get_profile(token, org_id, profile_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content


def clone_profile(token, org_id, profile_id, profile_name, **kwargs):
    url = f'https://desk.zoho.com/api/v1/profiles/{profile_id}/clone'
    headers = make_header(token, org_id)

    data_object = {'name': profile_name}
    data_object['description'] = kwargs.get('description')

    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return clone_profile(token, org_id, profile_id, profile_name, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content


def update_profile(token, org_id, profile_id, permissions_object, **kwargs):
    url = f'https://desk.zoho.com/api/v1/profiles/{profile_id}'
    headers = make_header(token, org_id)

    data_object = {"permissions": permissions_object}
    data_object['description'] = kwargs.get('description')

    data = json.dumps(data_object).encode('utf-8')

    response = requests.patch(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return update_profile(token, org_id, profile_id, permissions_object, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content


def delete_profile(token, org_id, profile_id, transfer_to_id):
    url = f'https://desk.zoho.com/api/v1/profiles/{profile_id}/delete'
    headers = make_header(token, org_id)

    data_object = {'transferToProfileId': transfer_to_id}
    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return delete_profile(token, org_id, profile_id, transfer_to_id)

    else:
        return token, response.status_code


def get_agents_by_profile(token, org_id, profile_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/profiles/{profile_id}/agents'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 401:
        token.generate()
        return get_agents_by_profile(token, org_id, profile_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("agents")


