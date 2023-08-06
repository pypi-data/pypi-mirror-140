import argparse
import signal

from efemarai import Session


def signal_handler(sig, frame):
    print("")
    exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config-file",
        "-c",
        default=None,
        help="Path where to store SDK configuration.",
    )
    args = parser.parse_args()

    Session._user_setup(config_file=args.config_file)


if __name__ == "__main__":
    main()
