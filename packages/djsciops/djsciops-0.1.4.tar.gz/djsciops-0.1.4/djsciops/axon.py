import pathlib
import os
import boto3.s3.transfer
import tqdm
from typing import Union
from . import utils as djsciops_utils


def _generate_transfer_mapping(
    session, s3_bucket: str, source: Union[str, list], destination: Union[str, list]
) -> tuple:
    if (
        isinstance(source, list)
        and isinstance(destination, list)
        and len(source) == len(destination)
    ):
        djsciops_utils.log(f"Upload mapping provided.")
        file_paths, object_paths = (source, destination)
        existing_objects = {
            pathlib.PosixPath(op.key)
            for op in session.s3.Bucket(s3_bucket).objects.filter(
                Prefix=os.path.commonprefix(object_paths)
            )
        }
        file_paths, object_paths = tuple(
            zip(
                *(
                    (fp, op)
                    for fp, op in zip(file_paths, object_paths)
                    if op not in existing_objects
                )
            )
        )
        assert file_paths, "All files already exist in object store."
    else:
        # modes: file -> directory, directory -> directory
        assert destination[-1] == "/", "Must point to a directory in object store."
        source = pathlib.PosixPath(source).resolve()
        # recursively list files that are not hidden or directories
        file_paths = {
            fp.relative_to(source)
            for fp in source.rglob("*")
            if not fp.is_dir() and not str(fp.name).startswith(".")
        }
        file_paths = (
            file_paths if file_paths else {pathlib.PosixPath(source.name)}
        )  # if specified a single file
        # recursively list objects
        existing_objects = {
            pathlib.PosixPath(op.key.replace(destination, ""))
            for op in session.s3.Bucket(s3_bucket).objects.filter(Prefix=destination)
        }
        # exclude objects that exist and verify that new objects are present
        file_paths = file_paths - existing_objects
        assert file_paths, "All files already exist in object store."
        object_paths = [pathlib.PosixPath(destination, fp) for fp in file_paths]
        file_paths = [
            pathlib.Path(source if source.is_dir() else source.parent, fp)
            for fp in file_paths
        ]

    return file_paths, object_paths


def upload_files(session, s3_bucket: str, source: str, destination: str):
    djsciops_utils.log("axon copy", message_type="header")
    file_paths, object_paths = _generate_transfer_mapping(
        session=session, s3_bucket=s3_bucket, source=source, destination=destination
    )
    djsciops_utils.log("Starting upload\n")
    with tqdm.tqdm(
        total=sum(os.stat(fp).st_size for fp in file_paths),
        unit="B",
        unit_scale=True,
        desc="",
    ) as pbar:
        for fp, op in zip(file_paths, object_paths):
            pbar.write(f"{fp}->{op}")
            session.s3.Bucket(s3_bucket).upload_file(
                Filename=str(fp),
                Key=str(op),
                Config=boto3.s3.transfer.TransferConfig(
                    multipart_threshold=1024 * 25,
                    max_concurrency=10,
                    multipart_chunksize=1024 * 25,
                    use_threads=True,
                ),
                Callback=lambda bytes_transferred: pbar.update(bytes_transferred),
            )
