<template>
  <div id="app">
    <router-view/>
    <MessageBoard ref="messageBoard" title="消息面板" :visible="messageBoardVisible"></MessageBoard>
  </div>
</template>

<script>
import MessageBoard from './components/MessageBoard.vue'

export default {
  name: 'App',
  data() {
    return {
      messageBoardVisible: false
    }
  },
  components: {
    MessageBoard
  },
  created() {
    window.pywebview.api.msg_append('1111')
  },
  methods: {
    showMessageBoard() {
      this.messageBoardVisible = true
    },
    hideMessageBoard() {
      this.messageBoardVisible = false
    },
    appendMsg(msg) {
      this.showMessageBoard()
      console.log("1")
      const messageBoard = this.$refs.messageBoard
      console.log("2")
      messageBoard.appendInfo(msg)
    },
  }
}
</script>

<style>
</style>
