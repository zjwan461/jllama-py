<template>
  <div>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>设置</el-breadcrumb-item>
    </el-breadcrumb>
    <el-card>
      <el-row>
        <el-col :span="12">
          <el-form :model="settings" :rules="rules" class="setting-form" label-width="160px">
            <el-form-item label="模型存放目录" prop="model_save_dir">
              <el-input v-model="settings.model_save_dir" placeholder="模型存放目录"></el-input>
            </el-form-item>
            <el-form-item label="LlamaFactory服务端口">
              <el-input-number v-model="settings.llama_factory_port"></el-input-number>
            </el-form-item>
            <el-form-item label="微调log step">
              <el-input-number v-model="settings.train_log_step"></el-input-number>
            </el-form-item>
            <el-form-item label="http网络代理" prop="http_proxy">
              <el-input v-model="proxy.http_proxy" placeholder="http代理"></el-input>
            </el-form-item>
            <el-form-item label="https网络代理" prop="http_proxy">
              <el-input v-model="proxy.https_proxy" placeholder="https代理"></el-input>
            </el-form-item>
            <el-form-item label="AIGC最小种子数" prop="min_seed">
              <el-input-number v-model="aigc.min_seed"></el-input-number>
            </el-form-item>
            <el-form-item label="AIGC最大种子数" prop="min_seed">
              <el-input-number v-model="aigc.max_seed"></el-input-number>
            </el-form-item>
            <el-form-item label="AIGC log step" prop="aigc_log_step">
              <el-input-number v-model="aigc.log_step"></el-input-number>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="save">提交</el-button>
            </el-form-item>
          </el-form>
        </el-col>
        <el-col :span="12">
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script>
import {startLoading, endLoading} from "../common/common";
import apis from "../common/apis";

export default {
  data() {
    return {
      envInit: '',
      rules: {
        model_save_dir: [
          {required: true, message: '模型保存目录必填', trigger: 'blur'}
        ]
      },
      settings: {
        llama_cpp_dir: '',
        model_save_dir: '',
        llama_factory_port: '',
        train_log_step: 5
      },
      proxy: {
        http_proxy: '',
        https_proxy: ''
      },
      aigc: {
        min_seed: 1,
        max_seed: 9999999999,
        log_step: 5
      }
    }
  },
  created() {
    this.getSettings()
  },
  methods: {
    save() {
      const req = {"ai_config": this.settings, "proxy": this.proxy, "aigc": this.aigc}
      apis.saveSetting(req).then(res => {
        if (res === 'success') {
          this.$message.success("更新成功")
        }
      }).catch(e => {
        this.$message.error(e)
      })
    },
    getSettings() {
      const loading = startLoading()
      apis.getSetting().then(res => {
        endLoading(loading)
        this.settings = res.ai_config
        this.proxy = res.proxy ? res.proxy : {}
        this.aigc = res.aigc ? res.aigc : {}
      }).catch(e => {
        endLoading(loading)
        this.$message.error(e)
      })
    },

  },
}
</script>

<style lang="less" scoped>
.setting-form {
  padding: 0 20px;
}
</style>
