<template>
  <div>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>工具箱</el-breadcrumb-item>
      <el-breadcrumb-item>微调历史</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card>
      <el-table
        :data="tableData"
        border
        style="width: 100%"
      >
        <el-table-column
          prop="type"
          label="微调模式">
        </el-table-column>
        <el-table-column
          prop="result"
          label="微调结果">
          <template slot-scope="scope">
            <el-tag
              :type="scope.row.result === '成功' ? 'success' : 'danger'"
              disable-transitions>{{ scope.row.result }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          width="500px"
          prop="train_args"
          label="微调参数">
        </el-table-column>
        <el-table-column
          prop="err_msg"
          label="失败信息">
        </el-table-column>
        <el-table-column
          prop="create_time"
          label="执行时间">
        </el-table-column>
        <el-table-column
          fixed="right"
          label="操作"
          width="180">
          <template slot-scope="scope">
            <el-button @click="reTrain(scope.row, scope.$index)" type="primary" size="small">重用</el-button>
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
import apis from "../../../common/apis";
import {endLoading, startLoading} from "../../../common/common";

export default {
  name: 'train-history',
  data() {
    return {
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
    resetDialog() {
      this.showDialog = false
      this.log = {
        logFilePath: '',
        logContent: '',
        id: -1
      }
      this.logIndex = 1
    },
    reTrain(item) {
      this.$router.push({path: '/tools/train', query: item})
    },
    del(item) {
      this.$confirm('此操作将永久删除该记录, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        apis.deleteTrainRecord(item.id).then(res => {
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
      apis.getTrainList(this.currentPage, this.pageSize).then(res => {
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
