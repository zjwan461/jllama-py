<template>
  <div>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>AIGC专区</el-breadcrumb-item>
      <el-breadcrumb-item>IP-Adapter-FaceID</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card>
      <el-row>
        <el-col :span="12">
          <div>
            <SdInfo :sd_info="sd_info" @getSdInfo="getSdInfo" @getIpAdapterModels="getIpAdapterModels"></SdInfo>
            <div v-if="sd_info.state ==='已初始化'">
              <el-form :model="sd_reasonning" ref="form" :rules="rules">
                <el-form-item label="上传原图" prop="input_img">
                  <el-input v-show="false" v-model="sd_reasonning.input_img" disabled></el-input>
                  <br>
                  <el-upload
                    drag
                    list-type="picture"
                    :multiple=false
                    :accept="'image/*'"
                    :auto-upload=true
                    :file-list="fileList"
                    :limit=1
                    :on-success="uploadSuccess"
                    :before-upload="beforeUpload"
                    :on-remove="fileRemove"
                    :on-exceed="exceed"
                    :action="uploadUrl">
                    <i class="el-icon-upload"></i>
                    <div class="el-upload__text">将图片拖到此处，或<em>点击上传</em></div>
                    <div class="el-upload__tip" slot="tip">只能上传jpg/png等图片文件</div>
                  </el-upload>
                </el-form-item>
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
                    <el-input-number :precision="2" :step="0.01" :max="1" :min="0.01" v-model="sd_reasonning.lora_alpha"
                                     placeholder="lora影响系数"></el-input-number>
                  </el-col>
                </el-form-item>
                <el-form-item label="IP-Adapter-FaceID" prop="ip_adapter_faceid_model">
                  <el-select v-model="sd_reasonning.ip_adapter_faceid_model">
                    <el-option label="ip-adapter-faceid_sd15.bin" value="ip-adapter-faceid_sd15.bin"></el-option>
                    <el-option label="ip-adapter-faceid-plusv2_sd15.bin"
                               value="ip-adapter-faceid-plusv2_sd15.bin"></el-option>
                  </el-select>
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
              <el-empty description="AIGC IP-Adapter-FaceID"></el-empty>
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
import {closestMultipleOf8} from "../../../common/common"
import ImageViewer from '@/components/ImageViewer.vue';
import SdInfo from '@/components/SdInfo.vue';


export default {
  components: {
    ImageViewer,
    SdInfo
  },
  data() {
    return {
      ipAdapterModels: [],
      uploadUrl: "http://127.0.0.1:5000/upload",
      fileList: [],
      current_seed: -1,
      loading_img: false,
      viewerVisible: false,
      generate_imgs: [],
      sd_info: {
        state: '待初始化',
        ip_adapter_state: '待初始化',
        ip_adapter_faceid_state: '待初始化'
      },
      sd_reasonning: {
        input_img: '',
        prompt: '',
        negative_prompt: '',
        seed: -1,
        checkpoint: null,
        lora_alpha: 0.7,
        lora: null,
        scheduler: 'Euler',
        num_inference_steps: 30,
        guidance_scale: 3.0,
        img_num: 1,
        img_height: 512,
        img_width: 512,
      },
      rules: {
        prompt: [
          {required: true, message: '请输入正向提示词', trigger: 'blur'}
        ],
        input_img: [
          {required: true, message: '请选择图片', trigger: 'blur'}
        ],
        ip_adapter_faceid_model: [
          {required: true, message: '请选择IP-Adapter-FaceID模型', trigger: 'blur'}
        ]
      },
    }
  },
  created() {
    this.getSdInfo()
    this.getUploadUrl()
    this.getDefaultNegativePrompt()
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
        if (this.sd_info.state !== '已初始化') {
          this.$message.error('检测到未初始化SD基础环境，请初始化后使用此功能')
        } else if (this.sd_info.ip_adapter_faceid_state !== '已初始化') {
          this.$message.error('检测到未初始化IP-Adapter-FaceID环境，请初始化后使用此功能');
        }
      }).catch(e => {
        this.$message.error(e)
      })
    },
    onSubmit(form) {
      this.$refs[form].validate((valid) => {
        if (valid) {
          this.loading_img = true
          this.$message.success("开始生成图片")
          apis.sdIpAdapterFaceid(this.sd_reasonning).then(res => {
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
    },
    uploadSuccess(response, file, fileList) {
      this.sd_reasonning.input_img = response.file_path
      this.fileList = fileList
    },
    beforeUpload(file) {

    },
    fileRemove(file, fileList) {

    },
    exceed(files, fileList) {
      this.$message.warning("一次只能处理一张图")
    },
    getUploadUrl() {
      const base_url = this.$store.state.sysInfo.base_url
      if (base_url) {
        this.uploadUrl = base_url + "/upload"
      } else {
        console.log("未从store找到base_url,将使用默认http://127.0.0.1:5000/upload")
      }
    },
    getDefaultNegativePrompt() {
      apis.getDefaultNegativePrompt().then(res => {
        if (res && res.length > 0) {
          this.sd_reasonning.negative_prompt = res
        }
      }).catch(e => {
        this.$message.error(e)
      })
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
