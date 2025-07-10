import torch
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler, DDIMScheduler, DPMSolverMultistepScheduler, \
    LMSDiscreteScheduler, PNDMScheduler
import matplotlib.pyplot as plt
from random import randint
from jllama.util.logutil import Logger
from enum import Enum

logger = Logger("sd_reasoning")


class SDScheduler(Enum):
    """
    | 调度器 | 速度 | 质量 | 推荐步数 | 特点 |
    | ------------------- | ------ | ------ | ---------- | -------------------------- |
    | DPMSolverMultistep | ⭐⭐⭐⭐ | ⭐⭐⭐ | 10 - 20 | 最快，适合快速原型 |
    | EulerDiscrete | ⭐⭐⭐ | ⭐⭐⭐⭐ | 20 - 30 | 快速且质量高 |
    | LMSDiscrete | ⭐⭐ | ⭐⭐⭐⭐ | 30 - 50 | 高质量，传统选择 |
    | PNDMS | ⭐⭐ | ⭐⭐⭐ | 30 - 50 | 默认，平衡速度和质量 |
    | DDIM | ⭐⭐⭐ | ⭐⭐⭐ | 20 - 50 | 确定性，适合图像编辑 |
    """
    DPM = DPMSolverMultistepScheduler
    Euler = EulerDiscreteScheduler
    LMS = LMSDiscreteScheduler
    PNDM = PNDMScheduler
    DDIM = DDIMScheduler


def supported_scheduler(scheduler: str) -> bool:
    """
    检查调度器是否被支持
    """
    return scheduler in SDScheduler.__members__


def list_schedulers() -> list:
    """
    列出所有支持的调度器
    """
    return [k for k in SDScheduler.__members__]


def generate_pic(sd_origin_model_path, prompt: str, negative_prompt: str = None, checkpoint_path: str = None,
                 lora_path: str = None,
                 num_images=1, guidance_scale=7.5, seed=-1, scheduler="Euler",
                 num_inference_steps=30, lora_alpha=0.7, height=512, width=512):
    # 设置设备
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"使用设备: {device}")
    torch_dtype = torch.bfloat16 if device == "cuda" else torch.float32
    logger.info("开始加载SD模型")
    # 使用第三方checkpoint生成图片，需要指定原生SD的config位置
    if checkpoint_path:
        logger.info(f"使用第三方checkpoint生成图片: {checkpoint_path}")
        pipe = StableDiffusionPipeline.from_single_file(
            checkpoint_path,
            torch_dtype=torch_dtype,
            safety_checker=None,  # 可以移除安全检查器，但要注意风险
            config=sd_origin_model_path,
            use_safetensors=True,
            local_files_only=True,
        )
    else:
        logger.info(f"使用原生SD模型生成图片: {sd_origin_model_path}")
        # 使用原生sd模型生成图片
        pipe = StableDiffusionPipeline.from_pretrained(
            sd_origin_model_path,
            torch_dtype=torch_dtype,
            safety_checker=None,  # 可以移除安全检查器，但要注意风险
            use_safetensors=True,
            local_files_only=True
        )
    pipe = pipe.to(device)

    if lora_path:
        # 加载 LoRA 权重
        logger.info(f"加载第三方LoRA: {lora_path}")
        pipe.load_lora_weights(lora_path, alpha=lora_alpha)

    # 采样方式
    pipe.scheduler = SDScheduler[scheduler].value.from_config(pipe.scheduler.config)

    if seed < 0:
        # 获取随机种子
        seed = randint(1, 100000)
        logger.info(f"获取随机种子，seed={seed}")
    else:
        logger.info(f"使用指定种子，seed={seed}")

    generator = torch.Generator(device).manual_seed(seed)

    """
       使用Stable Diffusion生成图像

       参数:
       - prompt: 正向提示词
       - negative_prompt: 逆向提示词
       - num_images_per_prompt: 生成图像数量
       - guidance_scale: 引导系数，控制文本对生成的影响程度
       - height, width: 图像高度和宽度，必须是8的倍数
       - num_inference_steps: 控制采样步数的参数
       - generator: 图片生成的种子，相同的种子会生成相同的图片
       - callback_on_step_end: SD推理的callback函数，用于监控推理进度
       """
    logger.info(f"开始生成图像: '{prompt}'")

    # 生成图像
    images = pipe(
        prompt,
        negative_prompt=negative_prompt,
        num_images_per_prompt=num_images,
        guidance_scale=guidance_scale,
        num_inference_steps=num_inference_steps,
        height=height,
        width=width,
        generator=generator,
        callback_on_step_end=SimpleSDCallback(log_step=5, total_step=num_inference_steps),
    ).images
    logger.info(f"生成完成")

    del pipe
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    logger.info(f"已卸载模型")
    return images, seed


# 定义回调函数
class SimpleSDCallback:

    def __init__(self, total_step: int, log_step=5):
        self.log_step = log_step
        self.total_step = total_step

    def __call__(self, pipeline, step_index, timestep, callback_kwargs):
        step = step_index + 1
        if step_index % self.log_step == 0:
            logger.info(f"step: {step}/{self.total_step}")
        if step == self.total_step:
            logger.info(f"step: {step}/{self.total_step}")
        return callback_kwargs


# 示例用法
if __name__ == "__main__":
    print(list_schedulers())
    print(supported_scheduler("Euler"))

    # 设置提示词
    prompt = "(a beautiful woman in a deep v-neck evening gown,full body,beautiful detailed eyes,beautiful detailed lips,extremely detailed eyes and face,long eyelashes,graceful posture,elegant demeanor,smiling,flowing hair,sparkling jewelry,red carpet,glamorous,high fashion,richly textured fabric,silky smooth,shimmering,refined,alluring,confident,(best quality,4k,8k,highres,masterpiece:1.2),ultra-detailed,(realistic,photorealistic,photo-realistic:1.37),HDR,studio lighting,ultra-fine painting,sharp focus,physically-based rendering,extreme detail description,professional,vivid colors,bokeh,portrait,fashion photography,evening atmosphere,warm tones,soft lighting)"
    negative_prompt = "old,ugly"
    # 生成图像
    images, seed = generate_pic(sd_origin_model_path=r"E:\models\AI-ModelScope\stable-diffusion-v1-5",
                                checkpoint_path=r"E:\models\MusePublic\majicMIX_realistic_maijuxieshi_SD_1_5\majicmixRealistic_v7.safetensors",
                                lora_path=r"E:\models\yangshaoping\ysp123majicMIX\ysp123majicMIX.safetensors",
                                prompt=prompt,
                                negative_prompt=negative_prompt, num_images=2, guidance_scale=3)
    print(f"种子: {seed}")
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
