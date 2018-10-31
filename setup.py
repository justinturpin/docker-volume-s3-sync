from setuptools import setup

setup(
    name='docker_volume_sync',
    version='0.1.0-alpha1',
    install_requires=[
        'click',
        's3cmd'
    ],
    entry_points={
        'console_scripts': [
            'docker-volume-sync=jt_docker_volume_sync.cli:cli',
        ]
    }
)
