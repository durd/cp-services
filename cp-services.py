import json, getpass, sys, os
from cpapi import APIClient, APIClientArgs

def dst_mgmt_publish(dst_client):
    api_res = dst_client.api_call('publish', {})
    if api_res.success:
        data = api_res.data
    else:
        data = api_res.error_message
        print(json.dumps(data, indent=2))
        exit(1)
    return data

def dst_mgmt_discard(dst_client):
    api_res = dst_client.api_call('discard', {})
    if api_res.success:
        data = api_res.data
        dst_mgmt_logout(dst_client)
    else:
        data = api_res.error_message
        print(json.dumps(data, indent=2))
        exit(1)
    return data

def dst_mgmt_logout(dst_client):
    api_res = dst_client.api_call('logout', {})
    if api_res.success:
        data = api_res.data
    else:
        data = api_res.error_message
        print(json.dumps(data, indent=2))
        exit(1)
    return data

def mgmt_add_service_groups(dst_client, payload):
    api_res = dst_client.api_call('add-service-group', payload)
    if api_res.success:
        data = api_res.data
    else:
        data = api_res.error_message
        print(json.dumps(data, indent=2))
        dst_mgmt_discard(dst_client)
        exit(1)
    return data

def mgmt_show_service_groups(src_client):
    api_res = src_client.api_call('show-service-groups', {'limit': 500, 'dereference-group-members': 'true', 'details-level': 'full'})
    if api_res.success:
        data = api_res.data
    else:
        data = api_res.error_message
        print(json.dumps(data, indent=2))
        exit(1)
    return data

def main():
    try:
        print('Source management information')
        src_mgmt_ip = input('Source management IP/hostname: ')
        src_username = input('Source management username: ')
        if sys.stdin.isatty():
            src_password = getpass.getpass('Source management password: ')
        else:
            print("Attention! Your password will be shown on the screen!")
            src_password = input('Source management password (cleartext): ')
        
        print('Destination management information')
        dst_mgmt_ip = input('Destination management IP/hostname: ')
        dst_username = input('Destination management username: ')
        if sys.stdin.isatty():
            dst_password = getpass.getpass('Destination management password: ')
        else:
            print("Attention! Your password will be shown on the screen!")
            dst_password = input('Destination management password (cleartext): ')
    except KeyboardInterrupt:
        exit(1)

    src_client_args = APIClientArgs(server=src_mgmt_ip, unsafe=True)
    dst_client_args = APIClientArgs(server=dst_mgmt_ip, unsafe=True)
    with APIClient(src_client_args) as src_client, APIClient(dst_client_args) as dst_client:
        # login to mgmt api
        src_login_res = src_client.login(src_username, src_password)
        if src_login_res.success is False:
            print('Login failed: {}'.format(src_login_res.error_message))
            exit(1)
        else:
            print('Web API login succeeded')

        # login to mgmt api
        dst_login_res = dst_client.login(dst_username, dst_password)
        if dst_login_res.success is False:
            print('Login failed: {}'.format(dst_login_res.error_message))
            exit(1)
        else:
            print('Web API login succeeded')

        groups = mgmt_show_service_groups(src_client)
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

                res = mgmt_add_service_groups(dst_client, new_group)
        if res:
            dst_mgmt_publish(dst_client)
            dst_mgmt_logout(dst_client)

if __name__ == "__main__":
    main()