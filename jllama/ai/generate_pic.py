import torch
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
import matplotlib.pyplot as plt

# 设置设备
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"使用设备: {device}")

# 加载模型
# model_id = r"E:\models\AI-ModelScope\stable-diffusion-v1-5"  # 也可以选择其他模型
# # 使用原生sd模型生成图片
# pipe = StableDiffusionPipeline.from_pretrained(
#     model_id,
#     torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32,
#     safety_checker=None,  # 可以移除安全检查器，但要注意风险
#     # config='path/to/stable_diffusion_v1_5',
#     use_safetensors=True,
#     local_files_only=True
# )

model_id = r"E:\models\MusePublic\majicMIX_realistic_maijuxieshi_SD_1_5\majicmixRealistic_v7.safetensors"
# 使用第三方checkpoint生成图片，需要指定原生SD的config位置
pipe = StableDiffusionPipeline.from_single_file(
    model_id,
    torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32,
    safety_checker=None,  # 可以移除安全检查器，但要注意风险
    config=r'E:\models\AI-ModelScope\stable-diffusion-v1-5',
    use_safetensors=True,
    local_files_only=True
)
pipe = pipe.to(device)

# 加载 LoRA 权重
lora_path = r"E:\models\yangshaoping\ysp123majicMIX"  # 替换为你的 LoRA 文件路径
pipe.load_lora_weights(lora_path, weight_name="ysp123majicMIX.safetensors", alpha=0.7)

# 采样方式
pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config)

# 设置固定的随机种子（例如 42）
seed = 42
generator = torch.Generator("cuda").manual_seed(seed)


# 定义生成函数
def generate_image(prompt, negative_prompt, num_images=1, guidance_scale=7.5, num_inference_steps=30, height=512,
                   width=512):
    """
    使用Stable Diffusion生成图像

    参数:
    - prompt: 文本提示词
    - num_images: 生成图像数量
    - guidance_scale: 引导系数，控制文本对生成的影响程度
    - height, width: 图像高度和宽度，必须是8的倍数
    """
    print(f"正在生成图像: '{prompt}'")

    # 生成图像
    images = pipe(
        prompt,
        negative_prompt=negative_prompt,
        num_images_per_prompt=num_images,
        guidance_scale=guidance_scale,
        num_inference_steps=num_inference_steps,  # 控制采样步数的参数
        height=height,
        width=width,
        generator=generator
    ).images

    return images


# 示例用法
if __name__ == "__main__":
    # 设置提示词
    prompt = "1girl,korean,long wavy hair,black silk stockings,dress,stand"
    negative_prompt = "old,ugly"
    # 生成图像
    images = generate_image(prompt, negative_prompt, num_images=2)

    # 显示图像
    for i, image in enumerate(images):
        plt.subplot(1, len(images), i + 1)
        plt.imshow(image)
        plt.axis('off')

    plt.tight_layout()
    plt.show()

    # 保存图像
    # for i, image in enumerate(images):
    #     image.save(f"generated_image_{i}.png")
    #     print(f"图像已保存为: generated_image_{i}.png")
