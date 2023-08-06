import appdirs
import pathlib
import os
import yaml
from . import __version__ as version
from . import utils as djsciops_utils

djsciops_utils.log("configuration", message_type="header")

config_template = """
version: "{djsciops_version}"
aws:
  account_id: "{djsciops_aws_account_id}"
s3:
  role: "{djsciops_s3_role}"
  bucket: "{djsciops_s3_bucket}"
djauth:
  client_id: "{djsciops_djauth_client_id}"  
"""

config_directory = appdirs.user_data_dir(appauthor="datajoint", appname="djsciops")

try:
    # loading existing config
    config = yaml.safe_load(pathlib.Path(config_directory, "config.yaml").read_text())
    djsciops_utils.log(
        "Existing configuration detected. Loading...",
        pause_duration=1,
    )
except FileNotFoundError:
    djsciops_utils.log(
        "Welcome! We've detected that this is your first time using DataJoint SciOps CLI tools. We'll need to ask a few questions to initialize properly.",
        pause_duration=5,
    )
    # generate default config
    config = config_template.format(
        djsciops_aws_account_id=(
            os.getenv("DJSCIOPS_AWS_ACCOUNT_ID")
            if os.getenv("DJSCIOPS_AWS_ACCOUNT_ID")
            else input("\n   -> AWS Account ID? ")
        ),
        djsciops_s3_role=(
            os.getenv("DJSCIOPS_S3_ROLE")
            if os.getenv("DJSCIOPS_S3_ROLE")
            else input("\n   -> S3 Role? ")
        ),
        djsciops_s3_bucket=(
            os.getenv("DJSCIOPS_S3_BUCKET")
            if os.getenv("DJSCIOPS_S3_BUCKET")
            else input("\n   -> S3 Bucket? ")
        ),
        djsciops_djauth_client_id=(
            os.getenv("DJSCIOPS_DJAUTH_CLIENT_ID")
            if os.getenv("DJSCIOPS_DJAUTH_CLIENT_ID")
            else input("\n   -> DataJoint Account Client ID? ")
        ),
        djsciops_version=version,
    )
    # write config
    os.makedirs(config_directory, exist_ok=True)
    with open(pathlib.Path(config_directory, "config.yaml"), "w") as f:
        f.write(config)
    # load config
    config = yaml.safe_load(config)

    djsciops_utils.log(
        "Thank you! We've saved your responses so you won't need to specify this again.",
        pause_duration=5,
    )
