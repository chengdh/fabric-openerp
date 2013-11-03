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


#目前的自定义模块
#html_report,custom_purchase,custom_hr_payroll,custom_stock,member_management

deploy_module = 'html_report'
options.set('scm', 'git')
options.set('deploy_via','checkout')
#设置当前要更新的module
options.set('application', deploy_module)
options.set('repository', "https://github.com/chengdh/%s.git" % deploy_module)
options.set('deploy_to','~/openerp7/custom_addons/%s' % deploy_module)
#设置user和runner
options.set('user','openerp')
options.set('runner','openerp')

@task
def development():
  options.set('current_stage', 'development')
  env.roledefs.update({'app': ['www.nt999.net:2222' ] })
  env.roledefs.update({'web': ['www.nt999.net:2222' ] })

@task
def production():
  options.set('current_stage', 'production')
  env.roledefs.update({'app': ['www.nt999.net:2222' ] })
  env.roledefs.update({'web': ['www.nt999.net:2222' ] })

@task
@roles('app')
def restart():
  pass

@task
@roles('app', 'web')
def update_symlink():
  with settings(warn_only=True):
    addons_path = "/home/openerp/openerp7/openobject-addons"
    dic =  dict(deploy_module = deploy_module,addons_path = addons_path)
    dic.update(var('latest_release'))
    result = run('rm -f %(addons_path)s/%(deploy_module)s && ln -s %(latest_release)s  %(addons_path)s/%(deploy_module)s' \
        % dic)

    if result.failed:
      alert('failed to update symlink. try to rollback.')
      invoke('rollback')
