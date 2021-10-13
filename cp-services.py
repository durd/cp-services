import json
from cpapi import APIClient, APIClientArgs

def dst_mgmt_publish():
    api_res = dst_client.api_call('publish', {})
    if api_res.success:
        data = api_res.data
    else:
        data = api_res.error_message
        print(json.dumps(data, indent=2))
        exit(1)
    return data

def dst_mgmt_discard():
    api_res = dst_client.api_call('discard', {})
    if api_res.success:
        data = api_res.data
    else:
        data = api_res.error_message
        print(json.dumps(data, indent=2))
        exit(1)
    return data

def dst_mgmt_logout():
    api_res = dst_client.api_call('logout', {})
    if api_res.success:
        data = api_res.data
    else:
        data = api_res.error_message
        print(json.dumps(data, indent=2))
        exit(1)
    return data

def mgmt_add_service_groups(payload):
    api_res = dst_client.api_call('add-service-group', payload)
    if api_res.success:
        data = api_res.data
    else:
        data = api_res.error_message
        print(json.dumps(data, indent=2))
        dst_mgmt_discard()
        exit(1)
    return data

def mgmt_show_service_groups():
    api_res = src_client.api_call('show-service-groups', {'limit': 500, 'dereference-group-members': 'true', 'details-level': 'full'})
    if api_res.success:
        data = api_res.data
    else:
        data = api_res.error_message
        print(json.dumps(data, indent=2))
        exit(1)
    return data

def main():
    src_client_args = APIClientArgs(server='src-mgmt-ip', unsafe=True)
    dst_client_args = APIClientArgs(server='dst-mgmt-ip', unsafe=True)
    with APIClient(src_client_args) as src_client, APIClient(dst_client_args) as dst_client:
        # login to mgmt api
        src_login_res = src_client.login('username', 'password')

        if src_login_res.success is False:
            print('Login failed: {}'.format(src_login_res.error_message))
            exit(1)
        else:
            print('Web API login succeeded')
        # login to mgmt api
        dst_login_res = dst_client.login('username', 'password')

        if dst_login_res.success is False:
            print('Login failed: {}'.format(dst_login_res.error_message))
            exit(1)
        else:
            print('Web API login succeeded')

        groups = mgmt_show_service_groups()
        #print(json.dumps(groups, indent=2))

        new_group = {'name': ''}
        for i in groups['objects']:
            if i['domain']['name'] == 'SMC User':
                print("{} - {}".format(i['name'], i['comments']))
                members = []
                for j in i['members']:
                    print("\t{} - {}".format(j['name'], j['comments']))
                    members.append(j['name'])
                new_group.update({'name': i['name']})
                new_group['members'] = members

                res = mgmt_add_service_groups(new_group)
        if res:
            dst_mgmt_publish()
            dst_mgmt_logout()

if __name__ == "__main__":
    main()