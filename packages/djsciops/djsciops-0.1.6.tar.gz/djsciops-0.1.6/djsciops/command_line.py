import argparse
from . import __version__ as version
from . import authentication as djsciops_authentication
from . import axon as djsciops_axon
from . import settings as djsciops_settings


def djsciops(args: list = None):
    """
    Primary console interface for djsciops's shell utilities.

    :param args: List of arguments to be passed in, defaults to reading stdin
    :type args: list, optional
    """
    parser = argparse.ArgumentParser(
        prog="djsciops", description="DataJoint SciOps console interface."
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"djsciops {version}"
    )
    command = parser.add_subparsers(dest="command")
    axon = command.add_parser("axon", description="Manage object store data.")
    subcommand = axon.add_subparsers(dest="subcommand")
    axon_cp = subcommand.add_parser(
        "cp", description="Copy objects by uploading to object store."
    )
    required_named = axon_cp.add_argument_group("required named arguments")

    required_named.add_argument(
        "source",
        type=str,
        help="Source file or directory on client.",
    )
    required_named.add_argument(
        "destination",
        type=str,
        help="Target directory in object store.",
    )

    kwargs = vars(parser.parse_args(args))
    if kwargs["command"] == "axon" and kwargs["subcommand"] == "cp":
        djsciops_axon.upload_files(
            session=djsciops_authentication.Session(
                aws_account_id=djsciops_settings.config["aws"]["account_id"],
                s3_role=djsciops_settings.config["s3"]["role"],
                auth_client_id=djsciops_settings.config["djauth"]["client_id"],
            ),
            s3_bucket=djsciops_settings.config["s3"]["bucket"],
            source=kwargs["source"],
            destination=kwargs["destination"],
        )
    raise SystemExit
