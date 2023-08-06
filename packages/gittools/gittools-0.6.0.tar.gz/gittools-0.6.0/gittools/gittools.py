"""Git tools for Python."""

from pathlib import Path, PurePosixPath
from datetime import datetime
import json
from copy import copy

import importlib_metadata
from git import Repo, InvalidGitRepositoryError

# ============================ Custom exceptions =============================


class DirtyRepo(Exception):
    """Specific exception indicating some changes in repo are not committed."""
    pass


class NotInTree(Exception):
    """Specific exception indicating file is not in commit tree."""
    pass


# =========================== Private subroutines ============================


def _pathify(path):
    """Transforms str or partial path in fully resolved path object."""
    pathabs = Path(path).resolve()  # absolute path of filename
    if not pathabs.exists():
        raise FileNotFoundError(f'Path {pathabs} does not exist')
    return pathabs


def _make_iterable(x):
    """Transforms non-iterables into a tuple, but keeps iterables unchanged."""
    try:
        iter(x)
    except TypeError:
        return x,
    else:
        return x


# ============================= Public functions =============================


def path_in_tree(path, commit):
    """Return True if path belongs to the commit's working tree, else False.

    Note that if the path is the root directory of the git repository (where
    the .git is located), the function also returns True even if one could
    argue that the root directory is technically not in the repo's tree.

    INPUTS
    ------
    - path: str or path object of folder or file
    - commit: *gitpython* commit object

    OUTPUT
    ------
    bool (True if path is in working tree, False if not)
    """

    pathabs = _pathify(path)
    rootabs = Path(commit.repo.working_dir).resolve()  # path of root of repo

    localpath = pathabs.relative_to(rootabs)  # relative path of file in repo
    localname = str(PurePosixPath(localpath))  # gitpython uses Unix names

    if localname == '.':  # Means that the entered path is the repo's root
        return True

    try:
        commit.tree[localname]
    except KeyError:  # in this case the file is not in the commit
        return False
    else:
        return True


def current_commit_hash(path='.', checkdirty=True, checktree=True):
    """Return HEAD commit hash corresponding to path if it's in a git repo.

    INPUT
    -----
    - path: str or path object of folder/file. Default: current working dir.
    - checkdirty: bool, if True exception raised if repo has uncommitted changes.
    - checktree: bool, if True exception raised if path/file not in repo's
    working tree and path is not the root directory of the repo.

    OUTPUT
    ------
    - str of the commit's hash name.
    """
    p = _pathify(path)
    repo = Repo(p, search_parent_directories=True)

    if checkdirty and repo.is_dirty():
        raise DirtyRepo("Dirty repo, please commit recent changes first.")

    commit = repo.head.commit

    if checktree and not path_in_tree(path, commit):
        raise NotInTree("Path or file not in working tree.")

    return str(commit)


def repo_tags(path='.'):
    """Return dict of all {'commit hash': 'tag name'} in git repo.

    INPUT
    -----
    - path: str or path object of folder/file. Default: current working dir.

    OUTPUT
    ------
    dict  {'commit hash': 'tag name'} (both key and value are str).
    """
    p = _pathify(path)
    repo = Repo(p, search_parent_directories=True)

    return {str(tag.commit): str(tag) for tag in repo.tags}


def path_status(path='.'):
    """Current (HEAD) commit hashes, status (dirty or clean), and potential tag.

    Slightly higher level compared to current_commit_hash, as it returns a
    dictionary with a variety of information (status, hash, tag)

    INPUT
    -----
    - path: str or path object of folder/file. Default: current working dir.

    OUTPUT
    ------
    Dictionary keys 'hash', 'status' (clean/diry), 'tag' (if exists)
    """
    info = {}

    # get commit hash and check repo status (dirty or clean) -----------------
    try:
        cch = current_commit_hash(path, checkdirty=True)
    except DirtyRepo:
        cch = current_commit_hash(path, checkdirty=False)
        status = 'dirty'
    else:
        status = 'clean'

    info['hash'] = cch
    info['status'] = status

    # check if tag associated with commit ------------------------------------
    commits_with_tags = repo_tags(path)
    if cch in commits_with_tags:
        info['tag'] = commits_with_tags[cch]

    return info


# ================== Functions for status of python modules ==================


def module_status(module,
                  dirty_warning=False,
                  dirty_ok=True,
                  notag_warning=False,
                  nogit_ok=False,
                  nogit_warning=False):
    """Get status info (current hash, dirty/clean repo, tag) of module(s).

    Parameters
    ----------
    - module or list/iterable of modules (each must belong to a git repository)
    - dirty_warning: if True, prints a warning if some git repos are dirty.
    - dirty_ok: if False, raise an error if module(s) is/are dirty.
    - notag_warning: if True, prints a warning if some git repos don't have tags
    - nogit_ok: if True, if some modules are not in a git repo, simply get
      their version number. If False (default), raise an error.
    - nogit_warning: if some modules are not in a git repo and nogit_ok is True,
      print a warning when this happens.

    Output
    ------
    Dict with module name as keys, and a dict {hash:, status:, tag:} as values
    """
    modules = _make_iterable(module)
    mods = {}  # dict {module name: dict of module info}

    for module in modules:

        name = module.__name__

        try:
            info = path_status(module.__file__)
        except InvalidGitRepositoryError:
            if nogit_ok:

                try:
                    version = module.__version__
                except AttributeError:
                    version = importlib_metadata.version(name)

                tag = 'v' + version
                info = {'status': 'not a git repository',
                        'tag': tag}

            else:
                raise InvalidGitRepositoryError(f'{module} not a git repo')
        mods[name] = info

    # Manage warnings if necessary -------------------------------------------

    if dirty_warning or not dirty_ok:

        dirty_modules = [module for module, info in mods.items()
                         if info['status'] == 'dirty']

        if len(dirty_modules) > 0:

            msg = 'These modules have dirty git repositories: '
            msg += ', '.join(dirty_modules)

            if not dirty_ok:
                raise DirtyRepo(msg)
            else:
                print(f'\nWarning: {msg}\n')

    if notag_warning:

        tagless_modules = [module for module, info in mods.items()
                           if 'tag' not in info]

        if len(tagless_modules) > 0:
            msg = '\nWarning: these modules are missing a tag: '
            msg += ', '.join(tagless_modules)
            print(f'{msg}\n')

    if nogit_ok and nogit_warning:

        nogit_modules = [module for module, info in mods.items()
                         if info['status'] == 'not a git repository']

        if len(nogit_modules) > 0:
            msg = '\nWarning: these modules are not in a git repository: '
            msg += ', '.join(nogit_modules)
            print(f'{msg}\n')

    return mods


def save_metadata(file,
                  info=None,
                  module=None,
                  dirty_warning=False,
                  dirty_ok=True,
                  notag_warning=False,
                  nogit_ok=False,
                  nogit_warning=False):
    """Save metadata (info dict) into json file, and add git commit & time info.

    Parameters
    ----------
    - file: str or path object of .json file to save data into.
    - info: dict of info
    - module: module or iterable (e.g. list) of modules with git info to save.
    - dirty_warning: if True, prints a warning if some git repos are dirty.
    - dirty_ok: if False, raise an error if module(s) is/are dirty.
    - notag_warning: if True, prints a warning if some git repos don't have tags
    - nogit_ok: if True, if some modules are not in a git repo, simply get
      their version number. If False (default), raise an error.
    - nogit_warning: if some modules are not in a git repo and nogit_ok is True,
      print a warning when this happens.
    """
    metadata = copy(info) if info is not None else {}
    metadata['time (utc)'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    # Info on commit hashes of homemade modules used -------------------------
    if module is not None:
        module_info = module_status(module,
                                    dirty_warning=dirty_warning,
                                    dirty_ok=dirty_ok,
                                    notag_warning=notag_warning,
                                    nogit_ok=nogit_ok,
                                    nogit_warning=nogit_warning)

        metadata['code version'] = module_info

    # Write to file ----------------------------------------------------------
    # Note: below, the encoding and ensure_ascii options are for signs like °
    with open(file, 'w', encoding='utf8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
