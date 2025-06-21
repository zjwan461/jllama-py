<template>
  <div>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>AI推理</el-breadcrumb-item>
      <el-breadcrumb-item>本地部署</el-breadcrumb-item>
    </el-breadcrumb>
    <el-card>
      <el-collapse v-model="activeNames" @change="handleChange" accordion>
        <el-collapse-item title="部署配置" name="1">
          <a href="https://llama-cpp-python.readthedocs.io/en/latest/server" target="_blank">配置参考</a>
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
          <div>服务端口:
            <el-tag>{{ llamaServer.server_port }}</el-tag>
            服务状态:
            <el-tag :type="llamaServer.server_status === 'running'?'success':'danger'">{{ llamaServer.server_status }}
            </el-tag>
          </div>
          <div style="margin: 10px 0">
            <el-button type="primary" size="mini" @click="startOrStopServer"
                       v-text="llamaServer.server_status  === 'running'?'停止服务':'启动服务'"></el-button>

            <el-button type="info" size="mini" @click="getLLamaServerInfo"
                       icon="el-icon-refresh">刷新
            </el-button>
          </div>
        </el-collapse-item>
      </el-collapse>

    </el-card>
  </div>
</template>

<script>
import CodeHighlight from '../CodeHighlight.vue';
import apis from '../../common/apis';
import {endLoading, startLoading} from "@/common/common";

export default {
  name: 'deploy',
  components: {
    CodeHighlight
  },
  data() {
    return {
      activeNames: ['1'],
      deployType: 'llama.cpp',
      deployTypeList: ['llama.cpp'],
      isFullscreen: false,
      loading: true,
      llamaServer: {},
      config: {
        code: '',
        language: 'json'
      }
    }
  },
  mounted() {
    this.getLlamaCppConfig()
    this.getLLamaServerInfo()
  },
  methods: {
    startOrStopServer() {
      if (this.llamaServer.server_status !== 'running') {
        const loading = startLoading("启动中...")
        apis.startLLamaServer().then(res => {
          endLoading(loading)
          this.getLLamaServerInfo()
        }).catch(e => {
          this.$message.error(e)
        })
      } else {
        const loading = startLoading("停止中...")
        apis.stopLLamaServer().then(res => {
          endLoading(loading)
          this.getLLamaServerInfo()
        }).catch(e => {
          this.$message.error(e)
        })
      }
    },
    getLLamaServerInfo() {
      apis.getLLamaServerInfo().then(res => {
        this.llamaServer = res
      }).catch(e => {
        this.$message.error(e)
      })
    },
    handleChange(val) {
      console.log(val)
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
