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
import fabric_gunicorn as gunicorn

env.hosts = ['www.nt999.net:2222'] 
env.user = 'openerp'
env.password = 'openerp'

OPENERP_HOME="/home/openerp/openerp7"
env.remote_workdir = "%s/openobject-server/" % OPENERP_HOME
env.gunicorn_wsgi_app = "openerp:service.wsgi_server.application"
env.gunicorn_bind = "0.0.0.0:8069"
env.gunicorn_workers = 4
env.errorlog = '%s/logs/gunicorn-error.log' % OPENERP_HOME
env.accesslog = '%s/logs/gunicorn-access.log' % OPENERP_HOME
env.loglevel = 'debug'
env.timout = 5000
#添加了openerp conf file
env.openerp_conf = 'newtime-wsgi.py'
#使用了virtualenv
env.virtualenv_dir = "OPENERP"

@task
def start_openerp_server():
  '''
  启动openerp server
  重写fabric_gunicorn中的start
  '''
  gunicorn.set_env_defaults()

  if gunicorn.gunicorn_running():
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


    if 'openerp_conf' in env:
      options.append('-c %s%s' % (env.remote_workdir,env.openerp_conf))

    options_string = ' '.join(options)

    if 'paster_config_file' in env:
      run('%s gunicorn_paster %s %s' % (prefix_string, options_string,env.paster_config_file))
    else:
      run('%s gunicorn %s %s' % (prefix_string, options_string,env.gunicorn_wsgi_app))

    if gunicorn.gunicorn_running():
      puts(colors.green("Gunicorn started."))
    else:
      abort(colors.red("Gunicorn wasn't started!"))

gunicorn.start = start_openerp_server
