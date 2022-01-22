import re
import subprocess
import sys
from pathlib import Path

import typer

repo_path = Path(__file__).parent
package_name = repo_path.name
package_path = repo_path / package_name
init_version_re = r'__version__ = [\'"](\S+)[\'"]'
poetry_version_re = r'Bumping version from (\S+) to (\S+)'

app = typer.Typer()


@app.command()
def version(
    rule: str = typer.Argument('patch', help='Poetry version bump rule.'),
):
    '''Increment package version.'''

    messages = []

    # Run poetry version
    result = subprocess.run(
        ['poetry', 'version', rule],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )

    # Lookup versions in poetry version results
    result_match = re.search(poetry_version_re, result.stdout)
    if not result_match:
        typer.echo(f'Error: Failed to bump version:\n{result.stdout}')
        raise typer.Exit()
    version, next_version = result_match.group(1), result_match.group(2)

    typer.echo(f'Bumping version from {version} to {next_version}...')
    typer.echo('  Updated pyproject.toml!')

    # Find version in __init__.py
    init_path = package_path / '__init__.py'
    init_text = init_path.read_text()
    init_match = re.search(init_version_re, init_text)
    if not init_match:
        typer.echo(f'  Failed to update {init_path}: __version__ undefined')
    else:
        # Update version in __init__.py
        init_path.write_text(
            init_text[:init_match.start(1)]
            + next_version
            + init_text[init_match.end(1):]
        )
        typer.echo(f'  Updated {init_path.relative_to(repo_path)}!')


@app.command()
def code_quality():
    '''Run code quality tools.'''

    subprocess.run('poetry run isort')


@app.command()
def release():
    '''Release package.'''

    subprocess.run('poetry publish --build')


@app.command()
def test():
    '''Run test suite.'''

    result = subprocess.run(['pytest', '-vv', '--cov=' + package_name])
    sys.exit(result.returncode)


if __name__ == '__main__':
    app()
