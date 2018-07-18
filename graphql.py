#!/usr/bin/env python3
import requests


API_ENDPOINT = "https://api.github.com/graphql"


class GithubRepo:

    def __init__(self, owner, name, api_key):
        self.owner = owner
        self.name = name
        self.api_key = api_key

    def _run_query(self, query):

        headers = { "Authorization": "bearer {}".format(self.api_key) }
        result = requests.post(API_ENDPOINT, json={'query': query}, headers=headers)
        if result.status_code != 200:
            raise RuntimeError("Query failed to run: ", result.message)

        return result.json()

    def get_label_names(self):
        query = """
        query {{
          repository(owner:"{}", name:"{}") {{
            labels(last:100) {{
              totalCount
              edges {{
                node {{
                  name
                }}
              }}
            }}
          }}
        }}
        """.format(self.owner, self.name)

        edges = []

        while True:
            results = self._run_query(query)
            total_count = results['data']['repository']['labels']['totalCount']
            edges.extend(results['data']['repository']['labels']['edges'])
            if len(edges) == total_count:
                break

        return [ x['node']['name'] for x in edges ]


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
