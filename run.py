import argparse

from utils import run


parser = argparse.ArgumentParser()

parser.add_argument("-r", "--run", type=int, required=True, choices=[0, 1, 2], help="Run type: 0 = baseline (cosine), 1 = constrained (BM25), 2 = unconstrained BM25 + (title + description)")
parser.add_argument("-q", "--queries", type=str, required=True, help="Path to topics XML file")
parser.add_argument("-d", "--documents_list", type=str, default=None, help="Path to documents list")
parser.add_argument("-o", "--output", type=str, default=None, help="Output results file")


def main(args):
    if "en" in args.queries:
        language = "en"
    elif "cs" in args.queries:
        language = "cs"
    else:
        raise ValueError("Could not determine language from queries filename")

    train = "train" in args.queries

    run(language, args.run, train, args.queries, args.documents_list, args.output)


if __name__ == '__main__':
    args = parser.parse_args()

    print(f"""
========================================
Running Information Retrieval System
----------------------------------------
Language : {"en" if "en" in args.queries else "cs"}
Run      : run-{args.run}
Dataset  : {"train" if "train" in args.queries else "test"}
Queries  : {args.queries}
Documents: {args.documents_list}
Output   : {args.output}
========================================
""")

    main(args)