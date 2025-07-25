import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Parse reasoning arguments")

    # Actions
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--process", action="store_true")

    # Parameters
    parser.add_argument("-p", "--prompt", type=str, default=None)
    parser.add_argument("-c", "--config", type=str, default=None)
    parser.add_argument("-i", "--instances", type=int, default=1)
    parser.add_argument("-s", "--samples", type=int, default=1)
    parser.add_argument("-d", "--domains", type=str, default=None)
    parser.add_argument("-e", "--experiment", type=str, default=None)

    return parser.parse_args()