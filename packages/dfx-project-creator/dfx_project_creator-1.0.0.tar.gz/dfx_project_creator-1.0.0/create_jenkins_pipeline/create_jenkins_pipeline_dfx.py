#!/usr/bin/env python3
import gitlab
import re
import jenkins
import os

from create_jenkins_pipeline import constants


def get_gitlab_object(url, token):
    gl = gitlab.Gitlab(url=url, private_token=token)
    gl.auth()
    return gl


def init(args):
    # Get files directory in order to use template files
    constants.DIR_NAME = os.path.dirname(__file__)

    # Get project information
    gl = get_gitlab_object(args.gitlab_url, args.gitlab_token)
    project = gl.projects.get(args.project_id)

    project_url = project.http_url_to_repo
    project_name = project.path

    # Read multibranch pipeline xml config
    multibranch = open(constants.DIR_NAME + constants.MULTIBRANCH_XML_PATH).read()
    #   another way is to get config from pre-exist job
    # my_job = server.get_job_config('access-control')

    url_with_remote = '<remote>' + project_url + '</remote>'
    multibranch = re.sub('<remote>?(.*?)</remote>', url_with_remote, multibranch, flags=re.DOTALL)

    # Create Jenkins job
    server = jenkins.Jenkins(args.jenkins_url, username=args.jenkins_username, password=args.jenkins_password)
    server.create_job(project_name, multibranch)
    server.disable_job(project_name)

    return 0
