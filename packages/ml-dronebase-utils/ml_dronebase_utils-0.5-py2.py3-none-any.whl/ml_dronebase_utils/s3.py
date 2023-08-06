import json
import os
import pathlib
import warnings
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from tqdm import tqdm


def is_json(myjson: str) -> bool:
    """Checks if the string is a json file.

    Args:
        myjson (str): Filename or path to potential json file.

    Returns:
        bool: Whether myjson was a json file.
    """
    try:
        json.loads(myjson)
    except ValueError:
        return False

    return True


def upload_file(
    local_file: str, bucket_name: str, prefix: str, exist_ok: bool = True
) -> None:
    client = boto3.client("s3")

    root = os.path.dirname(os.path.abspath(local_file))
    filename = os.path.basename(local_file)
    local_path = os.path.join(root, filename)
    print(local_path)

    if not pathlib.Path(prefix).suffix:
        s3_path = os.path.join(prefix, filename)
    else:
        if pathlib.Path(prefix).suffix == pathlib.Path(filename).suffix:
            s3_path = prefix
        else:
            s3_path = os.path.join(os.path.dirname(prefix), filename)
            warnings.warn(
                "Mismatched file extensions, converting prefix to local file format."
            )

    if exist_ok:
        try:
            client.head_object(Bucket=bucket_name, Key=s3_path)
        except ClientError:
            client.upload_file(local_path, bucket_name, s3_path)
    else:
        client.upload_file(local_path, bucket_name, s3_path)


def upload_dir(
    local_directory: str, bucket_name: str, prefix: str, exist_ok: bool = True
) -> None:
    """Upload data from a local directory to an S3 bucket.

    Args:
        local_directory (str): Local directory to upload from.
        bucket_name (str): S3 bucket name.
        prefix (str): Relative path from bucket to save data.
        exist_ok (bool): Decides whether or not to ignore existing files. Default True.
    """
    client = boto3.client("s3")

    # enumerate local files recursively
    for root, dirs, files in os.walk(local_directory):
        for filename in files:
            # construct the full local path
            local_path = os.path.join(root, filename)

            # construct the full Dropbox path
            relative_path = os.path.relpath(local_path, local_directory)
            s3_path = os.path.join(prefix, relative_path)

            if exist_ok:
                try:
                    client.head_object(Bucket=bucket_name, Key=s3_path)
                except ClientError:
                    client.upload_file(local_path, bucket_name, s3_path)
            else:
                client.upload_file(local_path, bucket_name, s3_path)


def download_s3_file(
    bucket_name: str, prefix: str, local_path: str, size_limit: Optional[int] = None
) -> None:
    """Download file from S3 bucket to local directory.

    Args:
        bucket_name (str): S3 bucket name.
        prefix (str): Relative path from bucket to requested file.
        local_path (str): Local directory to store file.
        size_limit (int, optional): Limits the file size accepted to size_limit bytes.
        Default None.
    """
    s3 = boto3.client("s3")
    if size_limit is not None:
        response = s3.head_object(Bucket=bucket_name, Key=prefix)
        file_size = int(response["ContentLength"])
        if file_size > size_limit:
            raise ValueError(
                "image size {} exceeds size_limit {}".format(file_size, size_limit)
            )

    s3.download_file(bucket_name, prefix, local_path)


def download_s3_folder(
    bucket_name: str,
    prefix: str,
    local_directory: Optional[str] = None,
    size_limit: Optional[int] = None,
) -> None:
    """Download the contents of a folder directory.

    Args:
        bucket_name (str): S3 bucket name.
        prefix (str): Relative path from bucket to requested files.
        local_directory (str, optional): Local directory to store files in.
        size_limit (int, optional): Limits the file size accepted to size_limit bytes.
        Default None.
    """
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    objects = bucket.objects.filter(Prefix=prefix)
    num_objects = sum(1 for _ in objects.all())
    for i, obj in enumerate(tqdm(objects, total=num_objects)):
        target = (
            obj.key
            if local_directory is None
            else os.path.join(local_directory, os.path.relpath(obj.key, prefix))
        )
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == "/":
            continue
        if size_limit is not None:
            if obj.size > size_limit:
                continue
        bucket.download_file(obj.key, target)


def sync_s3_folder(bucket_name: str, prefix: str, local_directory: str) -> None:
    """Download the contents of a folder directory in parallel using aws s3 sync.

    Args:
        bucket_name (str): S3 bucket name.
        prefix (str): Relative path from bucket to requested files.
        local_directory (str): Local directory to store files in.
    """
    os.makedirs(local_directory)
    os.system(f"aws s3 sync s3://{bucket_name}/{prefix}/ {local_directory}")
