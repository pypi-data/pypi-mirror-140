from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import input
from uuid import getnode as get_mac

import sys
import os
import webbrowser
import logging

from requests import ConnectionError

import p1
from p1.colors import *
from p1.utils import cprint, data2json, _assert
from p1.jsonfile import JsonFile

def main():
    try:
        sitename = sys.argv[2] if len(sys.argv) > 2 else '_DEFAULT'
        login(sitename)
    except Exception as e:
        cprint(LRED, "ops!")
        raise e


def login_old(sitename):
    """login in site"""
    assert False, "login_old is deprecated"

    # fetch site urls
    site = p1.get_site(sitename)
    _assert(site is not None, "Site %s not found in config.yaml" % sitename)

    login_url = site.login_url()
    token_url = site.token_url()
    _assert(login_url, "Site %s has no login url" % site.name)
    _assert(token_url, "Site %s has no token url" % site.name)

    # open login url to user
    cprint(LGREEN, "Obtenha um código em: %s" % login_url)
    webbrowser.open(login_url)
    code = input(LCYAN + "Code? " + RESET)

    # exchange code for token
    cprint(RESET, "Validadando o código: %s" % code)

    try:
        response = site.post(token_url, data={"code": code})
        _assert(response.ok, "Login failed")
    except ConnectionError:
        _assert(False, "Connection failed... check your internet connection")

    response.encoding = 'utf-8'
    try:
        token = response.json()
    except ValueError:
        _assert(False, "Server didn't send json")

    # save token
    tokens = JsonFile(os.path.expanduser('~/.p1/tokens.json'))
    tokens[site.name] = token['p1_token']
    tokens.writable = True
    tokens.save()

    msg = "Logged in %s as %s" % (site.name, token['email'])
    cprint(LGREEN, msg)
    logging.info(msg)


def login(sitename):
    """login in site"""

    # fetch site urls
    site = p1.get_site(sitename)
    _assert(site is not None, "Site %s not found in config.yaml" % sitename)

    # check site login style
    api_login_url = site.api_login_url()
    old_login_url = site.login_url();
    _assert(api_login_url or old_login_url, "Site %s has no login url" % site.name)

    # possibly switch to old style login function
    if not api_login_url and old_login_url:
        return login_old(sitename)

    # perform cli tools login; fetch auth and acces urls and login token
    response = site.post(api_login_url, {"mac": str(get_mac())})
    response.encoding = 'utf-8'
    user_auth_url = response.json()['user-auth-url']
    api_access_url = response.json()['api-access-url']

    # open browser at authorization page
    cprint(LCYAN, f"Abrir o browser para authorizar o login? (S/n) ", end="")
    if input() in "Ss":
        if webbrowser.open(user_auth_url):
            print(f"Aguardando autorização via browser…")
        else:
            cprint(LRED, "Ops! Não foi possível abrir o browser.")
            cprint(WHITE, "Use o link abaixo para logar:")
            cprint(YELLOW, user_auth_url)
    else:
        cprint(WHITE, "Ok. Use o link abaixo para logar:")
        cprint(YELLOW, user_auth_url)

    # request access code
    for i in range(10):
        response = site.get(f'{api_access_url}')
        if response.status_code == 500:
            cprint(LRED, "O login falhou (timeout)")
            cprint(LGREEN, "Tente novamente...")
            #sys.exit(1)
            continue
        authorization = response.json()
        if response.status_code == 200: break

    # check authorization
    if 'authorized' not in authorization:
        cprint(LRED, 'Login não autorizado')
        logging.info('Login não autorizado')
        sys.exit(1)

    # check whether the login worked
    if not 'tst_token' in authorization:
        cprint(LRED, 'O login falhou (não autorizado)')
        logging.info('tst_token não encontrado na resposta')
        return

    # save token
    tokens = JsonFile(os.path.expanduser('~/.p1/tokens.json'))
    tokens[site.name] = authorization['tst_token']
    tokens.writable = True
    tokens.save()

    msg = f"Você está logado no site de p1 como {YELLOW}{authorization['email']}{RESET}"
    cprint(LGREEN, msg)
    logging.info(msg)
