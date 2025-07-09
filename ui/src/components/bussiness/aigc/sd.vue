<template>
  <div>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>AIGC专区</el-breadcrumb-item>
      <el-breadcrumb-item>StableDiffusion绘图</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card>
      <el-row>
        <el-col :span="12">
          <div class="sd-info">
            <div>SD环境状态：
              <el-tag>{{ sd_info.state }}</el-tag>
            </div>
            <div>SD基础模型保存目录：<u>{{ sd_info.main_model_path }}</u></div>
            <div>SD版本：<u>{{ sd_info.sd_version }}</u></div>
            <div>常用AIGC社区：&nbsp;&nbsp;
              <a href="https://www.liblib.art/" target="_blank">liblib art</a>&nbsp;&nbsp;&nbsp;&nbsp;
              <a href="https://www.aigccn.cc/" target="_blank">AIGC社区</a>&nbsp;&nbsp;&nbsp;&nbsp;
              <a href="https://modelscope.cn/aigc/models" target="_blank">ModelScope AIGC</a>
            </div>
            <div>
              <el-button @click="initSd" type="primary" size="small" v-if="sd_info.state === '待初始化'">初始化
              </el-button>
            </div>
            <div v-if="sd_info.state ==='已初始化'">
              <el-form :model="sd_reasonning" ref="form" :rules="rules">
                <el-form-item label="正向提示词" prop="prompt">
                  <el-input type="textarea" v-model="sd_reasonning.prompt" placeholder="用来引导SD模型生成图片的自然语言。建议使用单词+,拼接的方式。例：1girl,long hair,stand,dress"></el-input>
                </el-form-item>
                <el-form-item label="反向提示词" prop="negative_prompt">
                  <el-input type="textarea" v-model="sd_reasonning.negative_prompt" placeholder="用于引导SD模型不要在生成图片时使用的风格"></el-input>
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
                  <el-button type="primary" @click="onSubmit(form)">提交</el-button>
                </el-form-item>
              </el-form>
            </div>
          </div>
        </el-col>
        <el-col>

        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script>
import apis from "../../../common/apis"
import {endLoading, startLoading} from "../../../common/common"

export default {
  data() {
    return {
      sd_info: {
        state: '待初始化'
      },
      sd_reasonning: {
        seed: -1,
        scheduler: 'Euler',
        num_inference_steps: 30,
        img_num: 2,
        img_height: 512,
        img_width: 512
      },
      rules: {
        prompt: [
          {required: true, message: '请输入正向提示词', trigger: 'blur'}
        ],

      },
    }
  },
  created() {
    this.getSdInfo()
  },
  methods: {
    getSdInfo() {
      apis.getSdInfo().then(res => {
        this.sd_info = JSON.parse(res)
      }).catch(e => {
        this.$message.error(e)
      })
    },
    initSd() {
      const loading = startLoading("SD模型下载中")
      apis.initSd().then(res => {
        endLoading(loading)
        this.$message.success("SD环境初始化完成")
        this.getSdInfo()
      }).catch(e => {
        endLoading(loading)
        this.$message.error(e)
      });
    },
    onSubmit(form) {
      this.$refs[form].validate((valid) => {
        if (valid) {

        }
      })
    },
  }
}
</script>

<style>
.sd-info {
  line-height: 30px;
}
</style>
