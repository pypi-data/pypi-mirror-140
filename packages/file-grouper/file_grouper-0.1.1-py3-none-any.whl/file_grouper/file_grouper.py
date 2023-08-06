import os
import re
import shutil

import click


@click.command()
@click.option("--dryrun/--no-dryrun", default=True)
@click.option("--verbose", is_flag=True)
@click.option("--key_regex", required=True, type=str)
@click.option("--group_no", default=0)
@click.option("--dst_root", default=".", help="destiation root folder")
@click.option("--force", is_flag=True)
@click.argument("files", nargs=-1)
def group_file(dryrun, verbose, key_regex, group_no, dst_root, force, files):
    """Given FILE_PATTERN (glob), for each file, extract key by KEY_REGEX and GROUP_NO,
    copy the file to folder with name of extracted `key`"""
    if verbose:
        click.echo(f"key_regex={key_regex}")
    key_re = re.compile(key_regex)
    for file_path in files:
        m = key_re.search(file_path)
        key = m.group(group_no)

        dst = os.path.join(dst_root, key)
        print(f"{file_path} --> {key}/")
        dst_file_path = os.path.join(dst, os.path.basename(file_path))
        if os.path.exists(dst_file_path) and not force:
            click.echo(f"Destination file '{dst_file_path}' exists.", err=True)
            return -1

        if not dryrun:
            os.makedirs(dst, exist_ok=True)
            shutil.copy(file_path, dst_file_path)
