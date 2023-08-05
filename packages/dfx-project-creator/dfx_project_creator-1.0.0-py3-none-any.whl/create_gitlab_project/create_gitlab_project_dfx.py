#!/usr/bin/env python3
import gitlab
import re

from create_gitlab_project import constants

import os


def get_gitlab_object(url, token):
    gl = gitlab.Gitlab(url=url, private_token=token)
    gl.auth()
    return gl


def init(args):
    # Get files directory in order to use template files
    constants.DIR_NAME = os.path.dirname(__file__)

    # Get gl object
    gl = get_gitlab_object(args.url, args.token)

    # Create project
    # group_id = gl.groups.list(search='<group-name>')[0].id
    project = gl.projects.create({'name': args.app_name, 'namespace_id': args.group_id})
    project_id = project.id

    # Read template files
    jenkinsfile = open(constants.DIR_NAME + constants.JENKINSFILE_PATH).read()
    readme = open(constants.DIR_NAME + constants.README_PATH).read()

    # Create initial commit
    #   prepare Jenkinsfile
    for name, pattern in constants.JENKINSFILE_REPLACEMENT_ITEMS.items():
        replacement = args.__getattribute__(name)
        jenkinsfile = jenkinsfile.replace(pattern, replacement)

    data = {
        'branch': 'main',
        'commit_message': 'Initial Commit',
        'actions': [
            {
                'action': 'create',
                'file_path': 'README.md',
                'content': readme,
            },
            {
                'action': 'create',
                'file_path': 'iac/Jenkinsfile',
                'content': jenkinsfile,
            },
            {
                'action': 'create',
                'file_path': 'iac/Dockerfile'
            },
            {
                'action': 'create',
                'file_path': 'iac/deployment.yml'
            }
        ]
    }

    commit = project.commits.create(data)

    # Create develop branch
    branch = project.branches.create({'branch': 'develop', 'ref': 'main'})

    # Make develop branch to default branch
    project.default_branch = "develop"
    project.save()

    # Create branch protections
    #   firstly delete default protection (there is no update branch protection, we should delete the default and recreate it)
    project.protectedbranches.delete('main')

    main_branch = project.protectedbranches.create({
        'name': 'main',
        'push_access_level': gitlab.const.NO_ACCESS
    })

    develop_branch = project.protectedbranches.create({
        'name': 'develop',
        'merge_access_level': gitlab.const.DEVELOPER_ACCESS,
        'push_access_level': gitlab.const.NO_ACCESS
    })

    # Print repository url in order to use it in second step (create jenkins multibranch pipeline)
    print(project_id)

    return 0
