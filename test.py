import json

from fk.artifact import _score_artifact


def main():
    with open('assets.json', 'rb') as f:
        repos = json.load(f)

    for repo in repos:
        artifacts = [a['name'] for a in repo['assets']]
        print(repo['url'], sorted(((_score_artifact(a), a) for a in artifacts), reverse=True)[0], '', sep='\n')


if __name__ == '__main__':
    main()
