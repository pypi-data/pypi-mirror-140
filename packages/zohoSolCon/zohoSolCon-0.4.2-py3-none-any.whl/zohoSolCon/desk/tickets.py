import requests
import json


def make_header(token, org_id):
    return {
        "orgId": org_id,
        "Authorization": f"Zoho-oauthtoken {token.access}"
    }


def get_ticket(token, org_id, ticket_id, **kwargs):
    url = 'https://desk.zoho.com/api/v1/tickets/{}'.format(ticket_id)
    headers = make_header(token, org_id)
    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 401:
        print("Auth")
        token.generate()
        return get_ticket(token, org_id, ticket_id, **kwargs)

    else:
        data = json.loads(response.content.decode('utf-8'))
        return token, data


def get_tickets(token, org_id, **kwargs):
    url = 'https://desk.zoho.com/api/v1/tickets'
    headers = make_header(token, org_id)
    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 401:
        print("Auth")
        token.generate()
        return get_tickets(token, org_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get('data')


def create_ticket(token, org_id, data_object):
    url = 'https://desk.zoho.com/api/v1/tickets'
    headers = make_header(token, org_id)

    data = json.dumps(data_object).encode("utf-8")
    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        print("Auth")
        token.generate()
        return create_ticket(token, org_id, data_object)
    

def update_ticket(token, org_id, ticket_id, data_object):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}'
    data = json.dumps(data_object).encode('utf-8')
    headers = make_header(token, org_id)
    response = requests.patch(url=url, headers=headers, data=data)
    if response.status_code == 401:
        print("Auth")
        token.generate()
        return update_ticket(token, org_id, ticket_id, data_object)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content


def trash_ticket(token, org_id, ticket_id_list):
    url = 'https://desk.zoho.com/api/v1/tickets/moveToTrash'
    headers = make_header(token, org_id)
    
    data_object = {'ticketIds': ticket_id_list}

    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        print("Auth")
        token.generate()
        return trash_ticket(token, org_id, ticket_id_list)

    else:
        return token, response.status_code


def move_ticket(token, org_id, ticket_id, department_id):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}/move'
    headers = make_header(token, org_id)
    data_object = {'departmentId': department_id}

    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        print("Auth")
        token.generate()
        return move_ticket(token, org_id, ticket_id, department_id)

    else:
        return token, response.status_code


def mark_read(token, org_id, ticket_id):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}/markAsRead'
    headers = make_header(token, org_id)
    response = requests.post(url=url, headers=headers)

    if response.status_code == 401:
        print("Auth")
        token.generate()
        return mark_read(token, org_id, ticket_id)

    else:
        return token, response.status_code


def mark_unread(token, org_id, ticket_id):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}/markAsUnRead'
    headers = make_header(token, org_id)
    response = requests.post(url=url, headers=headers)

    if response.status_code == 401:
        print("Auth")
        token.generate()
        return mark_unread(token, org_id, ticket_id)

    else:
        return token, reponse.status_code


def ticket_history(token, org_id, ticket_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}/History'
    headers = make_header(token, org_id)
    
    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 401:
        print("Auth")
        token.generate()
        return ticket_history(token, org_id, ticket_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content.get('data')


def ticket_resolution(token, org_id, ticket_id):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}/resolution'
    headers = make_header(token, org_id)
    response = requests.get(url=url, headers=headers)

    if response.status_code == 401:
        print("Auth")
        token.generate()
        return ticket_resolution(token, org_id, ticket_id)

    
def merge_tickets(token, org_id, ticket_id, merge_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}/merge'
    headers = make_header(token, org_id)

    data_object = {
        'ids': [merge_id],
        'source': kwargs.get('source')
    }
    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return merge_tickets(token, org_id, ticket_id, merge_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content

    
def split_ticket(token, org_id, ticket_id, thread_id):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}/threads/{thread_id}/split'
    headers = make_header(token, org_id)

    response = requests.post(url=url, headers=headers)
    if response.status_code == 401:
        token.generate()
        return split_ticket(token, org_id, ticket_id, thread_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content


def bulk_update_tickets(token, org_id, ticket_id_list, field_name, **kwargs):
    url = 'https://desk.zoho.com/api/v1/tickets/updateMany'
    headers = make_header(token, org_id)

    data_object = {
        'fieldName': field_name,
        'ids': ticket_id_list,
        'fieldValue': kwargs.get("fieldValue")
        'isCustomField': kwargs.get("isCustomField")
    }

    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return bulk_update_tickets(token, org_id, ticket_id_list, field_name, **kwargs)

    else:
        return token, response.status_code



def close_tickets(token, org_id, ticket_id_list):
    url = 'https://desk.zoho.com/api/v1/tickets/closeTickets'
    headers = make_header(token, org_id)

    data_object = {'ids': ticket_id_list}
    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return close_tickets(token, org_id, ticket_id_list)

    else:
        return token, response.status_code


def mark_as_spam(token, org_id, ticket_id_list, **kwargs):
    url = 'https://desk.zoho.com/api/v1/tickets/markSpam'
    headers = make_header(token, org_id)

    data_object = kwargs
    data_object['ids'] = ticket_id_list

    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return mark_as_spam(token, org_id, ticket_id_list, **kwargs)

    else:
        return token, response.status_code


def count_in_view(token, org_id, view_id, department_id, **kwargs):
    url = 'https://desk.zoho.com/api/v1/ticketQueueView/count'
    headers = make_header(token, org_id)

    params = {
        'viewId': view_id,
        'departmentId', department_id,
        'agentId': kwargs.get("agentId")
    }
    response = requests.get(url=url, headers=headers, params=params)

    if response.status_code == 401:
        token.generate()
        return count_in_view(token, org_id, view_id, department_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get('count')


def agents_ticket_count(token, org_id, agent_id_list, **kwargs):
    url = 'https://desk.zoho.com/api/v1/agentsTicketsCount?agentIds='
    for agent_id in agent_id_list:
        url += f"{agent_id},"

    url[-1] = ""
    headers = make_header(token, org_id)

    response = requests.get(url=url, token=token, params=kwargs)

    if response.status_code == 401:
        token.generate()
        return agents_ticket_count(token, org_id, agent_id_list, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("data")


def ticket_history(token, org_id, ticket_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}/History'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 401:
        token.generate()
        return ticket_history(token, org_id, ticket_id, **kwargs)

    else:
        content = json.loads(response.content.decode("utf-8"))
        return token, content.get("data")


def ticket_resolution(token, org_id, ticket_id):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}/resolution'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return ticket_resolution(token, org_id, ticket_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content


def resolution_history(token, org_id, ticket_id, **kwargs):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}/resolutionHistory'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 401:
        token.generate()
        return resolution_history(token, org_id, ticket_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get('data')


def update_resolution(token, org_id, content, **kwargs):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}/resolution'
    headers = make_header(token, org_id)

    data_object = {
        'content': content,
        'isNotifyContact': kwargs.get("isNotifyContact")
    }
    data = json.dumps(data_object).encode('utf-8')

    response = requests.patch(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return update_resolution(token, org_id, content, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, response.status_code, content


def delete_resolution(token, org_id, ticket_id):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}/resolution'
    headers = make_header(token, org_id)

    response = requests.delete(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return delete_resolution(token, org_id, ticket_id)

    else:
        return token, response.status_code


def get_metrics(token, org_id, ticket_id):
    url = f'https://desk.zoho.com/api/v1/tickets/{ticket_id}/metrics'
    headers = make_header(token, org_id)

    response = requests.get(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return get_metrics(token, org_id, ticket_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content


def delete_spam_tickets(token, org_id, department_id):
    url = 'https://desk.zoho.com/api/v1/tickets/emptySpam'
    headers = make_header(token, org_id)

    data_object = {'departmentId': department_id}
    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code == 401:
        token.generate()
        return delete_spam_tickets(token, org_id, department_id)

    else:
        return token, response.status_code



