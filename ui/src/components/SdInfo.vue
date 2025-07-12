<template>
  <div class="sd-info" v-loading="sd_info_loading">
    <div>SD环境状态：
      <el-tag type="success" v-if="sd_info.state=='已初始化'">{{ sd_info.state }}</el-tag>
      <el-tag type="danger" v-else>{{ sd_info.state }}</el-tag>
    </div>
    <div>SD基础模型保存目录：<u>{{ sd_info.main_model_path }}</u></div>
    <div>SD版本：<u>{{ sd_info.sd_version }}</u></div>
    <div>常用AIGC社区：&nbsp;&nbsp;
      <el-link type="primary" href="https://www.liblib.art/" target="_blank">liblib art</el-link>&nbsp;&nbsp;&nbsp;&nbsp;
      <el-link type="primary" href="https://www.aigccn.cc/" target="_blank">AIGC社区</el-link>&nbsp;&nbsp;&nbsp;&nbsp;
      <el-link type="primary" href="https://modelscope.cn/aigc/models" target="_blank">ModelScope AIGC</el-link>
    </div>
    <div>
      <el-button @click="initSd" type="primary" size="small" v-if="sd_info.state === '待初始化'">初始化
      </el-button>
    </div>
  </div>
</template>

<script>
import apis from "@/common/apis";

export default {
  name: 'SdInfo',
  props: {
    sd_info: {
      type: Object,
      required: true, // 是否必填
      default: {}
    }
  },
  data() {
    return {
      sd_info_loading: false,
    };
  },
  watch: {},
  created() {
  },
  methods: {
    initSd() {
      this.sd_info_loading = true
      apis.initSd().then(res => {
        this.sd_info_loading = false
        this.$message.success("SD环境初始化完成")
        this.$emit('getSdInfo') // 触发父组件方法

      }).catch(e => {
        this.sd_info_loading = false
        this.$message.error(e)
      });
    },
  }
};
</script>

<style scoped>
.sd-info {
  line-height: 30px;
}
</style>
