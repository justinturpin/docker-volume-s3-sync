#!/usr/bin/env python3

"""
Save and restore Docker Volumes to and from S3. Also supports saving volumes to disk.
"""

import click
import os
import tempfile

from subprocess import run, PIPE


@click.group()
def cli():
    pass


def path_split(path: str):
    return os.path.basename(path), os.path.dirname(os.path.abspath(os.path.expanduser(path)))


def volume_exists(volume_name) -> bool:
    return volume_name in run(['docker', 'volume', 'ls', '-q'], stdout=PIPE) \
        .stdout.decode().splitlines()


def volume_save_to_file(volume_name: str, path: str):
    filename, dirname = path_split(path)

    run([
        'docker', 'run', '--rm',
        '-v', '{}:/data'.format(volume_name),
        '-v', '{}:/tmp'.format(dirname),
        'alpine:edge',
        'tar', '-cf', '/tmp/{}'.format(filename), '-C', '/data', '.'
    ])


def volume_restore_from_file(volume_name: str, path: str):
    filename, dirname = path_split(path)

    run([
        'docker', 'run', '--rm',
        '-v', '{}:/data'.format(volume_name),
        '-v', '{}:/tmp:ro'.format(dirname),
        'alpine:edge',
        'tar', '-xf', '/tmp/{}'.format(filename), '-C', '/data', '.'
    ])


@cli.command()
@click.argument('volume-name')
@click.argument('path')
def volume_to_file(volume_name: str, path: str):
    """
    Save a volume to a file.
    """

    volume_save_to_file(volume_name, path)


@cli.command()
@click.argument('path')
@click.argument('volume-name')
def file_to_volume(path: str, volume_name: str):
    volume_restore_from_file(volume_name, path)


@cli.command()
@click.argument('volume-name', help='docker volume name to back up')
@click.argument('s3-path', help='s3 url to upload to (eg. s3://my-backup-bucket/myfile.tar.gz)')
def volume_to_s3(volume_name, s3_path):
    """Upload a volume to an S3 bucket."""

    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpfilename = os.path.join(tmpdirname, 'volume.tar.gz')
        volume_save_to_file(volume_name, tmpfilename)
        run(['s3cmd', 'put', tmpfilename, s3_path])


@cli.command()
@click.argument('s3-path', help='s3 url to restore from (eg. s3://my-backup-bucket/myfile.tar.gz)')
@click.argument('volume-name', help='docker volume name to create')
@click.option('--force', flag=True)
def s3_to_volume(s3_path, volume_name, force: bool):
    """
    Restore a volume from S3. By default will not restore a docker volume if a volume of that name
    already exists, allowing it to be used in configuration management tools that might run on a set
    schedule. The first time it runs you would want the restore to happen, but subsequent times you won't.

    Pass --force to override this behavior.
    """

    if not force and volume_exists(volume_name):
        print('Volume {} already exists, not restoring.'.format(volume_name))

        return

    with tempfile.TemporaryDirectory() as tmpdirname:
        # Create a temporary directory to put our volume file in.

        tmpfilename = os.path.join(tmpdirname, 'volume.tar.gz')
        run(['s3cmd', 'get', s3_path, tmpfilename])
        volume_restore_from_file(volume_name, tmpfilename)


if __name__ == '__main__':
    cli()
