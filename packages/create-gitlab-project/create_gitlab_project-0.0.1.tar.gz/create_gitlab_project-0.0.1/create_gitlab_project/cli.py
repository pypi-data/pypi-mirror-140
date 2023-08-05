import argparse
import logging
import os
import sys

from create_gitlab_project import create_gitlab_project_dfx

logger = logging.getLogger("dfx-create-gitlab-project")


def main():
    parser = argparse.ArgumentParser(prog='create-gitlab-project',
                                     description='Creates a Gitlab project with given arguments.')

    parser.add_argument('--url',
                        type=str,
                        metavar='URL',
                        help='GitLab Repository URL',
                        default=os.environ.get("GITLAB_PROJECT_URL", "https://gitlab.com"))
    parser.add_argument('-t', '--token',
                        type=str,
                        metavar="Access Token",
                        help="GitLab Access Token",
                        required=True)
    parser.add_argument('--group_id',
                        type=int,
                        help="Group ID to where the new project will be created",
                        required=True)
    parser.add_argument('--pipeline_type',
                        type=str,
                        help="Pipeline type (shared-lib/vars)",
                        choices=['containerPipeline', 'libraryPipeline'],
                        required=True)
    parser.add_argument('--project_type',
                        type=str,
                        help="Project type (library or container-app)",
                        choices=['maven-image', 'maven-library'],
                        required=True)
    parser.add_argument('--app_name',
                        type=str,
                        help="Applications name",
                        required=True)
    parser.add_argument('--namespace',
                        type=str,
                        help="Kubernetes namespace to deploy",
                        choices=['security'],
                        required=True)

    args = parser.parse_args()

    print("Gitlab project creation started with below arguments:")
    print(args)

    try:
        create_gitlab_project_dfx.init(args)
    except:
        logger.exception("create gitlab project failed")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
