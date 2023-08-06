# coding=utf-8
# Copyright (c) 2012,2022 Structured Abstraction Inc.
#
# See LICENSE for licensing details.
"""
Baste provides extensions for fabric [1].

Baste allows you to tack together a development stack with simple components in
preparation for development.

[1] - https://docs.fabfile.org/en/2.6/getting-started.html

"""
from abc import ABCMeta, abstractmethod

import datetime
import os
import os.path
import string
import random

from collections import OrderedDict

from invoke import Context
from fabric import Connection
from blessings import Terminal
from patchwork.transfers import rsync

import contextlib
import os

__all__ = [
    'blue',
    'confirm',
    'DiffCommand',
    'Git',
    'green',
    'modified_environ',
    'MysqlLoadGzip',
    'MysqlLoadPlain',
    'OrderedDict',
    'PgLoadPlain',
    'PgRestore',
    'PgShell',
    'project_relative',
    'python_dependency',
    'red',
    'Repository',
    'RsyncDeployment',
    'RsyncMedia',
    'StatusCommand',
]

t = Terminal()

#-------------------------------------------------------------------------------
def pushd() -> str:
    return "pushd > /dev/null"

#-------------------------------------------------------------------------------
def popd() -> str:
    return "popd > /dev/null"

#-------------------------------------------------------------------------------
def green(txt: str) -> str:
    return f'{t.green}{txt}{t.normal}'

#-------------------------------------------------------------------------------
def red(txt: str) -> str:
    return f'{t.red}{txt}{t.normal}'

#-------------------------------------------------------------------------------
def blue(txt: str) -> str:
    return f'{t.blue}{txt}{t.normal}'

#-------------------------------------------------------------------------------
def yellow(txt: str) -> str:
    return f'{t.yellow}{txt}{t.normal}'

#-------------------------------------------------------------------------------
def project_relative(c: Context, path):
    return os.path.join(os.path.dirname(c.cwd), path)

#-------------------------------------------------------------------------------
def confirm(msg: str) -> bool:
    val = input(f"{msg} (y/N): ")
    return val.lower() in ["yes", "y", "ye"]

#-------------------------------------------------------------------------------
@contextlib.contextmanager
def modified_environ(*remove, **update):
    """
    Temporarily updates the ``os.environ`` dictionary in-place.

    The ``os.environ`` dictionary is updated in-place so that the modification
    is sure to work in all situations.

    :param remove: Environment variables to remove.
    :param update: Dictionary of environment variables and values to add/update.
    """
    env = os.environ
    update = update or {}
    remove = remove or []

    # List of environment variables being updated or removed.
    stomped = (set(update.keys()) | set(remove)) & set(env.keys())
    # Environment variables and values to restore on exit.
    update_after = {k: env[k] for k in stomped}
    # Environment variables and values to remove on exit.
    remove_after = frozenset(k for k in update if k not in env)

    try:
        env.update(update)
        [env.pop(k, None) for k in remove]
        yield
    finally:
        env.update(update_after)
        [env.pop(k) for k in remove_after]

#-------------------------------------------------------------------------------
class Repository(metaclass=ABCMeta):
    """
    Generic base repository which knows how to construct a safe update command.
    """

    #---------------------------------------------------------------------------
    @abstractmethod
    def status_command(self, c: Context) -> str: pass

    #---------------------------------------------------------------------------
    @abstractmethod
    def update_command(self, c: Context) -> str: pass

    #---------------------------------------------------------------------------
    @abstractmethod
    def create_command(self, c: Context) -> str: pass

    #---------------------------------------------------------------------------
    def __init__(self, name, url):
        """Instantiate the repository with the given name and url"""
        self.name = name
        self.url = url

    def directory(self, c: Context):
        return project_relative(c, self.name)

    #---------------------------------------------------------------------------
    def status(self, c: Context, hide=False):
        return c.run(self.status_command(c), hide=hide)

    #---------------------------------------------------------------------------
    def update(self, c: Context, hide=False):
        print(green("[update] ") + self.name)
        cmd = f"test -d {self.directory(c)} && {self.update_command(c)} || {self.create_command(c)}"
        c.run(cmd, hide=hide)

#-------------------------------------------------------------------------------
class RepositoryMismatch(RuntimeError):
    """
    Indicates that the repository that is being updated is of a different type.
    """

#-------------------------------------------------------------------------------
class Git(Repository):
    """Represents a Git repository."""

    #---------------------------------------------------------------------------
    def __init__(self, name, url, branch=None, tag=None):
        self.name = name
        self.url = url
        self.branch = branch
        if not tag and not branch:
            self.branch = 'master'
        self.tag = tag
        if self.tag and self.branch:
            raise RuntimeError("Can't specify both a branch and a tag!!")

    #---------------------------------------------------------------------------
    def create_command(self, c: Context) -> str:
        dir = self.directory(c)
        if self.tag:
            return f"git clone {self.url} {dir} && {pushd()} {dir}; git checkout {self.tag} && {popd()}"
        else:
            return f"git clone {self.url} {dir} && {pushd()} {dir}; git checkout {self.branch} && {popd()}"

    #---------------------------------------------------------------------------
    def update_command(self, c: Context) -> str:
        if self.tag:
            return f"{pushd()} {self.directory(c)} && git checkout {self.tag} && {popd()}"
        else:
            return f"{pushd()} {self.directory(c)} && git checkout {self.branch} && git fetch origin && git pull origin {self.branch} && {popd()}"

    #---------------------------------------------------------------------------
    def status_command(self, c: Context) -> str:
        return f"{pushd()} {self.directory(c)} && git status && {popd()}"

    #---------------------------------------------------------------------------
    def diff_command(self, c: Context):
        return f"{pushd()} {self.directory(c)} && git diff && {popd()}"

#-------------------------------------------------------------------------------
def python_dependency(c: Context, package: str, dir: str=None):
    """Adds the given package as a dependency for the given python version."""

    # Figure out the directory we'll be symlinking to.
    if dir is None:
        base_dir = project_relative(c, package)
        if os.path.exists(os.path.join(base_dir, "__init__.py")):
            dir = os.path.join(base_dir, '..')
        elif os.path.exists(os.path.join(base_dir, package, "__init__.py")):
            dir = base_dir
        elif os.path.exists(os.path.join(base_dir, 'src', package, "__init__.py")):
            dir = os.path.join(base_dir, 'src')

    from distutils.sysconfig import get_python_lib
    pth_file = "%s/%s.pth" % (get_python_lib(), package)
    pth_file = project_relative(c, pth_file)
    python_path = dir
    create_pth_file = "echo \"%s\" > %s" % (python_path, pth_file)
    print(green("[install] ") + package)
    c.run(f"rm {pth_file}; {create_pth_file}")

#-------------------------------------------------------------------------------
class StatusCommand(object):
    """Helper which prints the status for all of the repos given to it."""

    #---------------------------------------------------------------------------
    def __init__(self, repos):
        self.repos = repos

    #---------------------------------------------------------------------------
    def __call__(self, c: Context):
        """
        Prints the status for each of the repositories.
        """
        for repo in self.repos.values():
            print(green(f"[status] {repo.name}"))
            repo.status(c)

#-------------------------------------------------------------------------------
class DiffCommand(object):
    """Helper which prints the diff for all of the repos given to it."""

    #---------------------------------------------------------------------------
    def __init__(self, repos):
        self.repos = repos

    #---------------------------------------------------------------------------
    def __call__(self, c: Context, hide: bool = False):
        """
        Prints the status for each of the repositories.
        """
        commands = []
        for repo in self.repos.values():
            commands.append(repo.diff_command())
        c.run("{ %s; } | less" % (" && ".join(commands)), hide=hide)

#-------------------------------------------------------------------------------
class PgRestore(object):
    #---------------------------------------------------------------------------
    def __init__(self, file, db, user, format="custom"):
        self.file = file
        self.db = db
        self.user = user
        self.format = format

    #---------------------------------------------------------------------------
    def __call__(self, c: Context):
        """
        Uses the pg_restore command to restore the database from the given file.
        """
        c.run(
            "pg_restore --clean --no-owner --no-privileges --format=%s --host=localhost --username=%s --dbname=%s %s" % (
                self.format, self.user, self.db, self.file
            )
        )

#-------------------------------------------------------------------------------
class PgLoadPlain(object):
    #---------------------------------------------------------------------------
    def __init__(self, file, db, user):
        self.file = file
        self.db = db
        self.user = user

    #---------------------------------------------------------------------------
    def __call__(self, c: Context):
        """Uses psql to load a plain dump format"""
        c.run(
            "bzcat %s | psql --host=localhost --username=%s --dbname=%s" % (
                self.file, self.user, self.db
            )
        )

#-------------------------------------------------------------------------------
class PgShell(object):
    #---------------------------------------------------------------------------
    def __init__(self, db, user):
        self.db = db
        self.user = user

    #---------------------------------------------------------------------------
    def __call__(self, c: Context):
        """
        Uses the psql command to give someone a shell within the db.
        """
        c.run("psql --host=localhost --username=%s %s" % (self.user, self.db))

#-------------------------------------------------------------------------------
class MysqlLoadPlain(object):
    #---------------------------------------------------------------------------
    def __init__(self, file, db, user, password=None):
        self.file = file
        self.db = db
        self.user = user
        self.password = password

    #---------------------------------------------------------------------------
    def __call__(self, c: Context):
        """Uses mysql command line client to load a plain dump format."""
        if not self.password:
            c.run(
                "mysql -h localhost -u %s -p %s < %s" % (self.user, self.db, self.file)
            )
        else:
            c.run(
                "mysql -h localhost -u %s -p%s %s < %s" % (self.user, self.password, self.db, self.file)
            )

#-------------------------------------------------------------------------------
class MysqlLoadGzip(object):
    #---------------------------------------------------------------------------
    def __init__(self, file, db, user, password=None):
        self.file = file
        self.db = db
        self.user = user
        self.password = password

    #---------------------------------------------------------------------------
    def __call__(self, c: Context):
        """Uses mysql command line client to load a plain dump format."""
        if not self.password:
            c.run(
                "gunzip --stdout %s | mysql -h localhost -u %s -p %s" % (self.file, self.user, self.db)
            )
        else:
            c.run(
                "gunzip --stdout %s | mysql -h localhost -u %s -p%s %s" % (self.file, self.user, self.password, self.db)
            )

#-------------------------------------------------------------------------------
class MysqlLoadBz2(object):
    def __init__(self, file, db, user, password=None):
        self.file = file
        self.db = db
        self.user = user
        self.password = password

    #---------------------------------------------------------------------------
    def __call__(self, c: Context):
        """Uses psql to load a plain dump format"""
        if not self.password:
            c.run(
                "bzcat %s | mysql -h localhost -u %s -p %s" % (self.file, self.user, self.db)
            )
        else:
            c.run(
                "bzcat %s | mysql -h localhost -u %s -p%s %s" % (self.file, self.user, self.password, self.db)
            )

#-------------------------------------------------------------------------------
class RsyncMedia(object):
    #---------------------------------------------------------------------------
    def __init__(self, host, remote_directory, local_directory):
        self.host = host
        self.local_directory = local_directory
        self.remote_directory = remote_directory

    #---------------------------------------------------------------------------
    def __call__(self, c: Context):
        """
        Uses the psql command to give someone a shell within the db.
        """
        c.run(
            "rsync --progress -avz --exclude=\".svn/*\" --exclude=\".svn\" -e ssh %s:%s %s" % (self.host, self.remote_directory, self.local_directory)
        )

REPO_EXCLUDES = [
    '.svn', '.git', '.hg', '.hgignore', 'requirements.txt', 'start.sh',
    'fabfile.py', '*.pyc', 'env', '*.swp', '.venv', 'env'
]

#-------------------------------------------------------------------------------
class RsyncDeployment(object):
    """
    An rsync deployment consists of the following steps:
        1. the local_directory is rsync'ed to the remote_directory/source
        2. an cp command will be run that cps remote_directory/source to
           remote_directory/<current_date_time>
        3. a remote command is run to symlink remote_directory/current to
           remote_directory/<current_date_time>
        4. It is then up to the caller to run the command to reload the server

    Please note that this command WILL delete files on the remote_director/source
    """
    #---------------------------------------------------------------------------
    def __init__(self, remote_directory, local_directory):
        self.remote_directory = remote_directory
        self.local_directory = local_directory

    #---------------------------------------------------------------------------
    def __call__(self, c: Connection, exclude=[]):
        """
        Actually perform the deployment.
        """

        exclude += REPO_EXCLUDES

        target_directory = os.path.join(self.remote_directory, "source")
        previous_directory = os.path.join(self.remote_directory, "previous")
        tmp_previous = os.path.join(self.remote_directory, "previous_tmp")
        current_symlink = os.path.join(self.remote_directory, "current")
        tmp_symlink = os.path.join(self.remote_directory, "current_tmp")
        date_directory = os.path.join(
                self.remote_directory,
                datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S")
            )
        c.run("mkdir -p %s" % target_directory)
        c.run("mkdir -p %s" % previous_directory)
        c.run("rm -rf %s" % (tmp_previous,))
        c.run("mv -Tf %s %s" % (previous_directory, tmp_previous))

        # only if the current directly exists can we copy it to the previous directory.
        if c.run("ls -1 %s | grep current | cat" % self.remote_directory):
            c.run("cp -rH %s %s" % (current_symlink, previous_directory))

        rsync(
            c,
            source=self.local_directory,
            target=target_directory,
            exclude=exclude,
            delete=True,
        )
        c.run("cp -r %s %s" % (target_directory, date_directory))
        c.run("ln -sf %s %s; mv -Tf %s %s" % (date_directory, tmp_symlink, tmp_symlink, current_symlink))
        c.run("rm -rf %s" % tmp_previous)

#-------------------------------------------------------------------------------
class UbuntuPgCreateDbAndUser(object):
    #---------------------------------------------------------------------------
    def __init__(
        self,
        db_name,
        db_user,
        source_template=None,
        create_role=True,
        as_user='postgres'
    ):
        self.db_name = db_name
        self.db_user = db_user
        self.source_template = source_template
        self.as_user = as_user
        self.create_role = create_role

    #---------------------------------------------------------------------------
    def __call__(self, c: Context):
        if not self.as_user:
            local_run = lambda command, warn: c.run(command, warn=warn)
        else:
            local_run = lambda command, warn: c.sudo(command, user=self.as_user, warn=warn)

        local_run("dropdb {}".format(self.db_name), warn=True)

        if self.create_role:
            local_run("dropuser {}".format(self.db_user), warn=True)
            local_run("createuser --createdb --pwprompt --no-superuser --no-createrole {}".format(self.db_user), warn=False)
        if not self.source_template:
            local_run("createdb -O {} {}".format(self.db_user, self.db_name), warn=False)
        else:
            local_run("createdb -T {} -O {} {}".format(self.source_template, self.db_user, self.db_name), warn=False)

#-------------------------------------------------------------------------------
class UbuntuMysqlCreateDbAndUser(object):
    #---------------------------------------------------------------------------
    def __init__(self, db_name, db_user, db_password):
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password

    #---------------------------------------------------------------------------
    def __call__(self, c: Context):
        # Drop the db
        sql = "DROP DATABASE IF EXISTS %(db)s; "
        sql = sql % { 'db': self.db_name, }
        command = "echo \"%s\" | mysql -p -u root" % (sql,)
        c.run(command)

        # Re create it.
        sql = "CREATE DATABASE %(db)s; " + \
            "GRANT ALL ON %(db)s.* to %(user)s@localhost IDENTIFIED BY '%(pw)s';"
        sql = sql % {
                'db': self.db_name,
                'user': self.db_user,
                'pw': self.db_password,
            }

        command = "echo \"%s\" | mysql -p -u root" % (sql,)
        c.run(command)


#-------------------------------------------------------------------------------
def pay_attention_confirm(question, yes=None):
    """Ask a user a question, require a unique answer for confirmation."""

    if yes is None:
        yes = ''.join([random.choice(string.ascii_letters) for _ in range(3)])
        yes = yes.lower()

    response = input(f'{question} [ y("{yes}") / n ]: ')
    if response == yes:
        return True
    return False


#-------------------------------------------------------------------------------
def local_changes(c: Context, repos):
    changes = []
    for repo in repos:
        new_changes = repo.status(c, hide=True).stdout
        if isinstance(repo, Git):
            ignored_lines = [
                'nothing to commit (working directory clean)',
                'nothing to commit, working directory clean',
                '# On branch master\n',
                'nothing to commit, working tree clean',
                'On branch master',
                'On branch main',
                'Your branch is up to date with \'origin/master\'.',
                'Your branch is up to date with \'origin/main\'.',
            ]
            for line in ignored_lines:
                new_changes = new_changes.replace(line, '')
            new_changes = "\n".join([
                line for line in new_changes.split("\n")
                if not "HEAD detached at " in line and not "Refresh index:" in line
            ])

        new_changes = new_changes.strip()
        if new_changes:
            changes.append(new_changes)

    return changes

