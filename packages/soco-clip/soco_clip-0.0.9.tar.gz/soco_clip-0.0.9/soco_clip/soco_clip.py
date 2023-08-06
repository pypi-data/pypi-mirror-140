import math
from PIL import Image
import torch
from argparse import ArgumentParser
from torchvision import transforms as T
from .models.wrapper import CustomCLIPWrapper
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
import PIL
import soco_clip.clip as clip
import os
import cv2
import shutil
import random


class CLIP(object):
    def __init__(self, clip_model="ViT-B-16", model_path = None, tokenizer=None, txt_encoder=None):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer) if tokenizer else None  #model_path = "zh_roberta_vit16.ckpt", tokenizer="hfl/chinese-roberta-wwm-ext", txt_encoder="hfl/chinese-roberta-wwm-ext"
        txt_encoder = AutoModel.from_pretrained(txt_encoder) if txt_encoder else None
        self.model = CustomCLIPWrapper.load_from_checkpoint(checkpoint_path=model_path, text_encoder=txt_encoder, minibatch_size=64, avg_word_embs=True, clip_model=clip_model ) if model_path else None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.image_encoder,self.preprocess = clip.load(clip_model, device=self.device) 
        if self.model:
            self.model.eval()

    def texts(self, query):
        if self.tokenizer:
            tk = self.tokenizer(query, return_tensors='pt', padding=True, truncation=True)
            y_hat = self.model.change_text_emb(self.model.encode_text(tk))
            return F.normalize(y_hat.to(self.device))
        else:
            text_input = clip.tokenize(query).to(self.device)
            text_embedding = self.image_encoder.encode_text(text_input)
            return text_embedding

    def image(self, im):
        if type(im) == str:
            image = Image.open(im)
        else:
            image = im
        image_input = self.preprocess(image).unsqueeze(0).to(self.device)
        img = self.image_encoder.encode_image(image_input)
        return img.to(torch.float32)
    
    def images(self, urls):
        temp = []
        for url in urls:
            if type(url) == str:
                image = Image.open(url)
            else:
                image = url
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            img = self.image_encoder.encode_image(image_input)
            temp.append(img[0])
        return torch.stack(temp, dim=0).to(torch.float32)

    def video(self,video_file, max_frames=50, rate=1000):
        pathOut = "tteemmpp"
        shutil.rmtree(pathOut,ignore_errors=True, onerror=None)
        os.makedirs(pathOut)
        count = 0
        vidcap = cv2.VideoCapture(video_file)
        success,image = vidcap.read()
        success = True
        paths = []
        while success:
            try:
                vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*rate))    # added this line
                success,image = vidcap.read()
                if success:
                    path = os.path.join(pathOut, "frame%d.jpg" % count)     # save frame as JPEG file
                    cv2.imwrite( os.path.join(pathOut, "frame%d.jpg" % count), image)     # save frame as JPEG file
                    count = count + 1
                    paths.append(path)
            except Exception as e:
                print (e)
                continue
        if max_frames > len(paths):
            y = self.images(paths)
        else:
            y = self.images(random.choices(paths, k=max_frames))
        return y

    def video_texts(self,video_file, texts, max_frames=50, rate=1000):
        pathOut = "tteemmpp"
        shutil.rmtree(pathOut,ignore_errors=True, onerror=None)
        os.makedirs(pathOut)
        count = 0
        vidcap = cv2.VideoCapture(video_file)
        success,image = vidcap.read()
        success = True
        paths = []
        while success:
            try:
                vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*rate))    # added this line
                success,image = vidcap.read()
                if success:
                    path = os.path.join(pathOut, "frame%d.jpg" % count)     # save frame as JPEG file
                    cv2.imwrite( os.path.join(pathOut, "frame%d.jpg" % count), image)     # save frame as JPEG file
                    count = count + 1
                    paths.append(path)
            except Exception as e:
                print (e)
                continue
        if max_frames > len(paths):
            y = self.images(paths)
        else:
            y = self.images(random.choices(paths, k=max_frames))
        t = self.texts(texts)
        z = t@y.mean(0, True).T.half()[:,0]
        maxindex = z.argmax()
        shutil.rmtree(pathOut,ignore_errors=True, onerror=None)
        return {"score":z.softmax(0)[maxindex].cpu().detach().item(), "pred":texts[maxindex]}

