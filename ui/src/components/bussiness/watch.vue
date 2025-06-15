<template>
  <div>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>模型进程</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card>
      <el-form :inline="true" :model="formInline" class="demo-form-inline">
        <el-form-item label="搜索">
          <el-input v-model="formInline.search" placeholder="搜索运行中的模型"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="getTableData">查询</el-button>
          <el-button type="success" @click="addNew">运行</el-button>
        </el-form-item>
      </el-form>
      <el-table
        :data="tableData"
        border
        style="width: 100%"
      >
        <el-table-column
          prop="model_name"
          label="模型名称">
        </el-table-column>
        <el-table-column
          width="60"
          prop="model_type"
          label="类型">
        </el-table-column>
        <el-table-column
          prop="file_path"
          label="文件路径">
        </el-table-column>
        <el-table-column
          prop="reasoning_args"
          label="运行参数">
        </el-table-column>
        <el-table-column
          fixed="right"
          label="操作"
          width="160">
          <template slot-scope="scope">
            <el-button @click="chat(scope.row, scope.$index)" type="primary" size="small">chat</el-button>
            <el-button @click="stop(scope.row, scope.$index)" type="danger" size="small">停止</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="block">
        <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page="currentPage"
                       :page-sizes="pageSizes" :page-size="pageSize" layout="total, sizes, prev, pager, next, jumper"
                       :total="total">
        </el-pagination>
      </div>
    </el-card>

    <el-dialog title="创建服务进程"
               :visible.sync="showDialog"
               :close-on-press-escape=false
               :close-on-click-modal=false
               :destroy-on-close=true
               width="800px"
               @close="resetDialog"
    >
      <el-form :model="modelForm" :rules="rules" ref="modelForm">
        <el-form-item label="模型" label-width="120px" prop="modelId">
          <el-select v-model="modelForm.modelId" placeholder="模型" @change="modelChange">
            <el-option v-for="item in modelList" :key="item.id" :label="item.name" :value="item.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="文件名" label-width="120px" prop="fileId" v-if="selectedModel.type ==='gguf'">
          <el-select v-model="modelForm.fileId" placeholder="文件名">
            <el-option v-for="item in fileList" :key="item.id" :label="item.file_name" :value="item.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="-ngl" label-width="120px" prop="ngl" v-if="selectedModel.type ==='gguf'">
          <el-input
            type="number"
            placeholder="存储在 VRAM 中的层数,通常数值越大性能越好,但是过大也会导致显存不足"
            v-model="modelForm.ngl"
            show-word-limit
          >
          </el-input>
        </el-form-item>
        <el-form-item label="-t" label-width="120px" prop="threads" v-if="selectedModel.type ==='gguf'">
          <el-input
            type="number"
            placeholder="生成期间使用的线程数（默认值：-1）"
            v-model="modelForm.threads"
            show-word-limit
          >
          </el-input>
        </el-form-item>
        <el-form-item label="-c" label-width="120px" prop="ctxSize" v-if="selectedModel.type ==='gguf'">
          <el-input
            type="number"
            placeholder="提示上下文的大小（默认值：4096，0 = 从模型加载）"
            v-model="modelForm.ctxSize"
            show-word-limit
          >
          </el-input>
        </el-form-item>
        <el-form-item label="其他参数" label-width="120px" prop="args" v-if="selectedModel.type ==='gguf'">
          <el-input type="textarea" v-model="modelForm.args" placeholder="其他llama.cpp参数"></el-input>
        </el-form-item>
        <el-form-item label="temperature" label-width="120px" prop="temperature">
          <el-input
            v-model="modelForm.temperature"
            placeholder="请输入0.0-1.0之间的小数"
            clearable
          >
          </el-input>
        </el-form-item>
        <el-form-item label="top_k" label-width="120px" prop="top_k">
          <el-input
            v-model="modelForm.top_k"
            placeholder="请输入0.0-1.0之间的小数"
            clearable
          >
          </el-input>
        </el-form-item>
        <el-form-item label="top_p" label-width="120px" prop="top_p">
          <el-input
            v-model="modelForm.top_p"
            placeholder="请输入0.0-1.0之间的小数"
            clearable
          >
          </el-input>
        </el-form-item>
        <el-form-item label="流式输出" label-width="120px" prop="stream">
          <el-switch v-model="modelForm.stream"></el-switch>
          <i style="color: #909399;">
            大模型流式输出即文本逐字实时生成显示，如果不开启则需要等待模型完成推理后再生产显示</i>
        </el-form-item>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="exec('modelForm')">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {copy, getRequestBodyJson} from '@/common/common'
import apis from "../../common/apis";
import {endLoading, startLoading} from "../../common/common";

export default {
  name: 'watch',
  data() {
    return {
      showDialog: false,
      modelForm: {
        modelId: '',
        fileId: '',
        ngl: 99,
        threads: -1,
        ctxSize: 0,
        temperature: '0.8',
        top_p: 0.90,
        top_k: 40,
        stream: true
      },
      selectedModel: {},
      modelList: [],
      fileList: [],
      rules: {
        modelId: [
          {required: true, message: '请输入模型名称', trigger: 'blur'}
        ],
        stream: [
          {required: true, message: '请确认是否开启流式输出', trigger: 'blur'}
        ],
        temperature: [
          {pattern: /^(0(\.\d+)?|1(\.0+)?)$/, message: '请输入0.1-1.0之间的小数', trigger: 'blur'}
        ],
        top_k: [
          {pattern: /[1-9]\d*/, message: '请输入数字', trigger: 'blur'}
        ],
        top_p: [
          {pattern: /^(0(\.\d+)?|1(\.0+)?)$/, message: '请输入0.1-1.0之间的小数', trigger: 'blur'}
        ],
      },
      formInline: {
        search: ''
      },
      tableData: [],
      currentPage: 1,
      pageSize: 10,
      total: 0,
      pageSizes: [10, 20, 50],
    }
  },
  created() {
    this.getModelList()
    this.getTableData()
  },
  methods: {
    handleSizeChange(pageSize) {
      this.pageSize = pageSize
      this.getTableData()
    },
    handleCurrentChange(current) {
      this.currentPage = current
      this.getTableData()
    },
    chat(row, index) {
      this.$router.push({
        path:'/ai/chat',
        query: row.model_id
      })
    },
    stop(row, index) {
      this.$http.get('/api/process/stop/' + row.execId).then(res => {
        if (res.success === true) {
          this.$message({
            type: 'success',
            message: '停止成功'
          })
          this.getTableData()
        }
      })
    },
    async modelChange(modelId) {
      await this.getModel(modelId)
      if (this.selectedModel.type === 'gguf') {
        this.getFileList(modelId);
      }
    },
    resetDialog() {
      this.showDialog = false
      this.modelForm = {
        modelId: '',
        fileId: '',
        ngl: 99,
        threads: -1,
        ctxSize: 0,
        temperature: '0.8',
        top_p: 0.90,
        top_k: 40,
        stream: true
      }
      this.selectedModel = {}
      this.getTableData()
    },
    addNew() {
      this.showDialog = true
    },
    exec(form) {
      this.$refs[form].validate((valid) => {
        if (valid) {
          const loading = startLoading()
          apis.runModel(this.modelForm).then(res => {
            endLoading(loading)
            if (res === 'success') {
              this.$message.success('运行成功')
            }
          }).catch(e => {
            endLoading(loading)
            this.$message.error(e)
          })
        }
      })
    },
    getTableData() {
      const loading = startLoading()
      apis.listRunningModel({
        page: this.currentPage,
        limit: this.pageSize,
        search: this.formInline.search
      }).then(res => {
        endLoading(loading)
        const data = JSON.parse(res)
        this.tableData = data.record
        this.total = data.total
      }).catch(e => {
        endLoading(loading)
        this.$message.error(e)
      });
    },
    async getModel(modelId) {
      await apis.getModel(modelId).then(res => {
        this.selectedModel = JSON.parse(res)
      }).catch(e => {
        this.$message.error(e);
      })
    },
    getModelList() {
      apis.modelList(1, 9999).then(res => {
        const data = JSON.parse(res)
        this.modelList = data.record
      }).catch(e => {
        this.$message.error(e);
      })
    },
    getFileList(modelId) {
      apis.fileList({modelId: modelId, ggufOnly: true}).then(res => {
        this.fileList = JSON.parse(res)
      }).catch(e => {
        this.$message.error(e)
      })
    }
  }
}
</script>

<style>
.logDialog {
  white-space: pre-line;
  overflow-y: auto;
  height: 60vh
}
</style>
