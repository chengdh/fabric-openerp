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

#导入gunicon控制
from fabric_gunicorn import *
"""
env.hosts = ['www.nt999.net:2222'] 
env.user = 'openerp'
env.password = 'openerp'
"""

OPENERP_HOME="/home/openerp/openerp"
env.remote_workdir = "%s/openobject-server/current" % OPENERP_HOME
env.gunicorn_wsgi_app = "openerp:service.wsgi_server.application"
env.gunicorn_bind = "0.0.0.0:8069"
env.gunicorn_workers = 4
env.errorlog = '%s/log/gunicorn-error.log' % env.remote_workdir
env.accesslog = '%s/log/gunicorn-access.log' % env.remote_workdir
env.loglevel = 'debug'
env.timeout = '50000'
#添加了openerp conf file
#使用了virtualenv
env.virtualenv_dir = "%s/openobject-server/shared/virtualenv"% OPENERP_HOME
env.gunicorn_pidpath = "%s/openobject-server/shared/pids/gunicorn.pid"% OPENERP_HOME

@task
def linode():
  env.hosts = ['ssapp.co'] 
  env.user = 'openerp'
  env.password = 'openerp'
  env.openerp_conf = 'linode-wsgi.py'

@task
def nt999():
  env.hosts = ['219.154.46.168:2222'] 
  env.user = 'openerp'
  env.password = 'openerp'
  env.openerp_conf = 'newtime-wsgi.py'

@task
def start_oe():
  '''
  启动openerp server
  重写fabric_gunicorn中的start
  '''
  set_env_defaults()

  if gunicorn_running():
    puts(colors.red("Gunicorn is already running!"))
    return

  if 'gunicorn_wsgi_app' not in env:
    abort(colors.red('env.gunicorn_wsgi_app not defined'))

  with cd(env.remote_workdir):
    prefix = []
    if 'virtualenv_dir' in env:
      prefix.append('source %s/bin/activate' % env.virtualenv_dir)
    if 'django_settings_module' in env:
      prefix.append('export DJANGO_SETTINGS_MODULE=%s' % env.django_settings_module)

    prefix_string = ' && '.join(prefix)
    if len(prefix_string) > 0:
      prefix_string += ' && '

    options = [
        '--daemon',
        '--pid %s' % env.gunicorn_pidpath,
        '--bind %s' % env.gunicorn_bind,
      ]
    if 'gunicorn_workers' in env:
      options.append('--workers %s' % env.gunicorn_workers)

    if 'gunicorn_worker_class' in env:
      options.append('--worker-class %s' % env.gunicorn_worker_class)

    if 'errorlog' in env:
      options.append('--error-logfile %s' % env.errorlog)

    if 'accesslog' in env:
      options.append('--access-logfile %s' % env.accesslog)

    if 'loglevel' in env:
      options.append('--log-level %s' % env.loglevel)

    if 'timeout' in env:
      options.append('--timeout %s' % env.timeout)


    if 'openerp_conf' in env:
      options.append('-c %s' % env.openerp_conf)

    options_string = ' '.join(options)

    if 'paster_config_file' in env:
      run('%s gunicorn_paster %s %s' % (prefix_string, options_string,env.paster_config_file))
    else:
      run('%s gunicorn %s %s' % (prefix_string, options_string,env.gunicorn_wsgi_app))

    if gunicorn_running():
      puts(colors.green("Gunicorn started."))
    else:
      abort(colors.red("Gunicorn wasn't started!"))

start = start_oe
