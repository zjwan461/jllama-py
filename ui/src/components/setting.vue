<template>
  <div>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>设置</el-breadcrumb-item>
    </el-breadcrumb>
    <el-card>
      <el-row>
        <el-col :span="12">
          <el-form :model="settings" :rules="rules" class="setting-form" label-width="160px">
            <el-form-item label="外挂llama.cpp目录" prop="llama_cpp_dir">
              <el-input v-model="settings.llama_cpp_dir" placeholder="填写此目录则会使用你外挂的llama.cpp"></el-input>
            </el-form-item>
            <el-form-item label="模型存放目录" prop="model_save_dir">
              <el-input v-model="settings.model_save_dir" placeholder=""></el-input>
            </el-form-item>
            <el-form-item label="LlamaFactory服务端口">
              <el-input-number v-model="settings.llama_factory_port"></el-input-number>
            </el-form-item>
            <el-form-item label="http网络代理" prop="http_proxy">
              <el-input v-model="proxy.http_proxy" placeholder="http代理"></el-input>
            </el-form-item>
            <el-form-item label="https网络代理" prop="http_proxy">
              <el-input v-model="proxy.https_proxy" placeholder="https代理"></el-input>
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
        llama_factory_port: ''
      },
      proxy: {
        http_proxy: '',
        https_proxy: ''
      }
    }
  },
  created() {
    this.getSettings()
  },
  methods: {
    save() {
      const req = {"ai_config": this.settings, "proxy": this.proxy}
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
        this.proxy = res.proxy
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
