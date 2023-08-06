from .base_backend import GitBackend
from subprocess import run
from pathlib import Path
import click
import json
from making_with_code_cli.helpers import cd
from making_with_code_cli.styles import (
    confirm,
)

class GithubBackend(GitBackend):
    """A Github backend. Students own their own repos and grant teachers access via token.
    Note that this gives the teacher account access to the student's entire github account, 
    within scope.
    """

    @classmethod
    def extend_settings(self, settings):
        "Asks for the user's github username and email address"
        def choose_github_username(github_username):
            msg = "What is your GitHub username? "
            return click.prompt(msg, default=github_username)
        def choose_github_email(github_email):
            msg = "What is the email address associated with your GitHub account? "
            return click.prompt(msg, default=github_email)
        def choose_git_name(git_name):
            msg = "What name do you want to use in your git commits? "
            return click.prompt(msg, default=git_name)
        if click.confirm("Do you have a GitHub account?"):
            settings['github_username'] = choose_github_username(settings.get("github_username"))
            settings['github_email'] = choose_github_email(settings.get("github_email"))
            settings['git_name'] = choose_git_name(settings.get("git_name"))
        return settings

    def init_clone(self, module, modpath):
        url = module["repo_url"]
        cmd = f'gh repo clone "{url}" "{modpath.name}"'
        with cd(modpath.parent):
            run(cmd, shell=True, check=True)

    def init_create_from_template(self, module, modpath):
        """Creates the named repo from a template, or clones an existing repo with. 
        """
        repo_name = modpath.name
        if self.user_has_repo(repo_name):
            cmd = f'gh repo clone "{repo_name}" "{modpath.name}"'
        else:
            url = module["repo_url"]
            cmd = f'gh repo create "{repo_name}" --clone --private --template "{url}"'
        with cd(modpath.parent):
            run(cmd, shell=True, check=True)

    def user_has_repo(self, name):
        "Checks to see whether the user already has the named repo."
        cmd = f"gh repo list --json name --limit 10000"
        result = run(cmd, shell=True, capture_output=True, text=True).stdout
        repo_names = [obj['name'] for obj in json.loads(result)]
        return name in repo_names
