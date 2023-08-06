###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import os
import random
import subprocess

import pytest

from LbDiracWrappers import DIRACCVMFSInstall, sort_versions


def test_versions(require_cvmfs_lhcb):
    lhcbdirac_versions = DIRACCVMFSInstall().versions
    assert len(lhcbdirac_versions) > 10
    assert "prod" in lhcbdirac_versions


def test_version_sort():
    example_input = [
        "v10.4.8",
        "v10r2",
        "v10.2.1",
        "v10.2.0-x86_64",
        "v10r2-pre9",
        "v10r2-pre8",
        "v10.2.0a8-x86_64",
        "v10r2-pre7",
        "v10r1p1",
        "v10r1",
        "v10r1-pre8",
        "v10r1-pre7",
    ]
    shuffled = example_input[:] + ["prod"]
    expected = [x for x in example_input if "v10r2" not in x and "v10r1" not in x]
    random.shuffle(shuffled)
    actual = sort_versions(shuffled)
    assert shuffled != expected
    assert actual == expected


def test_lhcb_proxy_info(require_cvmfs_lhcb):
    stdout, stderr = check_output(["lhcb-proxy-info", "--help"])
    assert "Usage:" in stdout
    assert "dirac-proxy-info" in stdout


def test_lhcb_proxy_init(require_cvmfs_lhcb):
    stdout, stderr = check_output(["lhcb-proxy-init", "--help"])
    assert "Usage:" in stdout
    assert "dirac-proxy-init" in stdout


@pytest.mark.parametrize(
    "cmd",
    [
        ["--list"],
        ["--list", "bash"],
        ["--list", "exit", "100"],
    ],
)
def test_lb_dirac_list(cmd, require_cvmfs_lhcb):
    stdout, stderr = check_output(["lb-dirac"] + cmd)
    assert "x86_64" not in stdout
    assert "aarch64" not in stdout
    assert "ppc64le" not in stdout
    lhcbdirac_versions = DIRACCVMFSInstall().versions
    for version in lhcbdirac_versions:
        if version.startswith("prod"):
            assert version not in stdout
        else:
            assert version in stdout


def test_lb_dirac_echo_list(require_cvmfs_lhcb):
    stdout, stderr = check_output(["lb-dirac", "echo", "--list"])
    assert stdout.strip() == "--list"


def test_lb_dirac_command(require_cvmfs_lhcb):
    stdout, stderr = check_output(["lb-dirac", "env"])
    assert "DIRAC=" in stdout

    stdout, stderr = check_output(["lb-dirac", "prod", "env"])
    assert "DIRAC=" in stdout

    version = get_random_version()
    stdout, stderr = check_output(["lb-dirac", version, "env"])
    assert "DIRAC=" in stdout
    assert "/" + version in stdout

    # Try a specific Python 3 version
    version = "v10.2.0a8"
    stdout, stderr = check_output(["lb-dirac", version, "env"])
    assert "DIRAC=" in stdout
    assert "/" + version in stdout


def test_lb_dirac_shells(require_cvmfs_lhcb):
    stdout, stderr = check_output(["lb-dirac", "bash", "-c", "env"])
    assert "DIRAC=" in stdout

    stdout, stderr = check_output(["lb-dirac", "sh", "-c", "env"], rc=1)
    assert "ERROR" in stderr

    stdout, stderr = check_output(["lb-dirac", "zsh", "-c", "env"], rc=1)
    assert "ERROR" in stderr

    stdout, stderr = check_output(["lb-dirac", "ksh", "-c", "env"], rc=1)
    assert "ERROR" in stderr

    stdout, stderr = check_output(["lb-dirac", "csh", "-c", "env"], rc=1)
    assert "ERROR" in stderr

    stdout, stderr = check_output(["lb-dirac", "tcsh", "-c", "env"], rc=1)
    assert "ERROR" in stderr

    stdout, stderr = check_output(["lb-dirac", "fish", "-c", "env"], rc=1)
    assert "ERROR" in stderr


def test_lb_dirac_interactive(require_cvmfs_lhcb):
    stdout, stderr = check_output(["lb-dirac", "bash"], write_stdin="env")
    assert "DIRAC=" in stdout

    stdout, stderr = check_output(["lb-dirac", "prod"], write_stdin="env")
    assert "DIRAC=" in stdout

    stdout, stderr = check_output(
        ["lb-dirac", "prod.py3"], write_stdin="python --version"
    )
    assert "Python 3." in stdout

    version = get_random_version()
    stdout, stderr = check_output(["lb-dirac", version], write_stdin="env")
    assert "DIRAC=" in stdout
    assert "/" + version in stdout


def test_install_locations(require_cvmfs_lhcb, require_cvmfs_lhcbdev):
    stdout, stderr = check_output(["lb-dirac", "env"])
    assert "DIRAC=/cvmfs/lhcb.cern.ch" in stdout

    version = get_random_version(path="/cvmfs/lhcb.cern.ch")
    stdout, stderr = check_output(["lb-dirac", version, "env"])
    assert "DIRAC=/cvmfs/lhcb.cern.ch" in stdout

    stdout, stderr = check_output(["lb-dirac", "prod.py3", "python", "--version"])
    assert "Python 3." in stdout

    version = get_random_version(path="/cvmfs/lhcbdev.cern.ch")
    stdout, stderr = check_output(["lb-dirac", version, "env"])
    assert "DIRAC=/cvmfs/lhcbdev.cern.ch" in stdout


def test_lhcbprod_priority(monkeypatch, require_cvmfs_lhcb, require_cvmfs_lhcbdev):
    stdout, stderr = check_output(["lb-dirac", "v10.2.1", "env"])
    assert "DIRAC=/cvmfs/lhcb.cern.ch/lhcbdirac/v10.2.1-x86_64" in stdout

    stdout, stderr = check_output(["lb-dirac", "--prod-only", "v10.2.1", "env"])
    assert "DIRAC=/cvmfs/lhcb.cern.ch/lhcbdirac/v10.2.1-x86_64" in stdout

    stdout, stderr = check_output(["lb-dirac", "--dev-only", "v10.2.1", "env"])
    assert "DIRAC=/cvmfs/lhcbdev.cern.ch/lhcbdirac/v10.2.1-x86_64" in stdout

    monkeypatch.setenv("DIRAC_INSTALL_ROOT", "/cvmfs/lhcb.cern.ch/lhcbdirac")
    stdout, stderr = check_output(["lb-dirac", "v10.2.1", "env"])
    assert "DIRAC=/cvmfs/lhcb.cern.ch/lhcbdirac/v10.2.1-x86_64" in stdout

    monkeypatch.setenv("DIRAC_INSTALL_ROOT", "/cvmfs/lhcbdev.cern.ch/lhcbdirac")
    stdout, stderr = check_output(["lb-dirac", "v10.2.1", "env"])
    assert "DIRAC=/cvmfs/lhcbdev.cern.ch/lhcbdirac/v10.2.1-x86_64" in stdout


def test_install_root_override(monkeypatch, require_cvmfs_lhcb, require_cvmfs_lhcbdev):
    stdout, stderr = check_output(["lb-dirac", "env"])
    assert "DIRAC=/cvmfs/lhcb.cern.ch/lhcbdirac/" in stdout

    stdout, stderr = check_output(["lb-dirac", "--prod-only", "env"])
    assert "DIRAC=/cvmfs/lhcb.cern.ch/lhcbdirac/" in stdout

    stdout, stderr = check_output(["lb-dirac", "--dev-only", "env"])
    assert "DIRAC=/cvmfs/lhcbdev.cern.ch/lhcbdirac/" in stdout

    monkeypatch.setenv("DIRAC_INSTALL_ROOT", "/cvmfs/lhcb.cern.ch/lhcbdirac")
    stdout, stderr = check_output(["lb-dirac", "env"])
    assert "DIRAC=/cvmfs/lhcb.cern.ch/lhcbdirac/" in stdout

    monkeypatch.setenv("DIRAC_INSTALL_ROOT", "/cvmfs/lhcbdev.cern.ch/lhcbdirac")
    stdout, stderr = check_output(["lb-dirac", "env"])
    assert "DIRAC=/cvmfs/lhcbdev.cern.ch/lhcbdirac/" in stdout


@pytest.fixture
def require_cvmfs_lhcb():
    assert os.listdir("/cvmfs/lhcb.cern.ch")


@pytest.fixture
def require_cvmfs_lhcbdev():
    assert os.listdir("/cvmfs/lhcbdev.cern.ch")


def check_output(cmd, rc=0, write_stdin=None):
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        universal_newlines=True,
    )
    stdout, stderr = proc.communicate(input=write_stdin)
    assert proc.returncode == rc
    return stdout, stderr


def get_random_version(path=""):
    ver_to_path = DIRACCVMFSInstall().versions
    # Try with a random version
    versions = list(ver_to_path)
    versions.pop(versions.index("prod"))
    random.shuffle(versions)
    for version in versions:
        dirac_path = ver_to_path[version][0]
        if path in str(dirac_path) and not dirac_path.is_file():
            print("Running tests with", version)
            return version
    raise ValueError(f"Failed to find a version with {path} in the path")
