"""Tests for the gittools module (pytest)."""


import gittools
from pathlib import Path


basepath = Path(gittools.__file__).parent / '..'


def test_cch():
    """Test current_commit_hash()"""
    cch = gittools.current_commit_hash(checkdirty=False)
    assert type(cch) is str


def test_pst():
    """Test path_status()"""
    pst = gittools.path_status()
    assert type(pst['hash']) is str


def test_mst():
    """Test module_status()"""
    mst = gittools.module_status(gittools)
    assert type(mst['gittools']['hash']) is str


def test_smd():
    """Test save_metadata()"""
    param = {'test': 'test', 'other': 33}
    file = basepath / 'tests' / 'metadata_file_test.json'
    gittools.save_metadata(file, info=param, module=gittools,
                           dirty_warning=True, notag_warning=True)
    assert file.exists()


def test_tags():
    """Test repo_tags()"""
    tags = gittools.repo_tags()
    assert len(tags) > 0
