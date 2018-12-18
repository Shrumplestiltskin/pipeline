#!/usr/bin/python3
#Some helpers for write + read rabbitmq scripts

import requests 
from os import environ
vault_server = environ['VAULT_ADDR']
kube_role = environ['KUBE_ROLE']

def get_approle_ids(token):
    '''takes token and returns an app secret id'''
    secret_id_url = vault_server + '/v1/auth/approle/role/rabbit-approle/secret-id'
    role_id_url = vault_server + '/v1/auth/approle/role/rabbit-approle/role-id'
    headers = {'X-Vault-Token': token}
    r = requests.post(secret_id_url, headers=headers)
    secret_id = r.json()['data']['secret_id']
    r = requests.get(role_id_url, headers=headers)
    role_id = r.json()['data']['role_id']
    return role_id, secret_id

def create_approle_token(role_id, secret_id):
    '''takes an approle role id and secret id and returns an approle token'''
    token_url = vault_server + '/v1/auth/approle/login'
    r = requests.post(token_url, json={'role_id':role_id, 'secret_id':secret_id})
    approle_token = r.json()['auth']['client_token']
    return approle_token

def kubernetes_auth_method(jwt):
    kube_auth_url = vault_server + '/v1/auth/kubernetes/login'
    r = requests.post(kube_auth_url, json={'jwt': jwt, 'role': kube_role})
    vault_token = r.json()['auth']['client_token']
    return vault_token

def create_dynamic_credential(token):
    '''takes an approle token and creates dynamic credentials in rabbitmq'''
    rabbit_cred_url = vault_server + '/v1/rabbitmq/creds/rabbit-role'
    headers = {'X-Vault-Token': token}
    r = requests.get(rabbit_cred_url, headers=headers)
    un = r.json()['data']['username']
    pw = r.json()['data']['password']
    return un, pw

def revoke_approle_token(approle_token):
    '''revokes the issued approle token by destroying itself thus cleaning up
    any dynamic credentials created with it'''
    revoke_token_url = vault_server + '/v1/auth/token/revoke-self'
    headers = {'X-Vault-Token': approle_token}
    r = requests.post(revoke_token_url, headers=headers)
    if r.status_code == 204:
        print('\nToken revoked')
    else:
        print('\nToken revocation issue')
