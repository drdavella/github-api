#!/usr/bin/env python3
import sys
from argparse import ArgumentParser, FileType
from graphql import GithubRepo


def flatten(array):
    return [x for inner in array for x in inner]


def main():

    p = ArgumentParser(description='Retrieves commit ids associated with a '
                       'specific milestone on github')
    p.add_argument('org', type=str, help='Organization that owns GitHub repository')
    p.add_argument('name', type=str, help='Name of GitHub repository')
    p.add_argument('milestone', type=str, help='Name of milestone')
    key_args = p.add_mutually_exclusive_group(required=True)
    key_args.add_argument('-k', '--key', type=str, help='GitHub API key')
    key_args.add_argument('-f', '--key-file', type=FileType(),
                          help='File containing GitHub API key')
    p.add_argument('-o', '--outfile', type=FileType('w'), default=sys.stdout,
                   help='Output file. Defaults to stdout')
    args = p.parse_args()

    if args.key:
        api_key = args.key
    else:
        api_key = args.key_file.read().strip()

    gh = GithubRepo(args.org, args.name, api_key)
    milestone_id = gh.get_milestone_id(args.milestone)
    if milestone_id < 0:
        sys.stderr.write("No milestone named '{}' found in {}/{}\n".format(
            args.milestone, args.org, args.name))
        return 1

    commits = flatten(reversed(gh.get_milestone_commits(milestone_id)))
    args.outfile.write('\n'.join(commits))
    args.outfile.write('\n')


if __name__ == '__main__':
    sys.exit(main())
