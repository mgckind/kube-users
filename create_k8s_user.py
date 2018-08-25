from __future__ import print_function
import os
import sys
import argparse
from subprocess import call

def phead(msg = None, pre='[ooo] '):
    sys.stdout.write(pre)
    sys.stdout.flush()
    if msg:
        print(msg)
    

parser = argparse.ArgumentParser(description='Add new user')
parser.add_argument('user', type=str, help='username, which it needs to be added to the machine first')
parser.add_argument('namespace', type=str, help='namespace for the developer')
parser.add_argument('--ca', type=str, help='path to ca certificates ca.key, ca.crt', default='/home/mcarras2/.pki/kube')
parser.add_argument('--template', type=str, help='kube config template', default='template')
args = parser.parse_args()
conf = {}
conf['user'] = args.user
conf['namespace'] = args.namespace
conf['pki'] = args.ca
conf['template'] = args.template

print('\n')
print('=======================================================================')
phead(msg='Creating namespace {namespace}'.format(**conf))
phead()
err = call('kubectl create namespace {namespace}'.format(**conf), shell=True)
if err != 0: phead(msg=' ** WARNING ** above', pre='[_X_] ' )
phead(msg='Creating certificates for {user}'.format(**conf))
phead()
err = call('openssl genrsa -out {user}.key 2048'.format(**conf),shell=True)
phead()
err = call('openssl req -new -key {user}.key -out {user}.csr -subj "/CN={user}/O={namespace}"'.format(**conf), shell=True)
err = call('openssl x509  -req -in {user}.csr -CA {pki}/ca.crt -CAkey {pki}/ca.key -CAcreateserial -out {user}.crt -days 500'.format(**conf), shell=True)
err = call('cp {template} config_{user}'.format(**conf), shell=True)
phead(msg='Adding {user} to {namespace}'.format(**conf))
phead()
err = call('kubectl config set-credentials {user} --kubeconfig=config_{user} --client-certificate={user}.crt --client-key={user}.key --embed-certs=true'.format(**conf), shell=True)
if err != 0: phead(msg=' ** WARNING ** above', pre='[_X_] ' )
phead()
err = call('kubectl config set-context {namespace}-context --namespace={namespace} --user={user} --cluster=kubernetes --kubeconfig=config_{user} '.format(**conf), shell=True)
if err != 0: phead(msg=' ** WARNING ** above', pre='[_X_] ' )
phead()
err = call('kubectl config set current-context {namespace}-context --kubeconfig=config_{user}'.format(**conf), shell=True)
if err != 0: phead(msg=' ** WARNING ** above', pre='[_X_] ' )
phead(msg='Cleaning up'.format(**conf))
#err = call('rm {user}.key {user}.crt {user}.csr'.format(**conf), shell=True)
phead(msg='Creating roles in {namespace}'.format(**conf))
phead()
err = call('kubectl apply -f role-developers-all.yaml -n {namespace}'.format(**conf), shell=True)
if err != 0: phead(msg=' ** WARNING ** above', pre='[_X_] ' )
phead(msg='Adding {user} to role developers-all'.format(**conf))
phead()
err = call('kubectl create rolebinding {user}-developer --role developers-all --user {user} --namespace {namespace}'.format(**conf), shell=True)
if err != 0: phead(msg=' ** WARNING ** above', pre='[_X_] ' )
phead()
err = call('kubectl create clusterrolebinding {user}-node-reader --clusterrole node-reader --user {user} --namespace {namespace}'.format(**conf), shell=True)
if err != 0: phead(msg=' ** WARNING ** above', pre='[_X_] ' )
print('=======================================================================')
phead(msg='--> Need to copy config_{user} to /home/{user}/.kube/config and set the permissions'.format(**conf))
print('\n')
err=call('sudo cp config_{user} /home/{user}/.kube/config'.format(**conf),shell=True)

