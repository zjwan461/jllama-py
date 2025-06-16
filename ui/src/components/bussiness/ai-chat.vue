<template>
  <div class="chat-container">
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>模型进程</el-breadcrumb-item>
      <el-breadcrumb-item>AI chat</el-breadcrumb-item>
    </el-breadcrumb>
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>AI聊天助手</span>
        <el-button style="float: right; padding: 3px 0" type="text">设置</el-button>
      </div>
      <div class="chat-messages">
        <div v-for="(message, index) in messages" :key="index" class="message-item">
          <div class="message-avatar" v-if="message.role === 'user'">
            <i class="el-icon-user"></i>
          </div>
          <div class="message-avatar" v-else>
            <span class="icon iconfont">&#xeb62;</span>
          </div>
          <div class="message-content" :class="message.role">
            <div class="message-bubble">
              <pre>{{ message.content }}</pre>
            </div>
          </div>

        </div>
        <div v-if="isLoading" class="message-item">
          <div class="message-avatar">
            <span class="icon iconfont">&#xeb62;</span>
          </div>
          <div class="message-content assistant">
            <div class="message-bubble" v-loading="isLoading" element-loading-text="思考中...">
              <!-- 加载时显示默认加载动画和文本 -->
            </div>
          </div>
        </div>
      </div>
      <div class="chat-input">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="2"
          placeholder="请输入问题..."
          @keyup.enter.native="sendMessage"
        ></el-input>
        <el-button @click="sendMessage" :disabled="isLoading">发送</el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
import apis from "@/common/apis";
import {endLoading, startLoading} from "@/common/common";

export default {
  name: 'ChatWindow',
  data() {
    return {
      messages: [],
      inputMessage: '',
      isLoading: false,
      apiKey: '',
      apiUrl: 'https://api.openai.com/v1/chat/completions',
      modelId: '',
      model: {}
    }
  },
  created() {
    this.modelId = this.$route.query.modelId
    if (this.modelId) {
      const loading = startLoading("加载模型...");
      apis.getModel(this.modelId).then(res => {
        endLoading(loading)
        this.model = JSON.parse(res)
      }).catch(e => {
        endLoading(loading)
        this.$message.error(e)
      })
    }
  },
  methods: {
    async sendMessage() {
      if (!this.inputMessage.trim()) return;

      // 添加用户消息到对话
      const userMessage = {
        role: 'user',
        content: this.inputMessage
      };
      this.messages.push(userMessage);
      this.inputMessage = '';

      try {
        this.isLoading = true;
        // 调用API获取回复
        const response = await this.callOpenAIAPI(userMessage);
        this.messages.push(response);
      } catch (error) {
        console.error('Error:', error);
        this.messages.push({
          role: 'assistant',
          content: '抱歉，请求出错: ' + error.message
        });
      } finally {
        this.isLoading = false;
      }
    },
    async callOpenAIAPI(userMessage) {
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: 'gpt-3.5-turbo',
          messages: [
            {role: 'system', content: '你是一个AI助手，回答用户的问题。'},
            userMessage
          ],
          temperature: 0.7
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return {
        role: 'assistant',
        content: data.choices[0].message.content
      };
    }
  }
}
</script>

<style scoped>
.chat-container {
  height: 70vh;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.box-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  min-height: 300px; /* 新增：设置聊天区域的最小高度 */
  overflow-y: auto;
  padding: 15px;
  margin-bottom: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}


.message-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 15px;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #909399;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
}

.message-content {
  flex: 1;
}

.message-bubble {
  padding: 10px 15px;
  border-radius: 4px;
  background-color: #e4e7ed;
  display: inline-block;
  max-width: 100%;
  white-space: pre-wrap;
  word-break: break-all;
}

.message-content.user .message-bubble {
  background-color: #409eff;
  color: #fff;
}

.chat-input {
  display: flex;
  gap: 10px;
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
}

.chat-input .el-input {
  flex: 1;
}

.chat-input .el-button {
  height: 40px;
  white-space: nowrap;
}

.el-loading-text {
  /* 禁止文本换行 */
  white-space: nowrap;
  /* 自动扩展容器宽度以适应文本 */
  display: inline-block;
  /* 可选：添加最小宽度或 padding 避免过于紧凑 */
  min-width: 120px;
  padding: 0 10px;
}
</style>

