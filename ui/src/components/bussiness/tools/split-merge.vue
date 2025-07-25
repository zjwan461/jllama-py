<template>
  <div>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>工具箱</el-breadcrumb-item>
      <el-breadcrumb-item>gguf拆分、合并</el-breadcrumb-item>
    </el-breadcrumb>
    <el-row>
      <el-col :span="12" class="card-box">
        <el-card class="card">
          <div slot="header"><span><i class="el-icon-scissors"></i> GGUF拆分、合并</span></div>
          <el-form ref="form" :rules="rules" :model="form" label-width="80px">
            <el-form-item label="操作选项" prop="options">
              <el-select v-model="form.options" placeholder="请选择操作选项" @change="handleChangeOptions">
                <el-option label="拆分" value="split"></el-option>
                <el-option label="合并" value="merge"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="输入文件" v-show="form.options === 'merge'">
              <el-input type="text" disabled v-model="form.input" placeholder="输入合并文件的目录和名称全路径">
              </el-input>
              <el-button size="small" type="primary" @click="openFileSelect('input')">选择文件</el-button>
              <br>
              <i
                style="color: #909399;">合并文件名规则：模型名-00001-of-00003.gguf。例如：DeepSeek-R1-Distill-Qwen-1.5B-Q2_K-00001-of-00003.gguf</i>
            </el-form-item>
            <el-form-item label="输入文件" v-show="form.options === 'split'">
              <el-input type="text" disabled v-model="form.input"
                        placeholder="输入拆分文件的目录和名称全路径"></el-input>
              <el-button size="small" type="primary" @click="openFileSelect('input')">选择文件</el-button>
            </el-form-item>
            <el-form-item label="拆分选项" v-show="form.options === 'split'">
              <el-radio-group v-model="form.splitOption" @change="handleSplitOptionChange">
                <el-radio label="--split-max-tensors"></el-radio>
                <el-radio label="--split-max-size"></el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="split参数" v-show="form.options === 'split'">
              <el-input type="text" v-model="form.splitParam" placeholder="split参数，参考如下"></el-input>
              <i
                style="color: #909399">对于split-max-tensors为拆分的tensors张量（如：256），对于split-max-size则为拆分的文件大小（如：1G/512M）</i>
            </el-form-item>
            <el-form-item label="输出文件" prop="output">
              <el-input type="text" v-model="form.output" placeholder="输出文件的目录和名称全路径"></el-input>
              <el-button size="small" type="primary" @click="openFileSelect('output')">选择文件</el-button>
              <br>
            </el-form-item>
            <el-form-item label="异步执行">
              <el-switch v-model="form.async"></el-switch>
              <i style="color: #909399;"> 默认同步执行，开启则会在后台执行，不会阻塞页面</i>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="onSubmit('form')">提交</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="12" class="card-box">
        <el-card class="card">
          <div slot="header"><span><i class="el-icon-scissors"></i> 调用历史</span></div>
          <el-table :data="tableData" style="width: 100%">
            <el-table-column type="expand">
              <template slot-scope="props">
                <el-form label-position="left" inline class="demo-table-expand">
                  <el-form-item label="分割选项">
                    <span>{{ props.row.split_option }}</span>
                  </el-form-item>
                  <el-form-item label="分割参数">
                    <span>{{ props.row.split_param }}</span>
                  </el-form-item>
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
            <el-table-column label="选项" prop="option">
              <template slot-scope="scope">
                <el-tag
                  :type="scope.row.option === 'split' ? 'primary' : 'success'"
                  disable-transitions>{{ scope.row.option }}
                </el-tag>
              </template>
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
  name: "split-merge",
  data() {
    return {
      total: 0,
      pageSize: 5,
      pageSizes: [5, 10, 20],
      currentPage: 1,
      tableData: [],
      form: {
        options: 'split',
        input: '',
        output: '',
        splitOption: '--split-max-tensors',
        splitParam: '',
        async: true
      },
      rules: {
        options: [
          {required: true, message: '请输入参数选项', trigger: 'blur'}
        ], output: [
          {required: true, message: '请输入output文件地址', trigger: 'blur'}
        ],
      },
    }
  },
  created() {
    this.getTableData()
  },
  methods: {
    openFileSelect(val) {
      apis.openFileSelector().then(res => {
        if (res && res.length > 0) {
          this.form[val] = res[0]
        }
      }).catch(e => {
        this.$message.error(e)
      })
      return false
    },
    handleChangeOptions(e) {
      if (e === 'split') {
        this.form = {
          options: 'split',
          input: '',
          output: '',
          splitOption: '--split-max-tensors',
          splitParam: '',
          async: true
        }
      } else if (e === 'merge') {
        this.form = {
          options: 'merge',
          input: '',
          output: '',
          splitOption: '',
          splitParam: '',
          async: true
        }
      }
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
      apis.listSplitMerge({page: this.currentPage, limit: this.pageSize})
        .then(res => {
          const data = JSON.parse(res)
          this.total = data.total
          this.tableData = data.record
        }).catch(e => {
        this.$message.error(e)
      })
    },
    handleSplitOptionChange(e) {
    },
    onSubmit(form) {
      this.$refs[form].validate((valid) => {
        if (valid) {
          const loading = startLoading("合并/拆分中")
          apis.splitMergeGguf(this.form).then(res => {
            endLoading(loading)
            console.log(res)
          }).catch(e => {
            endLoading(loading)
            this.$message.error(e)
          })
        }
      })
    }
  }
}

</script>

<style scoped>
.card {
}

.demo-table-expand {
  font-size: 0;
}

.demo-table-expand label {
  width: 150px;
  margin-left: 10px;
  color: #99a9bf;
}

.demo-table-expand .el-form-item {
  margin-right: 0;
  margin-bottom: 0;
  width: 50%;
}
</style>
