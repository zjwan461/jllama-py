<template>
  <div>
    <!-- Form -->
    <el-dialog :title="title" :visible.sync="visible">
      <el-form :model="form">
        <el-form-item label="" :label-width="formLabelWidth">
          <textarea v-model="form.log" autocomplete="off"></textarea>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'MessageBoard',
  props: {
    title: {
      type: String,
      default: '消息面板'
    },
    visible: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      form: {
        log: ''
      },
      formLabelWidth: '120px'
    }
  },
  methods: {
    appendInfo(line) {
      this.form.log += "\n" + line
    },
  }
}
</script>


<style scoped>

</style>
