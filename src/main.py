import argparse


def create_parser():
    parser = argparse.ArgumentParser(description="This is a simple game.")
    parser.add_argument(
        "--option",
        dest="option",
        help="what do you want to do?",
        choices={"run", "train"})

    return parser.parse_args()


if __name__ == "__main__":
    args = create_parser()
    pass