#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3==1.43.109"]
# ///
"""Build the blog and publish it to https://blog.delightql.org/.

    ./deploy.py              build, show what would change, ask, publish
    ./deploy.py --dry-run    build and show what would change, change nothing
    ./deploy.py --yes        publish without asking
    ./deploy.py --all        upload every file, changed or not (after changing
                             the content types or cache times below)

The bucket ends up holding exactly what Hugo built into public/: new and
changed files are uploaded, and files the build no longer has are deleted.
A file is unchanged when its MD5 equals the object's ETag, which holds for
one-part uploads, as every upload here is.

Credentials come from the AWS profile "delightql" and nothing else; its
credential_process decrypts the keys with gpg, once per run.

Exit: 0 published or nothing to do, 1 otherwise.
"""

import argparse
import hashlib
import mimetypes
import os
import subprocess
import sys
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

# The blog's own bucket. Never the main site's (delightql.org): this script
# deletes whatever the bucket holds that the build does not.
BUCKET = "blog.delightql.org"
REGION = "us-east-2"
PROFILE = "delightql"
HERE = Path(__file__).resolve().parent
PUBLIC = HERE / "public"

TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".xml": "application/xml; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".woff2": "font/woff2",
}
# Pages and feeds change with every post, so Cloudflare and browsers check
# them again after five minutes; everything else after an hour.
SHORT_LIVED = {".html", ".xml", ".json", ".txt"}


def headers(key: str) -> dict:
    suffix = Path(key).suffix.lower()
    kind = TYPES.get(suffix) or mimetypes.guess_type(key)[0] or "application/octet-stream"
    return {"ContentType": kind,
            "CacheControl": "max-age=300" if suffix in SHORT_LIVED else "max-age=3600"}


def build() -> dict[str, Path]:
    """Build the site into a clean public/; return {object key: file}."""
    try:
        subprocess.run(["hugo", "--gc", "--minify", "--cleanDestinationDir"], cwd=HERE, check=True)
        drafts = subprocess.run(["hugo", "list", "drafts"], cwd=HERE, check=True,
                                capture_output=True, text=True).stdout.splitlines()[1:]
    except (OSError, subprocess.CalledProcessError) as error:
        sys.exit(f"deploy.py: the Hugo build failed: {error}")
    if drafts:
        print(f"deploy.py: {len(drafts)} draft post(s) left out (draft = true)")
    files = {path.relative_to(PUBLIC).as_posix(): path
             for path in sorted(PUBLIC.rglob("*")) if path.is_file()}
    if "index.html" not in files:
        sys.exit(f"deploy.py: the build has no index.html; nothing published")
    return files


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="show what would change, change nothing")
    mode.add_argument("--yes", action="store_true", help="publish without asking")
    parser.add_argument("--all", action="store_true", help="upload every file, changed or not")
    args = parser.parse_args()

    files = build()
    # An endpoint left in the environment would send the files elsewhere,
    # and naming the profile makes boto3 ignore any keys there.
    for name in ("AWS_ENDPOINT_URL", "AWS_ENDPOINT_URL_S3"):
        os.environ.pop(name, None)
    s3 = boto3.Session(profile_name=PROFILE, region_name=REGION).client("s3")
    there = {}
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=BUCKET):
        for item in page.get("Contents", []):
            there[item["Key"]] = item["ETag"].strip('"')

    new = [key for key in files if key not in there]
    changed = [key for key in files if key in there and (args.all or there[key] != md5(files[key]))]
    stale = sorted(set(there) - set(files))
    for label, keys in (("new", new), ("changed", changed), ("delete", stale)):
        for key in keys:
            print(f"  {label:8s} {key}")
    print(f"deploy.py: s3://{BUCKET}: {len(new)} new, {len(changed)} changed, {len(stale)} to delete, "
          f"{len(files) - len(new) - len(changed)} unchanged")
    if not (new or changed or stale):
        return 0
    if args.dry_run:
        print("deploy.py: dry run, nothing changed")
        return 0
    if not args.yes:
        try:
            answer = input(f"deploy.py: publish to https://{BUCKET}/ ? [y/N] ")
        except EOFError:
            answer = ""
        if answer.strip().lower() not in ("y", "yes"):
            print("deploy.py: nothing published")
            return 1

    for key in new + changed:
        s3.put_object(Bucket=BUCKET, Key=key, Body=files[key].read_bytes(), **headers(key))
    for start in range(0, len(stale), 1000):
        batch = [{"Key": key} for key in stale[start:start + 1000]]
        failed = s3.delete_objects(Bucket=BUCKET, Delete={"Objects": batch, "Quiet": True}).get("Errors")
        if failed:
            print(f"deploy.py: could not delete {', '.join(e['Key'] for e in failed)}", file=sys.stderr)
            return 1
    print(f"deploy.py: published {len(new) + len(changed)} file(s), deleted {len(stale)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (BotoCoreError, ClientError) as error:
        sys.exit(f"deploy.py: {error}")
    except KeyboardInterrupt:
        sys.exit("\ndeploy.py: interrupted")
