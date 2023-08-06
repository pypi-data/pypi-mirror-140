import sys
import os

from urllib.parse import urlparse

import p1
from p1.colors import *
from p1.utils import cprint
from p1.utils import indent
from p1.utils import print_hints
from p1.utils import _assert
from p1.utils import is_posix_filename
from p1.utils import data2json
from p1.jsonfile import JsonFile

def main():
    assert sys.argv[0].endswith('p1') and sys.argv[1] == 'checkout'

    # parse user arguments
    args = sys.argv[2:]
    site, key, target_dir, overwrite = process_args(args)

    checkout(site, key, target_dir, overwrite)


def syntax_help():
    return LRED + "This is not a p1 directory.\n" + RESET +\
           "Usage: p1 checkout <key>[@<site>] [<directory>]\n"\
           "       p1 checkout <url> [<directory>]\n\n"\
           "   or: p1 checkout\n"\
           "       (inside a p1 directory)"\


def process_args(args):
    _assert(0 <= len(args) <= 3, syntax_help())

    # process overwrite argument
    YES = ["--yes", "-y"]
    overwrite = any(yes in args for yes in YES)
    args = [e for e in args if e not in YES]

    # add default args
    if len(args) == 0:
        ## no args: use current directory
        cwd = os.getcwd()
        _assert(p1.dirtype(cwd) == "assignment", f"error: no activity in {cwd}")
        args.append(os.path.basename(cwd))
        args.append(".")

    elif len(args) == 1 and os.path.isdir(args[0]):
        ## single directory as arg: make sure is a checkout
        checkout_file = args[0] + "/.p1/assignment.json"
        _assert(os.path.exists(checkout_file), "Directory %s has no checkout info\n%sTry: p1 checkout key <new-directory>" % (args[0], RESET))
        p1_object = JsonFile(checkout_file)
        _assert("key" in p1_object, "Checkout corrupted: missing key")
        _assert("site" in p1_object, "Checkout corrupted: missing site")
        args = ["%s@%s" % (p1_object["key"], p1_object["site"]), args[0]]

    data = { "destdir": args[1] if len(args) > 1 else None }

    key_or_url = args[0]
    url = urlparse(key_or_url)
    _assert(not url.fragment, "Fragments not supported in url")
    _assert(not url.username, "Usernames not supported in url")
    _assert(not url.password, "Passwords not supported in url")

    if url.scheme == 'http':
        # key_or_url == "http://.../key"
        path, key = url.path.rsplit("/", 1) if "/" in url.path else (url.path, '')
        data["url"] = "%s://%s%s" % (url.scheme, url.netloc, path)
        data["site"] = None
        data["key"] = key

    elif is_posix_filename(key_or_url, extra_chars="@"):
        num_ats = key_or_url.count("@")
        if num_ats == 0:
            # key_or_url == "key"
            data["url"] = None
            data["site"] = "_DEFAULT"
            data["key"] = key_or_url

        elif num_ats == 1:
            # key_or_url == "key@site"
            key, sitename = key_or_url.split("@")
            data["url"] = None
            data["site"] = sitename
            data["key"] = key
    else:
        _assert(False, "Unrecognized key/url")


    # get site based either on sitename or url
    assert data['site'] is None or data['url'] is None
    site = p1.get_site(name=data['site']) if data['site'] else p1.get_site(url=url)
    _assert(site and site.url, "No site/url identified. Check your config.yaml")

    return site, data['key'], data['destdir'], overwrite


def save_file(filename, content, mode):
    def octal_mode(mode):
        return {
            (False , False): 0o444,
            (False ,  True): 0o555,
            (True  , False): 0o644,
            (True  ,  True): 0o755
        }["w" in mode, "x" in mode]

    subdirs = os.path.dirname(filename)
    if not os.path.isdir(subdirs):
        os.makedirs(subdirs)

    with open(filename, encoding="utf-8", mode="w") as f:
        f.write(content)

    os.chmod(filename, octal_mode(mode))


def save_selected_files(savetable):
    for i in range(len(savetable)):
        line = savetable[i]
        if line[2] == 'unchanged':
            savetable[i][3] = 'skipped'
            continue

        try:
            filename = line[1]
            if os.path.exists(filename):
                os.chmod(filename, 0o644)

            mode = line[0].get('mode', '644')
            save_file(filename, line[0]['content'], mode)
            savetable[i][3] = 'saved'

        except (IOError, OSError) as e:
            savetable[i][3] = 'failed'
            assert False, f"CRITICAL ERROR: failed saving file '{line[1]}'"


def get_save_table(files, basedir):
    """
    Return a table that helps saving files to FS.
    Each line of the table has 4 columns:
    - the file itself
    - the filename to be saved to
    - the situation wrt to current FS: notfound, unchanged, changed
    - an empty cell to write the final status after saving
    """
    savetable = []
    for f in files:
        save_name = "%s/%s" % (basedir, f['name'])
        if not os.path.exists(save_name):
            savetable.append([f, save_name, 'notfound', None])
        else:
            # a version of the file already exists
            old_contents = open(save_name, encoding='utf-8').read()
            new_contents = f['content']
            if old_contents == new_contents:
                savetable.append([f, save_name, 'unchanged', None])
            else:
                savetable.append([f, save_name, 'changed', None])

    return savetable


def checkout(site, key, target_dir, overwrite_allowed):
    """checkout activity/assignment from site/collection"""

    def is_valid_dir(dirtype):
        return dirtype in [None, "assignment"]

    # fetch activity
    cprint(LGREEN, "Baixando atividade %s do servidor" % key)
    activity, response = site.get_activity(key)
    if response.status_code == 404:
        activity, response = site.get_directory(key)

    if response.status_code == 401:
        cprint(LRED, 'Checkout não autorizado (%s)' % site.last_response.status_code)
        cprint(WHITE, 'Execute: p1 login')
        return

    elif response.status_code == 404:
        cprint(LRED, 'Atividade não encontrada (%s)' % site.last_response.status_code)
        return

    elif response.status_code in [400, 412]:
        cprint(LRED, 'Checkout não permitido (%s)' % site.last_response.status_code)
        cprint(LRED, 'Problema: %s' % site.last_response.json()['messages'][0])
        return

    _assert(activity, "Não foi possível fazer o checkout (%s)" % response.status_code)

    # prepare hints
    hints = []

    # target_dir can be defined from the server with dirname
    target_dir = target_dir or activity.get('dirname')
    destdir = str(target_dir or next((activity.get(p) for p in ['name', 'id', 'iid'] if activity.get(p)), None) or key)
    if not target_dir:
        hints.append("use p1 checkout <key> <dir> to save activity to directory <dir>")
        while True:
            destdir = input("Type directory name (default '%s'): " % destdir) or destdir
            if is_posix_filename(destdir, extra_chars="/"): break
            cprint(YELLOW, "Nome de arquivo não é posix portável: '%s'" % destdir)

    _assert(not os.path.exists(destdir) or (os.path.isdir(destdir) and is_valid_dir(p1.dirtype(destdir))), "Invalid target directory: %s" % destdir)

    # analyze what must be saved to FS
    savetable = get_save_table(activity['files'], destdir)
    num_to_overwrite = 0
    for line in savetable:
        if line[2] == 'changed':
            num_to_overwrite += 1
            if not overwrite_allowed: cprint(LRED, f"{line[1]}")

    if num_to_overwrite and not overwrite_allowed:
        cprint(YELLOW, "Estes arquivos serão alterados! Confirma? (s/N)? ", end="")
        if input() != "s":
            cprint(YELLOW, 'Checkout cancelado pelo usuário')
            sys.exit(1)

    # save 'notfound' and 'changed' files
    save_selected_files(savetable)
    num_saved = 0
    for line in savetable:
        if line[3] == 'skipped':
            cprint(RESET, f"U {line[1]}")
        elif line[3] == 'saved':
            cprint(LCYAN, f"W {line[1]}")
            num_saved += 1

    cprint(LGREEN, f"{num_saved} arquivo(s) gravados")

    content = data2json({
            "site": site.name,
            "key": key,
            "iid": activity.get('iid'),
            "user": activity.get('user'),
            "dirname": activity.get('dirname'),
            "full_resource": activity['_response'].json() if '_response' in activity else None
        })
    save_file(f'{destdir}/.p1/assignment.json', content, "rw")
    print_hints(hints)
