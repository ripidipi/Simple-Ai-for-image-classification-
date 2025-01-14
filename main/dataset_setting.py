import random
import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import torchvision
from PIL import Image
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import os 
from typing import Dict, List, Tuple
from torch.utils.data import Dataset
import pathlib

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using : {device}")

data_path = Path("data/")
image_path = data_path / "food60"

train_dir = image_path / "train"
test_dir = image_path / "test"
quick_test_dir = image_path / "quick_test"

BATCH_SIZE = 64

def plot_transformed_images(image_paths, transform, n=3):
    "Plots a series of random images from image_paths."
    random_image_paths = random.sample(image_paths, k=n)
    for image_path in random_image_paths:
        with Image.open(image_path) as f:
            fig, ax = plt.subplots(1, 2)
            ax[0].imshow(f) 
            ax[0].set_title(f"Original \nSize: {f.size}")
            ax[0].axis("off")

            transformed_image = transform(f).permute(1, 2, 0) 
            ax[1].imshow(transformed_image) 
            ax[1].set_title(f"Transformed \nSize: {transformed_image.shape}")
            ax[1].axis("off")
            plt.xlabel(False)

            fig.suptitle(f"Class: {image_path.parent.stem}", fontsize=16)

    plt.show()        

def find_class(dir:str) -> Tuple[List[str], Dict[str, int]]:
    "Find right class in target dir"
    
    classes = sorted(entire.name for entire in os.scandir(dir) if entire.is_dir())
    
    if not classes:
        raise FileNotFoundError(f"classes didn't find in derectory {train_dir}... check path")
    classes_ind = {class_name: i for i, class_name in enumerate(classes)}
    return classes, classes_ind


class ImageCustomDataset(Dataset):
    "Main class of Image data"
    def __init__(self, 
                targ_dir:str,
                transform=None) -> None:
        "Params initialization"
        super().__init__()
        self.paths = list(pathlib.Path(targ_dir).glob("*/*.jpg"))
        self.transform = transform
        self.classes, self.classes_ind = find_class(targ_dir)
        

    def load_image(self, ind:int) -> Image.Image:
        "Open image via the path and return it"
        image_path = self.paths[ind]
        return Image.open(image_path)

    def __len__(self) -> int:
        "Take a length of dataset"
        return len(self.paths)
    
    def __getitem__(self, ind:int) -> Tuple[torch.Tensor, int]:
        "Return One sample of data, data and idx"
        img = self.load_image(ind)
        class_name = self.paths[ind].parent.name
        class_ind = self.classes_ind[class_name]
        
        if self.transform:
            return self.transform(img), class_ind
        else:
             return img, class_ind
        

train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(p=0.3),
    transforms.RandomVerticalFlip(p=0.3),
    # transforms.GaussianBlur(kernel_size=(5, 9), sigma=(0.1, 5)),
    transforms.RandomRotation(degrees=(30, 70)),
    transforms.ToTensor(),
])

test_transform = transforms.Compose([
        transforms.Resize(size=(224, 224)),
        transforms.ToTensor()
])



train_data_custom = ImageCustomDataset(targ_dir=train_dir,
                                       transform=train_transform)

test_data_custom = ImageCustomDataset(targ_dir=test_dir,
                                      transform=test_transform)

quick_test_data = ImageCustomDataset(targ_dir=quick_test_dir,
                                    transform=test_transform)

class_names = train_data_custom.classes

train_dataloader_custom = DataLoader(dataset=train_data_custom,
                                     batch_size=BATCH_SIZE,
                                     shuffle=True,
                                     pin_memory=True,
                                     )

test_dataloader_custom = DataLoader(dataset=test_data_custom,
                                    batch_size=BATCH_SIZE,
                                    shuffle=False,
                                    pin_memory=True,
                                    )

quick_test_dataloader = DataLoader(dataset=quick_test_data,
                                    batch_size=BATCH_SIZE,
                                    shuffle=False,
                                    pin_memory=True,
                                    )