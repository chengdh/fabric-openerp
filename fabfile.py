#coding: utf-8
#!/usr/bin/python
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

env.hosts = ['120.194.14.9'] 
env.user = 'openerp_newline'
env.password = 'openerp'


env.prerequisites = ['build-essential',
                    'python-dev',
                    'python-pip',
                    'postgresql',
                    'libldap2-dev',
                    'python-dateutil',
                    'python-docutil',
                    'python-mock',
                    'python-unittest2',
                    'python-feedparser',
                    'python-gdata',   
                    'python-ldap',
                    'python-libxslt1',
                    'python-lxml',
                    'python-mako',
                    'python-openid',
                    'python-psycopg2',
                    'python-pybabel',
                    'python-pychart',
                    'python-pydot',
                    'python-pyparsing',
                    'python-reportlab',
                    'python-simplejson',
                    'python-tz',
                    'python-vatnumber',
                    'python-vobject',
                    'python-webdav',
                    'python-xlwt',
                    'python-yaml',
                    'python-zsi',
                    ]
NOW = datetime.now().strftime("%Y.%m.%d.%H.%M")
DIRS = {
        'OPENERP_HOME': '/home/openerp_newline/openerp7',
        'SOURCE_CODE_BACKUP': '/opt/service/openerp/backup/source_code',
        'DATABASE_BACKUP': '/opt/service/openerp/backup/db',
}

#定义addons路径
ADDONS_PATH  = {
    #本地addons_path
    'local'  : ['/Users/chengdh/myproject/ktv_sale/addons/','/Users/chengdh/myproject/openerp7.0/openerp-web/addons/','/Users/chengdh/myproject/openerp7.0/openobject-addons/'], 
    #服务端的addons_path
    'server' : [DIRS['OPENERP_HOME']+"/addons"], 
    }

#gunicorn相关变量

env.remote_workdir = "%s/openobject-server/" % DIRS['OPENERP_HOME']
env.gunicorn_wsgi_app = "openerp:service.wsgi_server.application"
env.gunicorn_bind = "0.0.0.0:8900"
env.gunicorn_workers = 4
#添加了openerp conf file
env.openerp_conf = 'newtime-wsgi.py'


#上传给定的addon到服务器
def upload_addon(module_name):
  '''
  上传给定的addon到服务器
  '''
  #先创建服务端的addon path
  if not module_name:
    print('you must special a addon module name!')
    return
  server_path = ADDONS_PATH['server'][0]
  run("mkdir -p {0}".format(server_path))
  local_dir = [ the_dir + "/" + module_name for the_dir in ADDONS_PATH['local'] if os.path.isdir(the_dir + "/" + module_name)]
  if local_dir:
    print('upload addon {0} to {1}'.format(module_name,server_path))
    put(local_dir[0],server_path)


def check_installed(package_name):
    """
    Checks package whether installed
    """
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        result = run('dpkg -s {0} | grep "Status: install ok installed"'.format(package_name))
        return result.startswith("Status:")    
        
def apt_install(package_name):
    """
    Install package through apt-get install.
    """
    sudo('apt-get -y install {0}'.format(package_name))
    

def create_openerp_directories():
    sudo('mkdir -p ')
    sudo('mkdir -p ')
    sudo('mkdir -p ')
    #sudo('mkdir ')

@task
def pre_deploy():
    """
    Prepare enviroment before start installing python packages
    """
    for package_name in env.prerequisites:
        if not check_installed(package_name):
            apt_install(package_name)
        else:
            print('{0} already installed, moving on..'.format(package_name))
    sudo('pip install werkzeug')
    #download_openerp()

def pg_setup():
    """usage: fab backup_db:db_name"""
    file_path = "{0}{1}.{2}.sql".format(POSTGRES_HOME,db_name,NOW)
    sudo("pg_dump {0} -f {1}".format(db_name, file_path), user= "postgres")
    sudo("gzip {0}".format(file_path), user= "postgres")
    
@task
def setup_pg_user(username, password, db_name):
    """Adds a user to postgres and creates a database"""
    user_sql = "CREATE USER {0} WITH CREATEDB PASSWORD '{1}';".format(username, password)
    db_sql = "CREATE DATABASE {0} WITH OWNER {1};".format(db_name, username)
    sudo('psql -c "{0}"'.format(user_sql), user= "postgres")
    sudo('psql -c "{0}"'.format(db_sql), user= "postgres")
    pg_hba_conf_path =  "/etc/postgresql/9.1/main/pg_hba.conf"
    sudo('echo "host {0} {1} 127.0.0.1/32 trust" >> {2}'.format(db_name, username, pg_hba_conf_path,user="postgres"))
    sudo("service postgresql restart")

@task
def pg_backup():
    file_path = "{0}{1}.{2}.sql".format(POSTGRES_HOME,db_name,NOW)
    sudo("pg_dump {0} -f {1}".format(db_name, file_path), user= "postgres")
    sudo("gzip {0}".format(file_path), user= "postgres")
    
@task
def update_module(module_name):
  '''
  更新给定的模块
  :param module_name 模块名称
  '''
  upload_addon(module_name)
  gunicorn.reload()

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

