<template>
  <div>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>AI推理</el-breadcrumb-item>
      <el-breadcrumb-item>本地部署</el-breadcrumb-item>
    </el-breadcrumb>
    <el-card>
      <el-collapse v-model="activeNames" @change="handleChange">
        <el-collapse-item title="部署配置" name="1">
          <div v-if="loading">加载中...</div>
          <CodeHighlight v-else
                         @save="onSave"
                         @change="onChange"
                         ref="codeHighlight"
                         :code="config.code"
                         :language="config.language"
                         :showHeader="true"
                         :showThemeSelector="true"
                         :maxHeight="isFullscreen ? 'none' : '500px'"
          />
        </el-collapse-item>
        <el-collapse-item title="执行部署" name="2">
          <div>服务端口</div>
          <div>服务状态</div>
        </el-collapse-item>
      </el-collapse>

    </el-card>
  </div>
</template>

<script>
import CodeHighlight from '../CodeHighlight.vue';
import apis from "../../common/apis";

export default {
  name: "deploy",
  components: {
    CodeHighlight
  },
  data() {
    return {
      activeNames: ['1'],
      deployType: "llama.cpp",
      deployTypeList: ["llama.cpp"],
      isFullscreen: false,
      loading: true,
      config: {
        code: "",
        language: 'json'
      }
    }
  },
  mounted() {
    this.getLlamaCppConfig()
  },
  methods: {
    handleChange(val) {
      console.log(val);
    },
    onSave(code) {
      apis.saveLlamaCppConfig(code).then(res => {
        if (res === 'success') {
          this.$message.success('修改成功')
        }
      }).catch(e => {
        this.$message.error(e)
      })
    },
    onChange(code) {
      // console.log(code)
    },
    getLlamaCppConfig() {
      apis.getLlamaCppConfig().then(res => {
        this.config.code = res
        this.config.language = "json"
        this.loading = false
      }).catch(e => {
        this.$message.error(e)
      })
    },
    getOriginCode() {
      const codeHighlight = this.$refs.codeHighlight
      return codeHighlight.editedCode
    },
    getHtmlCode() {
      const codeHighlight = this.$refs.codeHighlight
      return codeHighlight.formattedCode
    },
  }
}
</script>


<style scoped>

</style>
