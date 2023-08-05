import argparse
import logging
import os
import sys

from create_jenkins_pipeline import create_jenkins_pipeline_dfx

logger = logging.getLogger("dfx-create-jenkins-pipeline")


def main():
    parser = argparse.ArgumentParser(prog='create-jenkins-pipeline',
                                     description='Creates a Jenkins Multibranch Pipeline with given arguments.')

    parser.add_argument('--gitlab_url',
                        type=str,
                        metavar='URL',
                        help='GitLab Repository URL',
                        default=os.environ.get("GITLAB_PROJECT_URL", "https://gitlab.com"))
    parser.add_argument('--gitlab_token',
                        type=str,
                        metavar="Access Token",
                        help="GitLab Access Token",
                        required=True)
    parser.add_argument('--project_id',
                        type=int,
                        help="Gitlab project ID",
                        required=True)
    parser.add_argument('--jenkins_url',
                        type=str,
                        metavar='URL',
                        help='Jenkins URL',
                        default=os.environ.get("JENKINS_URL", None))
    parser.add_argument('-u', '--jenkins_username',
                        type=str,
                        help="Jenkins Username",
                        required=True)
    parser.add_argument('-p', '--jenkins_password',
                        type=str,
                        help="Jenkins Password",
                        required=True)

    args = parser.parse_args()

    try:
        create_jenkins_pipeline_dfx.init(args)
    except:
        logger.exception("create jenkins pipeline failed")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
