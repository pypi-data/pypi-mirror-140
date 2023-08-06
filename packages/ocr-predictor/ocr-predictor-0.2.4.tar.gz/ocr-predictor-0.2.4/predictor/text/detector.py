from PIL import Image
import vietocr.tool.predictor as ocr
from vietocr.tool.config import Cfg

class TextDetector():

    def __init__(self, config, device, log):

        vietocr_config = Cfg.load_config_from_file(config['config'])
        vietocr_config['weights'] = config['weights']
        vietocr_config['device'] = device
        self.detector = ocr.Predictor(vietocr_config)

        self.log = log

    def vietocr(self, img):
        img = Image.fromarray(img)

        text = self.detector.predict(img)
        text = text.strip()

        return text, 1.0

    def predict(self, img):
             
        return self.vietocr(img)

    def predict_batch(self, imgs):
        imgs = [Image.fromarray(img) for img in imgs]

        text, prob = self.detector.predict_batch(imgs, return_prob=True)

        return text, prob
