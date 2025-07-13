<template>
  <div>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>AIGC专区</el-breadcrumb-item>
      <el-breadcrumb-item>StableDiffusion文生图</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card>
      <el-row>
        <el-col :span="12">
          <div>
            <SdInfo :sd_info="sd_info" @getSdInfo="getSdInfo"></SdInfo>
            <div v-if="sd_info.state ==='已初始化'">
              <el-form :model="sd_reasonning" ref="form" :rules="rules">
                <el-form-item label="正向提示词" prop="prompt">
                  <el-input type="textarea" v-model="sd_reasonning.prompt"
                            placeholder="用来引导SD模型生成图片的自然语言。建议使用单词+,拼接的方式。例：1girl,long hair,stand,dress"></el-input>
                </el-form-item>
                <el-form-item label="反向提示词" prop="negative_prompt">
                  <el-input type="textarea" v-model="sd_reasonning.negative_prompt"
                            placeholder="用于引导SD模型不要在生成图片时使用的风格"></el-input>
                </el-form-item>
                <el-form-item label="checkpoint">
                  <el-button size="mini" type="info" @click="openFileSelect('checkpoint')">选择文件</el-button>
                  <el-input v-model="sd_reasonning.checkpoint" placeholder="第三方checkpoint(全路径)"></el-input>
                </el-form-item>
                <el-form-item label="lora">
                  <el-button size="mini" type="info" @click="openFileSelect('lora')">选择文件</el-button>
                  <el-input v-model="sd_reasonning.lora" placeholder="第三方lora(全路径)"></el-input>
                </el-form-item>
                <el-form-item>
                  <el-col class="line" :span="3">种子</el-col>
                  <el-col :span="9">
                    <el-input-number v-model="sd_reasonning.seed"></el-input-number>
                  </el-col>
                  <el-col class="line" :span="3">采样方式</el-col>
                  <el-col :span="9">
                    <el-select v-model="sd_reasonning.scheduler">
                      <el-option value="Euler">Euler</el-option>
                      <el-option value="DPM">DPM</el-option>
                      <el-option value="LMS">LMS</el-option>
                      <el-option value="PNDM">PNDM</el-option>
                      <el-option value="DDIM">DDIM</el-option>
                    </el-select>
                  </el-col>
                </el-form-item>

                <el-form-item label="" prop="num_inference_steps">
                  <el-col class="line" :span="3">采样步数</el-col>
                  <el-col :span="9">
                    <el-input-number v-model="sd_reasonning.num_inference_steps"></el-input-number>
                  </el-col>
                  <el-col class="line" :span="3">图片张数</el-col>
                  <el-col :span="9">
                    <el-input-number v-model="sd_reasonning.img_num"></el-input-number>
                  </el-col>
                </el-form-item>

                <el-form-item label="" prop="img_height">
                  <el-col class="line" :span="3">图片宽度</el-col>
                  <el-col :span="9">
                    <el-input-number v-model="sd_reasonning.img_width"></el-input-number>
                  </el-col>
                  <el-col class="line" :span="3">图片高度</el-col>
                  <el-col :span="9">
                    <el-input-number v-model="sd_reasonning.img_height"></el-input-number>
                  </el-col>
                </el-form-item>
                <el-form-item>
                  <el-col class="line" :span="3">引导系数</el-col>
                  <el-col :span="9">
                    <el-input-number v-model="sd_reasonning.guidance_scale"
                                     placeholder="提示词引导系数"></el-input-number>
                  </el-col>
                  <el-col class="line" :span="3">lora系数</el-col>
                  <el-col :span="9">
                    <el-input-number :precision="2" :step="0.01" :max="1" v-model="sd_reasonning.lora_alpha"
                                     placeholder="lora影响系数"></el-input-number>
                  </el-col>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="onSubmit('form')">提交</el-button>
                </el-form-item>
              </el-form>
            </div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="image-area" v-loading="loading_img">
            <div v-if="generate_imgs.length==0" style="line-height: 28px">
              <el-image>
                <div slot="error" class="image-slot">
                  <i class="el-icon-picture-outline"></i>
                </div>
              </el-image>
            </div>
            <div style="text-align: center" v-if="current_seed !==-1">
              图片种子:
              <el-tag>{{ current_seed }}</el-tag>
            </div>
            <div v-if="generate_imgs.length>0" class="image-container" v-for="(image, index) in generate_imgs"
                 :key="index">
              <img
                :src="image"
                class="gallery-image"
                @click="viewImage(image)"
              >
              <div>
                <el-button type="text" size="mini" @click="saveImg(image)">保存图片</el-button>
              </div>
            </div>
          </div>
        </el-col>
        <image-viewer
          :visible.sync="viewerVisible"
          ref="imageViewerRef"
        ></image-viewer>
      </el-row>
    </el-card>
  </div>
</template>

<script>
import apis from "../../../common/apis"
import {endLoading, startLoading} from "../../../common/common"
import ImageViewer from '@/components/ImageViewer.vue';
import SdInfo from '@/components/SdInfo.vue';


export default {
  components: {
    ImageViewer,
    SdInfo
  },
  data() {
    return {
      current_seed: -1,
      loading_img: false,
      viewerVisible: false,
      generate_imgs: [],
      sd_info: {
        state: '待初始化'
      },
      sd_reasonning: {
        prompt: '',
        negative_prompt: '',
        seed: -1,
        checkpoint: null,
        lora_alpha: 0.7,
        lora: null,
        scheduler: 'Euler',
        num_inference_steps: 30,
        guidance_scale: 3.0,
        img_num: 2,
        img_height: 512,
        img_width: 512
      },
      rules: {
        prompt: [
          {required: true, message: '请输入正向提示词', trigger: 'blur'}
        ]

      },
    }
  },
  created() {
    this.getSdInfo()
  },
  methods: {
    openFileSelect(val) {
      apis.openFileSelector().then(res => {
        if (res && res.length > 0) {
          this.sd_reasonning[val] = res[0]
        }
      }).catch(e => {
        this.$message.error(e)
      })
      return false
    },
    getSdInfo() {
      apis.getSdInfo().then(res => {
        this.sd_info = JSON.parse(res)
      }).catch(e => {
        this.$message.error(e)
      })
    },
    onSubmit(form) {
      this.$refs[form].validate((valid) => {
        if (valid) {
          if (this.sd_reasonning.img_width % 8 !== 0) {
            this.$message.error("图片宽度必须为8的倍数")
            return false
          }
          if (this.sd_reasonning.img_height % 8 !== 0) {
            this.$message.error("图片高度必须为8的倍数")
            return false
          }
          this.loading_img = true
          this.$message.success("开始生成图片")
          apis.sdGeneratePic(this.sd_reasonning).then(res => {
            this.loading_img = false
            this.generate_imgs = res.images
            this.current_seed = res.seed
          }).catch(e => {
            this.loading_img = false
            this.$message.error(e)
          })
        }
      })
    },
    saveImg(image) {
      apis.saveImages(image).then(res => {
        if (res === "success") {
          this.$message.success("保存成功")
        }
      }).catch(e => {
        this.$message.error(e)
      })
    },
    viewImage(image) {
      this.$refs.imageViewerRef.loadImage(image);
      this.viewerVisible = true
    }
  }
}
</script>

<style>
.sd-info {
  line-height: 30px;
}

.image-area {
  overflow-y: auto;
  scroll-behavior: smooth;
  text-align: center;
}

.image-container {
  margin: 15px;
  text-align: center;
  transition: transform 0.3s;

}

.gallery-image {
  cursor: pointer;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  max-height: 300px;
}

</style>
