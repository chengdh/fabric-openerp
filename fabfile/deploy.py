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
def linode():
  options.set('current_stage', 'production')
  env.roledefs.update({'app': ['ssapp.co']})
  env.roledefs.update({'web': ['ssapp.co']})

#部署openobject-addons
@task
def addons():
  application = 'openobject-addons'
  options.set('local_project_path','/Users/chengdh/myproject/openerp7.0/openobject-addons')
  options.set('application', applicatioin)
  options.set('deploy_to','~/openerp/%s' % application )

#部署openerp-web
@task
def addons():
  application = 'openerp-web'
  options.set('application', applicatioin)
  options.set('local_project_path','/Users/chengdh/myproject/openerp7.0/openerp-web')
  options.set('deploy_to','~/openerp/%s' % application )

@task
def server():
  application = 'openobject-server'
  options.set('application', applicatioin)
  options.set('local_project_path','/Users/chengdh/myproject/openerp7.0/openobject-server')
  options.set('deploy_to','~/openerp/%s' % application )

#部署custom_addons/:module
@task
def custom_addons():
  #目前的自定义模块
  #html_report,custom_purchase,custom_hr_payroll,custom_stock,member_management,ktv_sale_refactor

  #deploy_module = 'html_report'
  #deploy_module = 'custom_purchase'
  #deploy_module = 'custom_stock'

  deploy_module = 'ktv_sale'

  options.set('scm', 'git')
  options.set('deploy_via','checkout')
  #设置当前要更新的module
  options.set('application', deploy_module)
  options.set('repository', "https://github.com/chengdh/%s.git" % deploy_module)
  options.set('deploy_to','~/openerp/custom_addons/%s' % deploy_module)
  #设置user和runner
  options.set('user','openerp')
  options.set('runner','openerp')

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
  options.set('application', applicatioin)
