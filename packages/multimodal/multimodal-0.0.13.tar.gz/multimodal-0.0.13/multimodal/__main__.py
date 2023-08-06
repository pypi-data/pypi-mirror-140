import argparse
from multimodal.commands.vqa_eval import (
    VQA2EvalCommand,
    VQACP2EvalCommand,
    VQACPEvalCommand,
    VQAEvalCommand,
)
from multimodal.commands.download import DownloadCommand

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command")
subparsers.required = True

for cls in [
    VQAEvalCommand,
    VQA2EvalCommand,
    VQACPEvalCommand,
    VQACP2EvalCommand,
    DownloadCommand,
]:
    subparser = cls.add_parser(subparsers)
    subparser.set_defaults(func=cls.run)
    

args = parser.parse_args()
args.func(args)

