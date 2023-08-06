from multimodal.datasets.vqa import VQA2
from torch.utils.data.dataset import Dataset



class VQACE(Dataset):

    SPLITS = ["train", "val", "val-simple", "val-counterexamples", "val-hard"]

    def __init__(self, 
        dir_data=None,
        features=None,
        split="train",
        min_ans_occ=9,
        dir_features=None,
        label="multilabel",
        tokenize_questions=False,
        load=True,):

        vqa2 = VQA2(dir_data=dir_data,
            features=features,
            split=split,
            min_ans_occ=min_ans_occ,
            dir_features=dir_features,
            label=label,
            tokenize_questions=tokenize_questions,
            load=load,
        )

        # filter questions with counterexamples
        

    def __len__(self) -> int:
        return 0

    def __getitem__(self, index):
        pass
