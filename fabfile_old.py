#coding: utf-8
#!/usr/bin/python
from fabric_deploy import options
from fabfile import *

env.hosts = ['120.194.14.9'] 
env.user = 'openerp_newline'
env.password = 'openerp'

current_module = 'custom_purchase'
options.set('scm', 'git')
#设置当前要更新的
options.set('application', current_module)
options.set('repository', "https://github.com/chengdh/%(module_name)s.git" % current_module)

@task
def development():
  options.set('current_stage', 'development')
  env.roledefs.update({'app': [ 'alpha' ] })

@task
def production():
  options.set('current_stage', 'production')
  env.roledefs.update({ 'app': [ 'zulu' ] })
