<template xmlns="http://www.w3.org/1999/html">
  <div>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>模型管理</el-breadcrumb-item>
      <el-breadcrumb-item>模型仓库</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card>
      <el-form :inline="true" :model="formInline" class="demo-form-inline">
        <el-form-item label="搜索">
          <el-input v-model="formInline.search" placeholder="搜索"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="getTableData">查询</el-button>
          <el-button type="success" @click="create">新增</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="tableData" border style="width: 100%" @expand-change="loadExpandData">
        <el-table-column type="expand">
          <template slot-scope="props">
            <el-form label-position="left" inline class="demo-table-expand">
              <el-form-item label="模型文件列表">
                <ul>
                  <li v-for="(item, index) in props.row.files" :key="index">{{ item.file_name }} &nbsp;&nbsp;&nbsp;&nbsp;
                    {{ item.type }} &nbsp;&nbsp;&nbsp;&nbsp;
                    {{ item.percent }} &nbsp;&nbsp;&nbsp;&nbsp;
                    <el-button type="text" size="small"
                               @click="delFile(item)">删除
                    </el-button>
                  </li>
                </ul>
              </el-form-item>
              <el-form-item label="存储目录">
                <span>{{ props.row.save_dir }}</span>
              </el-form-item>
              <el-form-item label="创建时间">
                <span>{{ props.row.create_time }}</span>
              </el-form-item>
            </el-form>
          </template>
        </el-table-column>
        <el-table-column prop="repo" label="repo">
        </el-table-column>
        <el-table-column prop="name" label="模型名称">
        </el-table-column>
        <el-table-column prop="type" label="模型类型">
        </el-table-column>
        <el-table-column prop="download_platform" label="下载平台">
        </el-table-column>
        <el-table-column fixed="right" label="操作" width="160">
          <template slot-scope="scope">
            <el-button @click="edit(scope.row, scope.$index)" type="primary" size="small">修改</el-button>
            <el-button @click="delModel(scope.row.id, scope.$index)" type="danger" size="small">删除</el-button>
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

    <el-dialog :title="dialogTitle" :visible.sync="showDialog" :close-on-press-escape=false :close-on-click-modal=false
               :destroy-on-close=true @close="resetDialog">
      <el-form :model="modelForm" :rules="rules" ref="modelForm">
        <el-form-item label="下载平台" label-width="120px" prop="download_platform">
          <el-select v-model="modelForm.download_platform" placeholder="下载平台">
            <el-option label="modelscope" value="modelscope"></el-option>
            <el-option label="huggingface" value="huggingface" :disabled="true"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="模型名称" label-width="120px" prop="name">
          <el-input v-model="modelForm.name" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="repo" label-width="120px" prop="repo">
          <el-input v-model="modelForm.repo" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="revision" label-width="120px">
          <el-input v-model="modelForm.revision" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="root" label-width="120px">
          <el-input v-model="modelForm.root" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="模型文件" label-width="120px">
          <el-table v-show="showModelFiles" :data="modelFiles" @selection-change="handleSelectionChange"
                    style="width: 100%">
            <el-table-column type="selection" width="55">
            </el-table-column>
            <el-table-column prop="Name" label="文件名" width="180">
            </el-table-column>
            <el-table-column prop="Size" label="文件大小" width="180">
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template slot-scope="scope">
                <el-button @click="download(scope.row, scope.$index)" type="text" size="small">下载</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="selectRepo('modelForm')" v-show="showSubmit">确 定</el-button>
        <el-button type="success" @click="download(undefined)" v-show="showDownload">下 载</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import apis from "../../../common/apis";
import {endLoading, startLoading} from "../../../common/common";

export default {
  name: 'model-download',
  data() {
    return {
      fluxCache: new Map(),
      model: {},
      multipleSelection: [],
      showSubmit: true,
      showDownload: false,
      modelFiles: [],
      showModelFiles: false,
      rules: {
        name: [
          {required: true, message: '请输入模型名称', trigger: 'blur'}
        ],
        repo: [
          {required: true, message: '请输入repo仓库名称', trigger: 'blur'}
        ],
        download_platform: [
          {required: true, message: '请输入下载平台', trigger: 'blur'}
        ]
      },
      modelForm: {
        download_platform: 'modelscope',
        revision: '',
        root: ''
      },
      dialogTitle: '新增模型',
      showDialog: false,
      formInline: {
        search: ''
      },
      tableData: [],
      total: 0,
      pageSize: 10,
      pageSizes: [10, 20, 50],
      currentPage: 1
    }
  },
  created() {
    this.getTableData()
  },
  methods: {
    delFile(item) {
      const loading = startLoading()
      apis.delFile(item.id).then(res => {
        endLoading(loading)
        if (res === "success") {
          this.$message.success(item.file_name + "已删除")
          this.reloadFiles(item.model_id)
        }
      }).catch(e => {
        endLoading(loading)
        this.$message.error(e)
      })
    },
    resetDialog() {
      this.modelForm = {
        download_platform: 'modelscope',
        revision: '',
        root: ''
      }
      this.getTableData()
      this.modelFiles = [];
      this.showModelFiles = false
      this.showDownload = false
      this.showSubmit = true
    },
    edit(row) {
      this.dialogTitle = '修改模型'
      this.showDialog = true
      this.modelForm = row
      if (!this.modelForm.revision) {
        this.modelForm.revision = ''
      }
      if (!this.modelForm.root) {
        this.modelForm.root = ''
      }
    },
    delModel(id) {
      this.$confirm('你确定要删除此模型配置？', '提示').then(() => {
        let req = {model_id: id}
        this.$confirm('是否删除已经下载的模型？').then(() => {
          req.del_file = true
          this.doDelModel(req)
        }).catch(() => {
          req.del_file = false
          this.doDelModel(req)
        })
      })
    },
    doDelModel(param) {
      const loading = startLoading()
      apis.delModel(param).then(res => {
        endLoading(loading)
        if (res === "success") {
          this.$message.success("模型已删除")
          this.getTableData()
        }
      }).catch(e => {
        endLoading(loading)
        this.$message.error(e)
      })
    },
    loadExpandData(row) {
      if (!row.files) {
        this.reloadFiles(row.id)
      }
    },
    reloadFiles(moel_id) {
      apis.getDownloadFiles(moel_id).then(res => {
        let line = this.tableData.find(item => item.id === moel_id)
        line.files = JSON.parse(res)
      }).catch(e => {
        this.$message.error(e)
      })
    },
    handleSelectionChange(val) {
      this.multipleSelection = val
    },
    download(row, index) {
      if (row) {
        const load = startLoading()
        apis.createDownload({
          modelId: this.model.id,
          modelName: this.model.name,
          fileName: row.Name,
          fileSize: row.Size,
        }).then(res => {
          endLoading(load)
          if (res === "success") {
            this.$message.success(row.Name + "开始下载")
          }
        }).catch(e => {
          endLoading(load)
          this.$message.error(e)
        })

      } else {
        // console.log(this.multipleSelection)
        let fileList = []
        this.multipleSelection.forEach(item => {
          fileList.push({
            fileName: item.Name,
            fileSize: item.Size
          })
        })
        if (fileList.length > 0) {
          const load = startLoading();
          apis.createBatchDownload({
            modelId: this.model.id,
            modelName: this.model.name,
            fileList: fileList,
          }).then(res => {
            endLoading(load)
            if (res === "success") {
              this.$message.success("开始下载所选文件")
            }
          }).catch(e => {
            endLoading(load)
            this.$message.error(e)
          })
        }
      }

    },
    selectRepo(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          const loading = startLoading()
          apis.createModel(this.modelForm)
            .then(res => {
              // console.log(res)
              if (res !== "error") {
                this.model = JSON.parse(res)
                apis.searchModelFile(this.modelForm).then(res => {
                  endLoading(loading)
                  // console.log(res)
                  this.modelFiles = res
                  this.showModelFiles = true
                  this.showDownload = true
                  this.showSubmit = false
                }).catch(e => {
                  this.$message.error(e)
                  endLoading(loading)
                })
              } else {
                endLoading(loading)
                this.$message.error('创建模型失败')
              }
            }).catch(e => {
            this.$message.error(e)
            endLoading(loading)
          })
        } else {
          return false
        }
      })
    },
    create() {
      this.dialogTitle = '新增模型'
      this.showDialog = true
    },
    getTableData() {
      const loading = startLoading();
      apis.modelList(this.currentPage, this.pageSize, this.formInline.search).then(res => {
        endLoading(loading)
        const resp = JSON.parse(res)
        // console.log(resp)
        this.tableData = resp.record
        this.total = resp.total
      }).catch(e => {
        endLoading(loading)
        this.$message.error(e);
      })
    },
    handleSizeChange(pageSize) {
      this.pageSize = pageSize
      this.getTableData()
    },
    handleCurrentChange(current) {
      this.currentPage = current
      this.getTableData()
    }
  }
}
</script>

<style>
.demo-table-expand {
  font-size: 0;
}

.demo-table-expand label {
  width: 200px;
  margin-left: 10px;
  color: #99a9bf;
}

.demo-table-expand .el-form-item {
  margin-right: 0;
  margin-bottom: 0;
  width: 50%;
}
</style>
