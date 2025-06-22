<template>
  <div class="chat-container">
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>模型进程</el-breadcrumb-item>
      <el-breadcrumb-item>AI chat</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>AI聊天助手: &nbsp;&nbsp; <strong>{{ model.name }}</strong></span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="$router.back()">返回</el-button>
      </div>
      <div class="chat-messages" ref="scrollableDiv">
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
      <div>
        <span style="color: #606266">深度思考:</span>
        <el-switch v-model="think"></el-switch>
      </div>
      <div class="chat-input">

        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="5"
          placeholder="请输入问题..."
          @keyup.enter.native="sendMessage"
        ></el-input>
        <el-button @click="sendMessage" type="primary" :disabled="isLoading">发送</el-button>
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
      apiUrl: 'http://127.0.0.1:5000/v1/chat/completions',
      modelId: '',
      modelName: '',
      modelType: '',
      reasoningArgs: '',
      model: {},
      memory: 5,
      stream: false,
      torch_dtype: 'auto',
      think: true
    }
  },
  created() {
    this.modelId = this.$route.query.modelId
    this.modelName = this.$route.query.modelName
    this.modelType = this.$route.query.modelType
    this.reasoningArgs = JSON.parse(this.$route.query.reasoningArgs)
    this.memory = this.reasoningArgs.memory
    this.stream = this.reasoningArgs.stream
    this.torch_dtype = this.reasoningArgs.torch_dtype
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
    toEnd() {
      if (this.$refs.scrollableDiv) {
        this.$refs.scrollableDiv.scrollTo({
          top: this.$refs.scrollableDiv.scrollHeight,
          behavior: 'smooth'
        });
      }
    },
    async sendMessage() {
      if (!this.inputMessage.trim()) return;

      if (this.think === true) {
        // this.inputMessage += "/think"
      } else {
        this.inputMessage += "/no_think"
      }
      // 添加用户消息到对话
      const userMessage = {
        role: 'user',
        content: this.inputMessage
      };

      if (this.messages.length >= this.memory) {
        this.messages.shift()
        this.messages.shift()
      }
      this.messages.push(userMessage);

      this.toEnd()

      this.inputMessage = '';

      try {
        this.isLoading = true;

        if (this.stream) {
          await this.callOpenAIAPIStream(this.messages, this.reasoningArgs);
        } else {
          // 调用API获取回复
          const response = await this.callOpenAIAPI(this.messages, this.reasoningArgs);
          this.messages.push(response);

        }
        this.toEnd()
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
    async callOpenAIAPI(messages, reasoningArgs) {
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify(
          Object.assign({
            model: this.model.name,
            messages: messages,
          }, reasoningArgs)
        )
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return {
        role: 'assistant',
        content: data.choices[0].message.content
      };
    },

    async callOpenAIAPIStream(messages, reasoningArgs) {
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify(
          Object.assign({
            model: this.model.name,
            messages: messages,
          }, reasoningArgs)
        )
      });

      // 获取响应的ReadableStream
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');

      let index = 0
      while (true) {
        if (this.isLoading === true) {
          this.isLoading = false;
        }
        const {done, value} = await reader.read();

        if (done) {
          console.log('流读取完成');
          break;
        }

        // 处理每一块数据（Uint8Array）
        const chunk = decoder.decode(value)
        // console.log('接收到数据块:', chunk);
        const dataStr = chunk.replace('data:', '').trim()
        // console.log(chunk.substring(6, chunk.length))
        const data = JSON.parse(dataStr)

        // 可以在这里更新UI或处理数据
        let content = data.choices[0].delta.content
        let role = data.choices[0].delta.role
        if (index === 0) {
          const message = {
            role: role,
            content: ''
          }
          this.messages.push(message)
        } else {
          if (content) {
            const message = this.messages[this.messages.length - 1];
            message.content += content
          }
        }
        this.toEnd()
        index++;
      }
    }
  }
}
</script>

<style scoped>
.chat-container {
  padding: 5px;
  margin: 0 auto;
}

.box-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  height: 45vh;
  overflow-y: auto;
  padding: 15px;
  margin-bottom: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  width: auto;
  white-space: normal; /* 默认值，在空格处换行 */
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

  .assistant {
    max-width: 90%;
  }
}

.message-bubble {
  padding: 10px 15px;
  border-radius: 4px;
  background-color: #e4e7ed;
  display: inline-block;
  max-width: 90%;
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

