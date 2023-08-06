import argparse
import os

import mite_vspkg


def argparse_parse(argv):
    parser = argparse.ArgumentParser(
        prog=mite_vspkg.__name__,
        formatter_class=argparse.RawTextHelpFormatter,
        description="Get list of files per Visual Studio installer package\n"
                    "    or unpack Visual Studio installer packages.")
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=("%(prog)s {version}".format(version=mite_vspkg.__version__)))
    parser.add_argument(
        "-d", "--work-dir",
        help="Directory with 'config' folder.\n"
             "Defaults to '<current_directory>/mite-vspkg'.")
    parser.add_argument(
        "-c", "--config-name",
        help="Name of the configuration file\n"
             "    in '<work_dir>/config' folder.\n"
             "Defaults to 'config.py'.\n"
             "If the default is used\n"
             "    and '<work_dir>/config/config.py' doesn't exist,\n"
             "    the default config is copied\n"
             "    to '<work_dir>/config/config.py'.")
    return parser.parse_args(args=argv[1:])


def process_args(args):
    if args.work_dir:
        work_dir = args.work_dir
    else:
        work_dir = os.path.join(os.getcwd(), "mite-vspkg")
    config_name = args.config_name
    if config_name and not config_name.endswith(".py"):
        config_name += ".py"
    return (work_dir, config_name)


def parse(argv):
    argparsed_args = argparse_parse(argv)
    return process_args(argparsed_args)
