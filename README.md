# Docker Volume S3 Sync

Upload Docker Volumes to S3, or an equivalent service.

Used to create backups of docker volumes whose restorations can be immediately be used by running
services by simply point them at the new volume.

## Installation

Currently requires Python 3 and `s3cmd` for the S3 upload and get process. Future versions will
use Boto3 directly, and possibly the docker API as well.
