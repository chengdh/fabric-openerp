#coding: utf-8
from __future__ import with_statement
from datetime import datetime
from fabric.contrib.files import upload_template, exists
from mako.template import Template
from fabric.operations import *
import os

from time import sleep
from fabric import colors
from fabric.api import task, env, run, cd
from fabric.utils import abort, puts
from fabric.context_managers import hide

from fabric_deploy import options
from fabric_deploy.deploy import *

'''
env.hosts = ['120.194.14.9'] 
env.user = 'openerp_newline'
env.password = 'openerp'
'''

current_module = 'custom_purchase'
options.set('scm', 'git')
#设置当前要更新的module
options.set('application', current_module)
options.set('repository', "https://github.com/chengdh/%s.git" % current_module)
options.set('deploy_to','~/addons/')
#设置user和runner
options.set('user','openerp_newline')
options.set('runner','openerp_newline')

@task
def development():
  options.set('current_stage', 'development')
  env.roledefs.update({'app': ['120.194.14.9' ] })
  env.roledefs.update({'web': ['120.194.14.9' ] })

@task
def production():
  options.set('current_stage', 'production')
  env.roledefs.update({'app': ['120.194.14.9' ] })
  env.roledefs.update({'web': ['120.194.14.9' ] })
