#!/bin/bash
echo "Set Encryption in all S3 Buckets"
export AWS_DEFAULT_REGION=eu-west-2
/home/steampipe/.local/bin/custodian run --dryrun -s out /home/japjot/linux/config/iaws/custom_scripts/s3_encryption.yaml
