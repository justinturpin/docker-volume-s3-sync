from setuptools import setup, find_packages

setup(
    name='docker_volume_sync',
    version='0.1.0-alpha1',
    install_requires=[
        'click',
        's3cmd'
    ],
    packages=find_packages(exclude=['bin', 'env', 'test']),
    entry_points={
        'console_scripts': [
            'docker-volume-sync=jt_docker_volume_sync.cli:cli',
        ]
    }
)
