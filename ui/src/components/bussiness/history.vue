<template>
  <div>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>AI推理</el-breadcrumb-item>
      <el-breadcrumb-item>推理历史</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card>
      <el-form :inline="true" :model="formInline" class="demo-form-inline">
        <el-form-item label="搜索">
          <el-input v-model="formInline.search" placeholder="搜索模型运行历史"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="getTableData">查询</el-button>
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
          width="70"
          prop="model_type"
          label="类型">
          <template slot-scope="scope">
            <el-tag
              :type="scope.row.model_type === 'gguf' ? 'primary' : 'success'"
              disable-transitions>{{ scope.row.model_type }}
            </el-tag>
          </template>
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
          prop="start_time"
          label="执行时间">
        </el-table-column>
         <el-table-column
          prop="stop_time"
          label="停止时间">
        </el-table-column>
        <el-table-column
          fixed="right"
          label="操作"
          width="80">
          <template slot-scope="scope">
            <el-button @click="del(scope.row, scope.$index)" type="danger" size="small">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="block">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="pageSizes"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total">
        </el-pagination>
      </div>
    </el-card>
  </div>
</template>

<script>
import apis from "../../common/apis";
import {endLoading, startLoading} from "../../common/common";

export default {
  name: 'history',
  data() {
    return {
      logIndex: 1,
      logLine: 30,
      showDialog: false,
      log: {
        logFilePath: '',
        logContent: '',
        id: -1
      },
      formInline: {
        search: ''
      },
      tableData: [],
      currentPage: 1,
      pageSize: 10,
      total: 0,
      pageSizes: [10, 20, 50]
    }
  },
  created() {
    this.getTableData()
  },
  methods: {
    del(item) {
      this.$confirm('此操作将永久删除该记录, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        apis.delRunningModel(item.id).then(res => {
          if (res === "success") {
            this.$message.success("已删除")
            this.getTableData()
          }
        }).catch(e => {
          this.$message.error(e)
        })
      })
    },
    getTableData() {
      const loading = startLoading()
      apis.listRunningModeHistory({
        limit: this.pageSize,
        page: this.currentPage,
        search: this.formInline.search
      }).then(res => {
        endLoading(loading)
        const data = JSON.parse(res)
        this.total = data.total
        this.tableData = data.record
      }).catch(e => {
        endLoading(loading)
        this.$message.error(e)
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
.logDialog {
  white-space: pre-line;
  overflow-y: auto;
  height: 60vh
}
</style>
