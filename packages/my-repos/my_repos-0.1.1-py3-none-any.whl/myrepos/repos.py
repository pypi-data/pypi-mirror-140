#!/usr/bin/env python

from pathlib import Path
from pydoc import cli
import subprocess
import sys
from typing import Optional

import click


def update_repo(url: str, repo_clone: Path):
    print(f"{url} -> {repo_clone}")
    repo_clone = Path(repo_clone)
    if repo_clone.is_dir():
        return subprocess.run(
            ("git", "fetch"),
            cwd=repo_clone,
        )
    else:
        return subprocess.run(
            ("git", "clone", "--bare", url, repo_clone),
        )


@click.command()
@click.option(
    "--repo-list-file", help="file with a list of repositories; omit to read from stdin"
)
@click.option(
    "--mirror-dir", type=Path, default=Path(".mirrors")
)
def sync(repo_list_file: str, mirror_dir: Path):
    repos = repos_from_file(repo_list_file)
    repo_dir = mirror_dir
    for repo in repos:
        repo_host, _, name = repo.partition("/")
        update_repo(url=f"{repo_host}/{name}", repo_clone=repo_dir / name)


def repos_from_file(repo_list_file: Optional[str]):
    if repo_list_file is None:
        yield from map(str.strip, sys.stdin.readlines())
    else:
        with open(repo_list_file) as f:
            yield from map(str.strip, f.readlines())


@click.group()
def cli():
    pass

cli.add_command(sync)

if __name__ == "__main__":
    cli()
