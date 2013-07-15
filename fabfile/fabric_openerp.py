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
