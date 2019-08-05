#!/usr/bin/env python3
# coding: utf-8
'''
Author: Park Lam <lqmonline@gmail.com>
Copyright: Copyright 2019, unipark.io
'''
import os
import re
import requests
import json
from decouple import config
from zipfile import ZipFile
from io import BytesIO

PACKAGE_NAME = 'pychromedriver'
PACKAGE_URL = 'https://test.pypi.org/pypi/pychromedriver/json' \
        if config('DEBUG', default=False, cast=bool) \
        else 'https://pypi.org/pypi/pychromedriver/json'

CHROMEDRIVER_URL = 'https://chromedriver.storage.googleapis.com/'
OS_TYPES = [ 'win', 'mac', 'linux' ]
ARCHITECTURE = [ '32', '64' ]
FILE_NAME = 'chromedriver_'
FILE_EXT = '.zip'

DOWNLOAD_DIR = './pychromedriver/'
VERSION_FILE = './VERSION.txt'

def compare_version(alpha, beta):
    alpha_arr = alpha.split('.')
    beta_arr = beta.split('.')

    while alpha_arr and beta_arr:
        m = int(alpha_arr.pop(0))
        n = int(beta_arr.pop(0))
        if m > n:
            return 1
        elif m < n:
            return -1

    while alpha_arr:
        m = int(alpha_arr.pop(0))
        if m > 0:
            return 1

    while beta_arr:
        n = int(beta_arr.pop(0))
        if n > 0:
            return -1
    return 0

def get_pip_version():
    page = requests.get(PACKAGE_URL)
    return json.loads(page.text)['info']['version']

def get_next_version(prev_version):
    version_lst = get_chromedriver_versions()
    while version_lst:
        next_version = version_lst.pop(0)
        if compare_version(prev_version, next_version) == -1:
            return next_version
    return None

def get_chromedriver_versions():
    import lxml.etree as et
    version_lst = []
    ver_regex = r'(\w+\.?)*/chromedriver_(win32|linux32|mac32|linux64|mac64).\w{3}'

    cont = requests.get(CHROMEDRIVER_URL).text
    doc = et.fromstring(cont.encode('utf8'))
    ns = { 's3': doc.xpath('namespace-uri(.)') }
    for node in doc.xpath('//s3:Contents', namespaces=ns):
        info = node.xpath('./s3:Key', namespaces=ns)[0]
        result = re.match(ver_regex, info.text)
        if result:
            version, _ = info.text.split('/')
            if version not in version_lst:
                version_lst.append(version)
    return version_lst

def download_chromedriver(version):
    import lxml.etree as et
    cont = requests.get(CHROMEDRIVER_URL).text
    doc = et.fromstring(cont.encode('utf8'))
    ns = { 's3': doc.xpath('namespace-uri(.)') }
    ver_regex = r'%s/chromedriver_(win32|linux32|mac32|linux64|mac64).\w{3}' % version
    for node in doc.xpath('//s3:Contents/s3:Key', namespaces=ns):
        if re.match(ver_regex, node.text):
            url = os.path.join(CHROMEDRIVER_URL, node.text)
            print("Download file: ", url)
            filename = node.text.split('/').pop().split('.').pop(0)
            if 'win32' in filename:
                filename += '.exe'
            zf = ZipFile(BytesIO(requests.get(url).content))
            for f in zf.namelist():
                zf.extract(f, DOWNLOAD_DIR)
                os.rename(os.path.join(DOWNLOAD_DIR, f), \
                        os.path.join(DOWNLOAD_DIR, filename))


if __name__ == '__main__':
    version = os.environ.get('VERSION')
    force_upload = False

    if version:
        force_upload = True

    if not force_upload:
        pip_version = get_pip_version()
        print('Current PyPI version:', pip_version)

        version = get_next_version(pip_version)
        print('Version to update:', version)
        if not version:
            print('Latest version.')
            exit(1)

        download_chromedriver(version)
        with open(VERSION_FILE, 'w') as f:
            f.write(version)
    else:
        download_chromedriver(version)
        with open(VERSION_FILE, 'w') as f:
            f.write(version)
