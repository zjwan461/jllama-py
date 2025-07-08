import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import matplotlib.pyplot as plt

# 设置设备
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"使用设备: {device}")

# 加载模型
model_id = "runwayml/stable-diffusion-v1-5"  # 也可以选择其他模型
pipe = StableDiffusionPipeline.from_single_file(
    model_id,
    torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32,
    safety_checker=None,  # 可以移除安全检查器，但要注意风险
    config='path/to/stable_diffusion_v1_5',
    use_safetensors=True,
    local_files_only=True
)
pipe = pipe.to(device)


# 定义生成函数
def generate_image(prompt, num_images=1, guidance_scale=7.5, height=512, width=512):
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
        num_images_per_prompt=num_images,
        guidance_scale=guidance_scale,
        height=height,
        width=width
    ).images

    return images


# 示例用法
if __name__ == "__main__":
    # 设置提示词
    prompt = "一只可爱的柯基犬在花园里玩耍，阳光明媚，色彩鲜艳"

    # 生成图像
    images = generate_image(prompt, num_images=2)

    # 显示图像
    for i, image in enumerate(images):
        plt.subplot(1, len(images), i + 1)
        plt.imshow(image)
        plt.axis('off')

    plt.tight_layout()
    plt.show()

    # 保存图像
    for i, image in enumerate(images):
        image.save(f"generated_image_{i}.png")
        print(f"图像已保存为: generated_image_{i}.png")
