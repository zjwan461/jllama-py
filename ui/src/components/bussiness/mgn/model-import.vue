<template>
  <div>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>模型管理</el-breadcrumb-item>
      <el-breadcrumb-item>模型导入</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card>
      <el-form ref="form" :model="form" label-width="80px">
        <el-form-item label="选择模型" prop="model">
          <el-select v-model="form.modelId" placeholder="请选择模型" @change="modelChange">
            <el-option v-for="item in modelList" :key="item.id" :label="item.name"
                       :value="item.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="输入文件">
          <el-button size="small" type="primary" :disabled="import_state" @click="doFileUpload()">点击上传</el-button>
          &nbsp;&nbsp;<i>支持多选</i>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import apis from "../../../common/apis";
import {endLoading, startLoading} from "../../../common/common";

export default {
  data() {
    return {
      form: {
        modelId: ''
      },
      import_state: false,
      modelList: [],
    }
  },
  created() {
    this.getModelList()
  },
  methods: {
    getModelList() {
      apis.modelList(1, 10000).then(res => {
        const resp = JSON.parse(res)
        this.modelList = resp.record
      })
    },
    modelChange() {
    },
    doImport(file_path) {
      const loading = startLoading()
      apis.importFile({file_path: file_path, model_id: this.form.modelId}).then(res => {
        endLoading(loading)
        if (res === "success") {
          this.$message.success("导入成功")
        }
      }).catch(e => {
        endLoading(loading)
        this.$message.error(e)
      })
    },
    doFileUpload() {
      if (this.beforeUpload()) {
        this.import_state = true
        apis.openFileSelector().then(res => {
          this.import_state = false
          if (res) {
            this.doImport(res)
          }
        }).catch(err => {
          this.$message.error(err)
          this.import_state = false
        })
      }
    },
    beforeUpload() {
      if (!this.form.modelId || this.form.modelId === '') {
        this.$message.error('请先选择模型')
        return false
      }
      return true
    }
  }
}
</script>

<style></style>
