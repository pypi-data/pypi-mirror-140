import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--dir-data", required=True)

    args = parser.parse_args()
    