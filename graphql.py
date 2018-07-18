#!/usr/bin/env python3
import requests


API_ENDPOINT = "https://api.github.com/graphql"


class GithubRepo:

    def __init__(self, owner, name, api_key):
        self.owner = owner
        self.name = name
        self.api_key = api_key

    def _run_query(self, query, variables=None):

        json = dict(query=query)
        if variables:
            json['variables'] = variables

        headers = { "Authorization": "bearer {}".format(self.api_key) }
        result = requests.post(API_ENDPOINT, json=json, headers=headers)
        if result.status_code != 200:
            raise RuntimeError("Query failed to run: ", result.message)

        json_data = result.json()
        if 'errors' in json_data:
            msg = '\n'.join([x['message'] for x in json_data['errors']])
            raise RuntimeError("Query failed to run: " + msg)

        return json_data


    def get_label_names(self):
        query = """
        query RepoLabelQuery($owner: String!, $name: String!) {
          repository(owner:$owner, name:$name) {
            labels(last:100) {
              totalCount
              edges {
                node {
                  name
                }
              }
            }
          }
        }
        """

        variables = dict(owner=self.owner, name=self.name)

        edges = []

        while True:
            results = self._run_query(query, variables=variables)
            total_count = results['data']['repository']['labels']['totalCount']
            edges.extend(results['data']['repository']['labels']['edges'])
            if len(edges) == total_count:
                break

        return [ x['node']['name'] for x in edges ]


    def get_issues(self):
        query = """
        query RepoIssueQuery($owner: String!, $name: String!, $after: String) {
          repository(owner:$owner, name:$name) {
            issues(first:100, after:$after) {
              totalCount
              pageInfo {
                hasNextPage
              }
              edges {
                cursor
                node {
                  number
                  title
                  body
                  bodyText
                  bodyHTML
                  labels(first:100) {
                    edges {
                      node {
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """

        variables = dict(owner=self.owner, name=self.name)

        edges = []

        while True:
            results = self._run_query(query, variables)
            issues = results['data']['repository']['issues']
            edges.extend(issues['edges'])
            if not issues['pageInfo']['hasNextPage']:
                break

            cursor = issues['edges'][-1]['cursor']
            variables['after'] = cursor

        return [ x['node'] for x in edges ]


# For quick interactive testing
if __name__ == '__main__':
    import os
    import sys

    if len(sys.argv) != 2:
        msg = "USAGE: {} <token file>\n".format(os.path.basename(sys.argv[0]))
        sys.stderr.write(msg)
        sys.exit(1)

    if not os.path.isfile(sys.argv[1]):
        msg = "Token file path '{}' does not exist\n".format(sys.argv[1])
        sys.exit(1)

    token = open(sys.argv[1]).read().strip()

    ghr = GithubRepo('astropy', 'astropy', token)
    print(ghr.get_label_names())
