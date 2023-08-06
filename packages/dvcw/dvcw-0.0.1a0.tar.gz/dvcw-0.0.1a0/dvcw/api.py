import dvc.api


def get_url(path: str, repo: str = None, rev: str = None, remote: str = None):
    return dvc.api.get_url(path=path, repo=repo, rev=rev, remote=remote)
