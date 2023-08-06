from argparse import ArgumentParser
from multimodal.features.bottomup import COCOBottomUpFeatures
from multimodal import DEFAULT_DATA_DIR
from multimodal.datasets.vqa import VQA, VQA2, VQACE, VQACP, VQACP2, AdVQA
from functools import partial

class DownloadCommand:

    command = "download"
    datasets = {
        "vqa2": VQA.download_and_process,
        "vqa": VQA2.download_and_process,
        "vqacp": VQACP.download_and_process,
        "vqacp2": VQACP2.download_and_process,
        "advqa": AdVQA.download_and_process,
        "vqace": VQACE.download_and_process,
        "coco-bottomup-trainval": partial(COCOBottomUpFeatures.download_and_process, name="coco-bottomup"),
        "coco-bottomup-trainval-36": partial(COCOBottomUpFeatures.download_and_process, name="trainval2014_36"),
    }

    @classmethod
    def add_parser(cls, subparser):
        parser: ArgumentParser  = subparser.add_parser("download")
        parser.add_argument("dataset", choices=cls.datasets.keys())
        parser.add_argument("--dir_data", default=DEFAULT_DATA_DIR)
        return parser
    
    @classmethod
    def run(cls, args):
        dataset = cls.datasets[args.dataset]
        print(f"Downloading from dataset {args.dataset}")
        dataset(dir_data=args.dir_data)
