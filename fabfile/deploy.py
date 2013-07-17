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


current_module = 'custom_purchase'
options.set('scm', 'git')
options.set('deploy_via','checkout')
#设置当前要更新的module
options.set('application', current_module)
options.set('repository', "https://github.com/chengdh/%s.git" % current_module)
options.set('deploy_to','~/custom_addons/%s' % current_module)
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

@task
@roles('app')
def restart():
  pass

@task
@roles('app', 'web')
def update_symlink():
  with settings(warn_only=True):
    addons_path = "/home/openerp_newline/openerp7/addons"
    dic =  dict(current_module = current_module,addons_path = addons_path)
    dic.update(var('latest_release'))
    result = run('rm -f %(addons_path)s/%(current_module)s && ln -s %(latest_release)s  %(addons_path)s/%(current_module)s' \
        % dic)

    if result.failed:
      alert('failed to update symlink. try to rollback.')
      invoke('rollback')
