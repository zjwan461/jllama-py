<template>
  <div class="chat-container">
    <!-- 头部区域 -->
    <el-header class="header">
      <div class="header-title">AI对话助手</div>
      <el-button icon="el-icon-setting" @click="showSettings = true"></el-button>
    </el-header>

    <!-- 主要内容区域 -->
    <el-main class="main-content">
      <!-- 聊天消息区域 -->
      <div class="chat-messages" ref="messagesContainer">
        <div v-for="(message, index) in messages" :key="index" class="message-item">
          <!-- 机器人消息 -->
          <div v-if="message.type === 'bot'" class="message-bot">
            <div class="avatar">AI</div>
            <div class="message-content">
              <div class="message-text" v-html="message.content"></div>
            </div>
          </div>
          
          <!-- 用户消息 -->
          <div v-else class="message-user">
            <div class="message-content">
              <div class="message-text">{{ message.content }}</div>
            </div>
            <div class="avatar">你</div>
          </div>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="isLoading" class="message-bot message-loading">
          <div class="avatar">AI</div>
          <div class="message-content">
            <div class="message-text">
              <el-loading v-bind="loadingOptions"></el-loading>
            </div>
          </div>
        </div>
      </div>
    </el-main>

    <!-- 底部输入区域 -->
    <el-footer class="footer">
      <el-form :model="form" ref="formRef" label-width="0px">
        <el-form-item prop="content">
          <el-input 
            v-model="form.content" 
            type="textarea" 
            :rows="2" 
            placeholder="请输入问题..."
            @keyup.enter.native="sendMessage"
          ></el-input>
        </el-form-item>
        <el-button 
          type="primary" 
          @click="sendMessage"
          :loading="isLoading"
          :disabled="isLoading || !form.content.trim()"
        >发送</el-button>
      </el-form>
    </el-footer>

    <!-- 设置对话框 -->
    <el-dialog :visible.sync="showSettings" title="设置">
      <el-form :model="settings" label-width="120px">
        <el-form-item label="API端点">
          <el-input v-model="settings.apiEndpoint" placeholder="请输入API端点"></el-input>
        </el-form-item>
        <el-form-item label="API密钥">
          <el-input v-model="settings.apiKey" type="password" placeholder="请输入API密钥"></el-input>
        </el-form-item>
        <el-form-item label="AI模型">
          <el-radio-group v-model="settings.model">
            <el-radio label="gpt-3.5-turbo">GPT-3.5 Turbo</el-radio>
            <el-radio label="gpt-4">GPT-4</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="回复风格">
          <el-select v-model="settings.style" placeholder="请选择回复风格">
            <el-option label="简洁明了" value="concise"></el-option>
            <el-option label="详细解释" value="detailed"></el-option>
            <el-option label="专业严谨" value="professional"></el-option>
            <el-option label="友好自然" value="friendly"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="温度值">
          <el-slider v-model="settings.temperature" :min="0" :max="1" :step="0.1"></el-slider>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showSettings = false">取消</el-button>
        <el-button type="primary" @click="saveSettings">保存设置</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'AIChatPage',
  data() {
    return {
      // 消息列表
      messages: [
        {
          type: 'bot',
          content: '你好！我是AI对话助手，有什么可以帮助你的吗？'
        }
      ],
      // 表单数据
      form: {
        content: ''
      },
      // 加载状态
      isLoading: false,
      // 设置相关
      showSettings: false,
      settings: {
        apiEndpoint: 'https://api.openai.com/v1/chat/completions',
        apiKey: '',
        model: 'gpt-3.5-turbo',
        style: 'friendly',
        temperature: 0.7
      },
      // 加载选项
      loadingOptions: {
        text: 'AI正在思考...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0)'
      },
      // 错误信息
      error: null
    }
  },
  methods: {
    // 发送消息
    async sendMessage() {
      const content = this.form.content.trim();
      if (!content) return;
      
      // 添加用户消息
      this.messages.push({
        type: 'user',
        content: content
      });
      
      // 清空输入框
      this.form.content = '';
      
      // 滚动到底部
      this.$nextTick(() => {
        this.scrollToBottom();
      });
      
      try {
        // 显示加载状态
        this.isLoading = true;
        this.error = null;
        
        // 调用API获取回复
        const response = await this.callAIAPI(content);
        
        // 添加AI回复
        this.messages.push({
          type: 'bot',
          content: response
        });
      } catch (error) {
        console.error('API调用失败:', error);
        this.error = 'API调用失败，请检查设置和网络连接';
        
        // 添加错误提示消息
        this.messages.push({
          type: 'bot',
          content: `<div class="error-message">${this.error}</div>`
        });
      } finally {
        // 隐藏加载状态
        this.isLoading = false;
        
        // 滚动到底部
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }
    },
    
    // 调用AI API
    async callAIAPI(prompt) {
      // 从设置中获取API配置
      const { apiEndpoint, apiKey, model, temperature } = this.settings;
      
      // 构建消息历史
      const messages = this.messages
        .filter(msg => msg.type !== 'bot' || !msg.content.includes('API调用失败'))
        .map(msg => ({
          role: msg.type === 'user' ? 'user' : 'assistant',
          content: msg.content
        }));
      
      // 添加系统消息以影响回复风格
      messages.unshift({
        role: 'system',
        content: this.getSystemMessage()
      });
      
      // 构建请求体
      const requestBody = {
        model,
        messages,
        temperature,
        max_tokens: 1000
      };
      
      // 发送请求
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify(requestBody)
      });
      
      // 处理响应
      if (!response.ok) {
        throw new Error(`API返回错误: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // 检查API返回是否包含错误
      if (data.error) {
        throw new Error(data.error.message || 'API返回错误');
      }
      
      // 返回回复内容
      return data.choices[0].message.content;
    },
    
    // 获取系统消息以影响回复风格
    getSystemMessage() {
      const styleDescriptions = {
        concise: '你的回答应该简洁明了，避免不必要的细节。',
        detailed: '你的回答应该详细全面，提供充分的解释和背景信息。',
        professional: '你的回答应该专业严谨，使用适当的技术术语和逻辑结构。',
        friendly: '你的回答应该友好自然，使用通俗易懂的语言和适当的礼貌用语。'
      };
      
      return `你是一个AI对话助手。${styleDescriptions[this.settings.style] || ''}请尽可能提供有帮助的回答。`;
    },
    
    // 滚动到底部
    scrollToBottom() {
      const container = this.$refs.messagesContainer;
      container.scrollTop = container.scrollHeight;
    },
    
    // 保存设置
    saveSettings() {
      // 在实际应用中，应该保存设置到本地存储
      localStorage.setItem('aiChatSettings', JSON.stringify(this.settings));
      
      this.$message({
        message: '设置已保存',
        type: 'success'
      });
      this.showSettings = false;
    }
  },
  mounted() {
    // 从本地存储加载设置
    const savedSettings = localStorage.getItem('aiChatSettings');
    if (savedSettings) {
      this.settings = JSON.parse(savedSettings);
    }
    
    // 页面加载后滚动到底部
    this.$nextTick(() => {
      this.scrollToBottom();
    });
  }
}
</script>

<style scoped>
.chat-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #409EFF;
  color: white;
  height: 60px !important;
  padding: 0 20px;
}

.header-title {
  font-size: 20px;
  font-weight: bold;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  background-color: #f5f7fa;
  padding: 20px;
}

.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message-item {
  display: flex;
  align-items: flex-start;
}

.message-bot {
  justify-content: flex-start;
}

.message-user {
  justify-content: flex-end;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #409EFF;
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  margin: 0 10px;
}

.message-user .avatar {
  background-color: #67c23a;
}

.message-content {
  max-width: 70%;
  padding: 10px 15px;
  border-radius: 8px;
  position: relative;
}

.message-bot .message-content {
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.message-user .message-content {
  background-color: #67c23a;
  color: white;
}

.message-text {
  word-wrap: break-word;
}

.message-loading .message-text {
  min-height: 20px;
}

.footer {
  padding: 20px;
  border-top: 1px solid #ebeef5;
  background-color: white;
}

.el-input__inner {
  border-radius: 4px 4px 0 0 !important;
}

.el-button {
  margin-top: 10px;
  float: right;
}

.error-message {
  color: #f56c6c;
  font-weight: bold;
}
</style>    