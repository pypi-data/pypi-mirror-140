###############################################################################
# (c) Copyright 2018-2022 CERN                                                #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import argparse
import os
import pipes
import platform
import re
import sys
from pathlib import Path

import packaging.version

VERISON_PATTERN = re.compile(
    r"(prod(?:.py3)?|v\d+.\d+.\d+(a\d+)?\-x86_64|v\d+.\d+.\d+(a\d+)?)"
)
LHCB_ETC = Path("/cvmfs/lhcb.cern.ch/etc/grid-security")
ENV_VAR_WHITELIST = [
    # General unix
    r"CUDA_.*",
    r"DISPLAY",
    r"EDITOR",
    r"GIT_SSH.*",
    r"HOME",
    r"HOSTNAME",
    r"https?_proxy",
    r"KRB5.*",
    r"LANG",
    r"LC_.*",
    r"SSH_.*",
    r"TERM",
    r"TMPDIR",
    r"TZ",
    r"USER",
    r"VISUAL",
    # HEP specific
    r"VOMS_.*",
    r"X509_.*",
    r"XRD_.*",
    # LHCb specific
    r"MYSITEROOT",
]
ENV_VAR_WHITELIST = re.compile(r"^(" + r"|".join(ENV_VAR_WHITELIST) + r")$")
OLD_VERSION_RE = re.compile(
    r"^v(?P<major>\d+)r(?P<minor>\d+)(?:p(?P<patch>\d+))?(?:-pre(?P<pre>\d+))?$"
)
PROD_INSTALL_ROOT = Path("/cvmfs/lhcb.cern.ch/lhcbdirac/")
DEV_INSTALL_ROOT = Path("/cvmfs/lhcbdev.cern.ch/lhcbdirac/")


def sort_versions(versions):
    parsedVersions = {}
    for version in versions:
        match = OLD_VERSION_RE.match(version)
        if match:
            # Python 2 based versions are no longer supported
            continue
        # Try Python 3 style versions
        try:
            v = packaging.version.Version(version.split("-")[0])
        except Exception:
            continue
        parsedVersions[version] = (
            v.major,
            v.minor,
            v.micro,
            v.pre[1] if v.is_prerelease else sys.maxsize,
            False,
        )

    return sorted(parsedVersions, key=parsedVersions.get, reverse=True)


class DIRACCVMFSInstall:
    def __init__(self, install_roots=None):
        if install_roots is None:
            try:
                install_roots = [Path(os.environ["DIRAC_INSTALL_ROOT"])]
            except KeyError:
                install_roots = [PROD_INSTALL_ROOT, DEV_INSTALL_ROOT]
        elif isinstance(install_roots, (Path, str)):
            install_roots = [Path(install_roots)]
        self._install_roots = install_roots
        self._versions = self._find_versions()

    @property
    def versions(self):
        return self._versions

    def _find_versions(self):
        versions = {}
        for install_root in self._install_roots:
            if not install_root.is_dir():
                continue
            legacy_versions = {}
            for version in filter(VERISON_PATTERN.match, os.listdir(install_root)):
                # Skip versions that have already been found from a preferred location
                if version in versions:
                    continue
                dirac_path = install_root / version
                bashrc = install_root / "bashrc.py3"
                if version == "prod":
                    versions[version] = dirac_path, bashrc
                elif "." not in version:
                    continue
                elif "-" in version:
                    # This is for the old layout and these should be removed
                    # This is a Python 3 style version
                    version, arch = version.split("-")
                    if version in versions:
                        continue
                    # Remove -$arch from the end of the dirac_path
                    dirac_path = dirac_path.parent / dirac_path.name[: -len(arch) - 1]
                    legacy_versions[version] = dirac_path, bashrc
                else:
                    versions[version] = dirac_path, bashrc
            versions = {**legacy_versions, **versions}
        return versions

    def call(self, command, version="prod"):
        """Replace the current process with a command in the LHCbDirac environment

        If the command is successfully executed this function will never return.
        """
        dirac_path, bashrc = self.versions[version]

        if dirac_path.is_file():
            with open(dirac_path, encoding="utf-8") as fp:
                version = fp.read().strip()
            dirac_path, bashrc = self.versions[version]

        env = {k: v for k, v in os.environ.items() if ENV_VAR_WHITELIST.match(k)}
        if "." in version or version == "prod":
            new_dirac_path = dirac_path / f"{platform.system()}-{platform.machine()}"
            if new_dirac_path.is_dir():
                dirac_path = new_dirac_path
            else:
                # Legacy style versions need the architecture adding
                dirac_path = (
                    dirac_path.parent / f"{dirac_path.name}-{platform.machine()}"
                )
        env["DIRAC"] = dirac_path
        env["BASH_ENV"] = bashrc
        env["PS1"] = "(LHCbDIRAC " + version + ")$ "
        if LHCB_ETC.is_dir():
            env["VOMS_USERCONF"] = env.get("VOMS_USERCONF", LHCB_ETC / "vomses")
            env["X509_CERT_DIR"] = env.get("X509_CERT_DIR", LHCB_ETC / "certificates")
            env["X509_VOMS_DIR"] = env.get("X509_VOMS_DIR", LHCB_ETC / "vomsdir")
            env["X509_VOMSES"] = env.get("X509_VOMSES", LHCB_ETC / "vomses")

        if Path(command[0]).name == "bash":
            exec_command = "source $BASH_ENV; exec bash --norc --noprofile"
            for c in command[1:]:
                exec_command += " " + pipes.quote(c)
        elif Path(command[0]).name in ["sh", "ksh", "csh", "tcsh", "zsh", "fish"]:
            raise NotImplementedError(
                f"Unable to launch {command[0]} as only bash is supported by LHCbDIRAC"
            )
        else:
            exec_command = " ".join(pipes.quote(x) for x in command)

        sys.stdout.flush()
        sys.stderr.flush()
        os.execvpe("bash", ["bash", "--norc", "--noprofile", "-c", exec_command], env)


def lb_dirac():
    """Invoke a commands in the correct environment"""
    parser = argparse.ArgumentParser(
        usage="lb-dirac [-h] [--list] [version] [command] ...",
        description="Run a command in the LHCbDIRAC environment",
    )
    parser.add_argument("--list", action="store_true", help="List available versions")
    # argparse doesn't support optional positional arguments so use metavar to
    # set the help text
    positional_help_text = (
        "version  optional, the version of LHCbDIRAC to use (default: prod)\n  "
        "command  optional, the command to run (default: bash)\n  "
        "...      optional, any additional arguments"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--prod-only",
        dest="install_root",
        action="store_const",
        const=PROD_INSTALL_ROOT,
        help=f"Only consider versions in {PROD_INSTALL_ROOT}",
    )
    group.add_argument(
        "--dev-only",
        dest="install_root",
        action="store_const",
        const=DEV_INSTALL_ROOT,
        help=f"Only consider versions in {DEV_INSTALL_ROOT}",
    )
    parser.add_argument(
        "command",
        metavar=positional_help_text,
        default=["bash"],
        nargs=argparse.REMAINDER,
    )
    args = parser.parse_args()

    dirac_install = DIRACCVMFSInstall(install_roots=args.install_root)

    # Handle --list
    if args.list:
        print(*sort_versions(dirac_install.versions), sep="\n")
        sys.exit(0)

    # Parse the version/command positional arguments
    if args.command and args.command[0] in dirac_install.versions:
        command = args.command[1:]
        version = args.command[0]
    else:
        command = args.command
        version = "prod"
    command = command or ["bash"]

    # Try to replace the current process with the desired command
    try:
        dirac_install.call(command, version)
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)


def lhcb_proxy_init():
    """Invoke lhcb-proxy-init in the correct environment"""
    dirac_install = DIRACCVMFSInstall()
    # We just ignore the first argument...
    return dirac_install.call(["lhcb-proxy-init"] + sys.argv[1:])


def lhcb_proxy_info():
    """Invoke lhcb-proxy-init in the correct environment"""
    dirac_install = DIRACCVMFSInstall()
    # We just ignore the first argument...
    return dirac_install.call(["dirac-proxy-info"] + sys.argv[1:])
