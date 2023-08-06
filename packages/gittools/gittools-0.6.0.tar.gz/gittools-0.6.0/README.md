# About

Tools for getting information about git repositories in python, based on *gitpython*; *gittools* provides functions to get quick commit information of paths / files:
- `current_commit_hash()` (return *str* of latest commit)
- `path_status()` (return *dict* with more info, e.g. tags, dirty or not, etc.)

There are also functions targeted for use on python modules that are within a git repository (e.g. following editable install from git clone):
- `module_status()`: similar to *path_status()* but with python module(s) as an input instead of a path
- `save_metadata()`: save git information and any other metadata provided as input into a JSON file.

Other functions include `repo_tags()` and `path_in_tree()` (see below).

See docstrings and information below for more details.


# Install

```bash
pip install gittools
```

# Contents

See help / docstrings of functions for details, and **Examples** section below.

## General functions

```python
current_commit_hash(path='.', checkdirty=True, checktree=True)
```
commit hash (str) of HEAD commit of repository where path belongs; if True, `checkdirty` and `checktree` raise exceptions if repo is dirty and if path does not belong to repo's tree, respectively.

```python
path_status(path='.')
```
Similar to `current_commit_hash()` but does not raise exceptions. Instead, returns git status (commit hash, dirty or clean, tag if there is one) as a dictionary.


## Functions for python modules

```python
module_status(module, dirty_warning=False, dirty_ok=True, notag_warning=False, nogit_ok=False, nogit_warning=False)
```
Version of `path_status()` adapted for python modules (module can be a single module or a list/iterable of modules). Data is returned as a dict of dicts where the keys are module names and the nested dicts correspond to dicts returned by `path_status()`.

There is a `nogit_ok` option to avoid raising an error if one or several modules are not in a git repository. In this case, the returned information of the module indicates that the module is not in a git repo and uses the module version number as a tag.

Other options are to print warnings when:
- the repo is dirty, i.e. uncommitted (`dirty_warning`),
- it is missing a tag at the current commit (`notag_warning`),
- one or more modules are not in a git repo (`nogit_warning`).

If `dirty_ok` is set to False, a `DirtyRepo` exception is thrown if the module(s) have a dirty repository.


```python
save_metadata(file, info=None, module=None, dirty_warning=False, dirty_ok=True, notag_warning=False, nogit_ok=False, nogit_warning=False):
```
Save metadata (`infos` dictionary), current time, and git module info. The `module`, `dirty_warning`, `notag_warning`, `nogit_ok` and `nogit_warning` parameters are the same as for `module_status()`.


## Miscellaneous functions


- `repo_tags(path='.')`: lists all tags in repository the path belongs to, as a {'commit hash': 'tag name'} dictionary (both keys and values are strings).

- `path_in_tree(path, commit)`: used by *current_commit_hash*; returns True if path belongs to the commit's working tree (or is the root directory of repo), else False.


Exceptions
----------

The `checkdirty` and `checktree` options raise custom exceptions: `DirtyRepo` and `NotInTree`, respectively.


# Examples

```python
>>> from gittools import current_commit_hash, repo_tags

>>> current_commit_hash()  # Most recent commit of the current working directory
'1f37588eb5aadf802274fae74bc4abb77d9d8004'

# Other possibilities
>>> current_commit_hash(checkdirty=False) # same, but avoid raising DirtyRepo
>>> current_commit_hash('gitrepos/repo1/foo.py') # same, but specify path/file

# Note that the previous example will raise an exception if the file is not
# tracked in a git repository. To silence the exception and see the most
# recent commit hash of the closest git repository in a parent directory:
>>> current_commit_hash('Test/untracked_file.pyc', checktree=False)

# List all tags of repo:
>>> repo_tags()  # current directory, but also possible to specify path
{'1f37588eb5aadf802274fae74bc4abb77d9d8004': 'v1.1.8',
 'b5173941c9cceebb786b0c046c67ea505786d820': 'v1.1.9'}
```

It can be easier to use higher level functions to get hash name, clean/dirty status, and tag (if it exists):
```python
>>> from gittools import path_status, module_status

>>> path_status()  # current working directory (also possible to specify path)
{'hash': '1f37588eb5aadf802274fae74bc4abb77d9d8004',
 'status': 'clean',
 'tag': 'v1.1.8'}

>>> import mypackage1  # module with clean repo and tag at current commit
>>> module_status(mypackage1)
{'mypackage1': {'hash': '1f37588eb5aadf802274fae74bc4abb77d9d8004',
                'status': 'clean',
                'tag': 'v1.1.8'}}

>>> import mypackage2  # this package has uncommitted changes and no tags
>>> module_status(mypackage2, dirty_warning=True)
Warning: the following modules have dirty git repositories: mypackage2
{'mypackage2': {'hash': '8a0305e6c4e7a57ad7befee703c4905aa15eab23',
                'status': 'dirty'}}

>>> module_status([mypackage1, mypackage2]) # list of modules
{'mypackage1': {'hash': '1f37588eb5aadf802274fae74bc4abb77d9d8004',
                'status': 'clean',
                'tag': 'v1.1.8'},
 'mypackage2': {'hash': '8a0305e6c4e7a57ad7befee703c4905aa15eab23',
                'status': 'dirty'}}

# mypackage3 not a git repo
>>> module_status([mypackage1, mypackage2, mypackage3], nogit_ok=True)
{'mypackage1': {'hash': '1f37588eb5aadf802274fae74bc4abb77d9d8004',
                'status': 'clean',
                'tag': 'v1.1.8'},
 'mypackage2': {'hash': '8a0305e6c4e7a57ad7befee703c4905aa15eab23',
                'status': 'dirty'},
 'mypackage3': {'status': 'not a git repository',
                'tag': 'v1.3.2'}}
```

Save metadata with current time and git info (from `module_status()`)
```python
>>> import gittools, oclock, numpy
>>> from gittools import save_metadata
>>> modules = gittools, aquasol
>>> parameters = {'temperature': 25, 'pressure': 2338}
>>> save_metadata('metadata.json', info=parameters, module=modules, nogit_ok=True)

# Writes a .json file with the following info:
{
    "temperature": 25,
    "pressure": 2338,
    "time (utc)": "2020-12-03 21:33:17",
    "code version": {
        "gittools": {
            "hash": "12f2ceb3c5fffcc31e422474485e2481890a8094",
            "status": "dirty",
            "tag": "v0.3.1"
        },
        "oclock": {
            "hash": "826aa76e5096680805eb43fb22a80ccc3b282015",
            "status": "clean",
            "tag": "v1.0.1"
        }
        "numpy": {
            "status": "not a git repository",
            "tag": "v1.19.2"
        }
    }
}
```


# Requirements / dependencies

### Python

- Python >= 3.6

### Python packages

(installed automatically by pip if necessary)

- gitpython (https://gitpython.readthedocs.io)
- importlib-metadata

### Other

- git (see gitpython requirements for git minimal version)


# Author

Olivier Vincent (ovinc.py@gmail.com)

# License

3-Clause BSD (see *LICENSE* file)
