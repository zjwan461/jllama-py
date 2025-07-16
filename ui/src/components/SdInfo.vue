<template>
  <div class="sd-info">
    <div>SD环境状态：
      <el-tag type="success" v-if="sd_info.state=='已初始化'">{{ sd_info.state }}</el-tag>
      <el-tag type="danger" v-else>{{ sd_info.state }}</el-tag> &nbsp;&nbsp;&nbsp;&nbsp;
      <el-tooltip content="初始化SD基础运行环境">
        <el-button :loading="sd_info_loading" @click="initSd" type="text" size="mini" round v-if="sd_info.state === '待初始化'">初始化
        </el-button>
      </el-tooltip>
    </div>
    <div>
      IP-Adapter环境状态:
      <el-tag type="success" v-if="sd_info.ip_adapter_state=='已初始化'">{{ sd_info.ip_adapter_state }}</el-tag>
      <el-tag type="danger" v-else>{{ sd_info.ip_adapter_state }}</el-tag> &nbsp;&nbsp;&nbsp;&nbsp;
      <el-tooltip content="初始化IP-Adapter运行环境">
        <el-button :loading="ip_adapter_loading" @click="initIpAdapter" round type="primary" size="mini"
                   v-if="sd_info.ip_adapter_state ==='待初始化'">init
        </el-button>
      </el-tooltip>
    </div>
    <div>
      IP-Adapter-FaceID环境状态:
      <el-tag type="success" v-if="sd_info.ip_adapter_faceid_state=='已初始化'">{{
          sd_info.ip_adapter_faceid_state
        }}
      </el-tag>
      <el-tag type="danger" v-else>{{ sd_info.ip_adapter_faceid_state }}</el-tag> &nbsp;&nbsp;&nbsp;&nbsp;
      <el-tooltip content="初始化IP-Adapter-FaceID运行环境">
        <el-button :loading="ip_adapter_faceid_loading" @click="initIpAdapterFaceid" round type="primary" size="mini"
                   v-if="sd_info.ip_adapter_faceid_state ==='待初始化'">init
        </el-button>
      </el-tooltip>
    </div>
    <div>SD基础模型保存目录：<u>{{ sd_info.main_model_path }}</u></div>
    <div>SD版本：<u>{{ sd_info.sd_version }}</u></div>
    <div>常用AIGC社区：&nbsp;&nbsp;
      <el-link type="primary" href="https://www.liblib.art/" target="_blank">liblib art</el-link>&nbsp;&nbsp;&nbsp;&nbsp;
      <el-link type="primary" href="https://www.aigccn.cc/" target="_blank">AIGC社区</el-link>&nbsp;&nbsp;&nbsp;&nbsp;
      <el-link type="primary" href="https://modelscope.cn/aigc/models" target="_blank">ModelScope AIGC</el-link>
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
      ip_adapter_loading: false,
      ip_adapter_faceid_loading: false,
    };
  },
  watch: {},
  created() {
  },
  methods: {
    initSd() {
      this.$message.info("开始下载SD基础模型")
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
    initIpAdapter() {
      this.$message.info("开始下载IP-Adapter模型")
      this.ip_adapter_loading = true
      apis.initIpAdapter().then(res => {
        this.ip_adapter_loading = false
        this.$message.success("IP-Adapter环境初始化完成")
        this.$emit('getSdInfo') // 触发父组件方法
        this.$emit('getIpAdapterModels')
      }).catch(e => {
        this.ip_adapter_loading = false
        this.$message.error(e)
      });
    },
    initIpAdapterFaceid() {
      this.$message.info("开始下载IP-Adapter-FaceID相关模型，文件较多，等待时间较长")
      this.ip_adapter_faceid_loading = true
      apis.initIpAdapterFaceid().then(res => {
        this.ip_adapter_faceid_loading = false
        this.$message.success("IP-Adapter-FaceId环境初始化完成")
        this.$emit('getSdInfo') // 触发父组件方法

      }).catch(e => {
        this.ip_adapter_faceid_loading = false
        this.$message.error(e)
      });
    }
  }
};
</script>

<style scoped>
.sd-info {
  line-height: 35px;
}
</style>
