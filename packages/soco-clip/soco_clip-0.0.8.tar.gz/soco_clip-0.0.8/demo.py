from soco_clip import CLIP


if __name__ == "__main__":
    import glob
    import numpy as np
    X = CLIP()
    #kmodel = CLIP("ViT-B-16","en_roberta_vit16.ckpt","roberta-base","roberta-base")
    #kmodel = CLIP("ViT-B-16","zh_roberta_vit16.ckpt","hfl/chinese-roberta-wwm-ext","hfl/chinese-roberta-wwm-ext")
    #z = kmodel.text_encode(["冬天","冬天"])
    #i = X.image_encodes(["/mnt/lambda_data/KL/CUHK-PEDES/imgs/test_query/p20_s39.jpg","/mnt/lambda_data/KL/CUHK-PEDES/imgs/test_query/p53_s102.jpg"])
    #print (X.clip_text_encode(["i am a boy"]))
    #print (z@i.T)

    print (X.image("sample.png"))
    print (X.video_texts("a.mp4",["play","washing","swimming"]))
