import yaml
import torch
import torch.nn as nn
from torchvision import transforms, models
from torch.nn.functional import softmax

class DC():
    def __init__(self, config, device, log):
        self.cfg = yaml.safe_load(open(config['config']))
        self.classes = self.cfg['CLASSES']
        self.cfg['MODEL']['WEIGHTS'] = config['weights']
        self.device = device

        self.build_model()

    def build_model(self):
        self.transformer = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((self.cfg['INPUT']['SIZE'], self.cfg['INPUT']['SIZE'])),
            transforms.ToTensor(),
            transforms.Normalize(self.cfg['MODEL']['PIXEL_MEAN'], self.cfg['MODEL']['PIXEL_STD'])
            ])

        model = models.resnet18(pretrained=False)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, self.cfg['MODEL']['NUM_CLASSES'])
        model.load_state_dict(torch.load(self.cfg['MODEL']['WEIGHTS'], map_location=torch.device(self.device)))

        model.eval()

        self.model = model.to(self.device)

    def predict(self, img):
        with torch.no_grad():
            img = self.transformer(img).unsqueeze_(0)
            img = img.to(self.device)
            outputs = self.model(img)
            outputs = softmax(outputs, 1)

            prob, preds = torch.max(outputs, 1)
            prob = float(prob.item())
            pred = self.classes[preds.item()]

        return pred, prob

