<template>
  <div>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>工具箱</el-breadcrumb-item>
      <el-breadcrumb-item>模型量化</el-breadcrumb-item>
    </el-breadcrumb>
    <el-row>
      <el-col :span="12" class="card-box">
        <el-card class="card">
          <div slot="header"><span><i class="el-icon-edit"></i> 量化</span></div>
          <el-form ref="form1" :rules="rules1" :model="form1" label-width="80px" v-show="step === 1">
            <el-form-item label="模型" prop="model">
              <el-select v-model="form1.model" placeholder="请选择" @change="modelChange">
                <el-option v-for="item in modelList" :key="item.id" :label="item.name"
                           :value="item.id"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="文件名" prop="file">
              <el-select v-model="form1.file" placeholder="请选择">
                <el-option v-for="item in fileList" :key="item.id" :label="item.file_name"
                           :value="item.file_path"></el-option>
              </el-select>
            </el-form-item>
          </el-form>
          <el-form ref="form2" :rules="rules2" :model="form2" label-width="80px" v-show="step === 2">
            <el-form-item label="量化精度" prop="quantizeParam">
              <el-select v-model="form2.quantizeParam" placeholder="请选择">
                <el-option v-for="item in supportedQuantizeList" :key="item" :label="item"
                           :value="item"></el-option>
              </el-select>
            </el-form-item>
          </el-form>
          <el-form ref="form3" :rules="rules3" :model="form3" label-width="80px" v-show="step === 3">
            <el-form-item label="输出路径" prop="output">
              <el-input type="text" v-model="form3.output" placeholder="输出gguf文件的位置"></el-input>
            </el-form-item>
            <el-form-item label="异步执行">
              <el-switch v-model="form3.async"></el-switch>
              <i style="color: #909399;"> 默认同步执行，开启则会在后台执行，不会阻塞页面</i>
            </el-form-item>
          </el-form>
          <div class="stepButton">
            <el-button type="info" size="small" :disabled="step === 1" @click="back()">上一步</el-button>
            <el-button type="primary" size="small" @click="next('form1')"
                       v-show="step === 1">下一步
            </el-button>
            <el-button type="primary" size="small" @click="next('form2')"
                       v-show="step === 2">下一步
            </el-button>
            <el-button type="primary" size="small" @click="submit('form3')"
                       v-show="step >= 3">提交
            </el-button>
          </div>
          <el-steps :active="step">
            <el-step title="选择模型" description="选择需要量化的模型文件"></el-step>
            <el-step title="设置量化参数" description="设置量化的参数"></el-step>
            <el-step title="指定输出目录" description="量化模型的保存目录"></el-step>
          </el-steps>
        </el-card>
      </el-col>
      <el-col :span="12" class="card-box">
        <el-card class="card">
          <div slot="header"><span><i class="el-icon-edit"></i> 操作历史</span></div>
          <el-table :data="tableData" style="width: 100%">
            <el-table-column type="expand">
              <template slot-scope="props">
                <el-form label-position="left" inline class="demo-table-expand">
                  <el-form-item label="输入文件">
                    <span>{{ props.row.input }}</span>
                  </el-form-item>
                  <el-form-item label="输出文件">
                    <span>{{ props.row.output }}</span>
                  </el-form-item>
                </el-form>
              </template>
            </el-table-column>
            <el-table-column label="执行时间" prop="create_time">
            </el-table-column>
            <el-table-column label="量化精度" prop="param">
            </el-table-column>
          </el-table>
          <div class="block">
            <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange"
                           :current-page="currentPage" :page-sizes="pageSizes" :page-size="pageSize"
                           layout="total, sizes, prev, pager, next, jumper" :total="total">
            </el-pagination>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import apis from "../../../common/apis";
import {endLoading, startLoading} from "../../../common/common";

export default {
  name: "quantization",
  data() {
    return {
      total: 0,
      pageSize: 5,
      pageSizes: [5, 10, 20],
      currentPage: 1,
      tableData: [],
      step: 1,
      form1: {
        model: '',
        file: ''
      },
      modelList: [],
      fileList: [],
      rules1: {
        model: [
          {required: true, message: '请输入模型名称', trigger: 'blur'}
        ], file: [
          {required: true, message: '请输入文件名称', trigger: 'blur'}
        ],
      },
      supportedQuantizeList: [],
      form2: {
        quantizeParam: ''
      },
      rules2: {
        quantizeParam: [
          {required: true, message: '请输入量化精度', trigger: 'blur'}
        ],
      },
      form3: {
        output: '',
        async: true
      },
      rules3: {
        output: [
          {required: true, message: '请输入GGUF文件输出全路径', trigger: 'blur'}
        ],
      }
    }
  },
  created() {
    this.getModelList()
    this.getSupportedQuantize()
    this.getTableData()
  },
  methods: {
    getSupportedQuantize() {
      apis.listQuantizeParams().then(res => {
        this.supportedQuantizeList = res
      }).catch(e => {
        this.$message.error(e)
      })
    },
    back() {
      this.step--
    },
    getModelList() {
      apis.modelList(1, 9999).then(res => {
        this.modelList = JSON.parse(res).record
      }).catch(e => {
        this.$message.error(e)
      })

    },
    modelChange(modelId) {
      this.getFileList(modelId)
    },
    getFileList(modelId) {
      apis.fileList({modelId: modelId, ggufOnly: true}).then(res => {
        this.fileList = JSON.parse(res)
      }).catch(e => {
        this.$message.error(e)
      })
    },
    next(form) {
      this.$refs[form].validate((valid) => {
        if (valid) {
          this.step++
        }
      })
    },
    submit(form) {
      this.$refs[form].validate((valid) => {
        if (valid) {
          this.step++
        }
        const req = {
          input: this.form1.file,
          qType: this.form2.quantizeParam,
          output: this.form3.output,
          async: this.form3.async
        }
        if (this.step >= 3) {
          const loading = startLoading("量化中")
          apis.quantize(req).then(res => {
            endLoading(loading)
            console.log(res)
          }).catch(e => {
            endLoading(loading)
            this.$message.error(e)
          })
        }
      })
    },
    handleSizeChange(pageSize) {
      this.pageSize = pageSize
      this.getTableData()
    },
    handleCurrentChange(current) {
      this.currentPage = current
      this.getTableData()
    },
    getTableData() {
      apis.listQuantize({page: this.currentPage, limit: this.pageSize})
        .then(res => {
          const data = JSON.parse(res)
          this.tableData = data.record
          this.total = data.total
        }).catch(e => {
        this.$message.error(e)
      })
    }
  }
}
</script>

<style>
.stepButton {
  margin: 10px auto;
  height: 50px;
}
</style>
