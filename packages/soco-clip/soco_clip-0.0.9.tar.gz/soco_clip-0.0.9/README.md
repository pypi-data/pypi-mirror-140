# soco-clip

## How to install
```
pip install soco-clip
```

## Download model
```
wget https://openaipublic.azureedge.net/clip/models/5806e77cd80f8b59890b7e101eabd078d9fb84e6937f9e85e4ecb61988df416f/ViT-B-16.pt
```

## Examples
```
from soco_clip import CLIP

encoder = CLIP()

encoded_texts = encoder.texts(["standing","sitting"])
encoded_images = encoder.images(["a.jpg","b.jpg"])
video_texts_result = encoder.video_texts("a.mp4",["standing","sitting"])

```

