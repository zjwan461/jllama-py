import cv2
from insightface.app import FaceAnalysis
from insightface.utils import face_align
import torch
import os
import matplotlib.pyplot as plt
from random import randint

os.environ["http_proxy"] = "http://192.168.31.67:1082"
os.environ["https_proxy"] = "http://192.168.31.67:1082"
app = FaceAnalysis(name="buffalo_l", root="E:/models/insightface",
                   providers=['AzureExecutionProvider', 'CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))

image = cv2.imread(r"C:\Users\89712\Pictures\liuyifei.webp")
faces = app.get(image)

faceid_embeds = torch.from_numpy(faces[0].normed_embedding).unsqueeze(0)
face_image = face_align.norm_crop(image, landmark=faces[0].kps, image_size=224)  # you can also segment the face

import torch
from diffusers import StableDiffusionPipeline, DDIMScheduler, AutoencoderKL
from PIL import Image

from ip_adapter.ip_adapter_faceid import IPAdapterFaceID, IPAdapterFaceIDPlus

# from ip_adapter.ip_adapter_faceid import IPAdapterFaceIDPlus


sd_origin_model_path = r"E:\models\AI-ModelScope\stable-diffusion-v1-5"
base_model_path = r"E:\models\MusePublic\majicMIX_realistic_maijuxieshi_SD_1_5\majicmixRealistic_v7.safetensors"
vae_model_path = r"E:/models\zhuzhukeji\sd-vae-ft-mse"
image_encoder_path = "laion/CLIP-ViT-H-14-laion2B-s32B-b79K"
ip_ckpt = r"E:\models\guaidao\IP-Adapter-FaceID\ip-adapter-faceid_sd15.bin"
lora_ckpt = r"E:\models\guaidao\IP-Adapter-FaceID\ip-adapter-faceid_sd15_lora.safetensors"

device = "cuda" if torch.cuda.is_available() else "cpu"

noise_scheduler = DDIMScheduler(
    num_train_timesteps=1000,
    beta_start=0.00085,
    beta_end=0.012,
    beta_schedule="scaled_linear",
    clip_sample=False,
    set_alpha_to_one=False,
    steps_offset=1,
)
# vae = AutoencoderKL.from_pretrained(vae_model_path).to(dtype=torch.float16)
pipe = StableDiffusionPipeline.from_single_file(
    base_model_path,
    torch_dtype=torch.float16,
    scheduler=noise_scheduler,
    # vae=vae,
    config=sd_origin_model_path,
    feature_extractor=None,
    safety_checker=None
)

# pipe.load_lora_weights(lora_ckpt)
# pipe.fuse_lora()

# load ip-adapter

# ip_model = IPAdapterFaceID(pipe, ip_ckpt, device)
ip_model = IPAdapterFaceIDPlus(pipe, image_encoder_path, ip_ckpt, device,)

# generate image
prompt = "1girl,naked,beach,busty"
negative_prompt = "monochrome, lowres, bad anatomy, worst quality, low quality, blurry"

seed = randint(1, 100000000)
images = ip_model.generate(
    prompt=prompt, negative_prompt=negative_prompt, face_image=face_image, faceid_embeds=faceid_embeds, num_samples=1,
    width=512, height=768,
    num_inference_steps=30, seed=seed, guidance_scale=7.5
)
# 显示图像
for i, image in enumerate(images):
    plt.subplot(1, len(images), i + 1)
    plt.imshow(image)
    plt.axis('off')

plt.tight_layout()
plt.show()
