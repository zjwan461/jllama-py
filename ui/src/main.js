import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import './plugins/element.js'
import './assets/css/global.css'
import './assets/css/ruoyi.css'
import './assets/iconfont/iconfont.css'
import {showNotice} from "./common/common";


Vue.config.productionTip = false

window.addEventListener('pywebviewready', function () {
  window.vue = new Vue({
    router,
    store,
    methods: {
      messageArrive(title, msg, type) {
        showNotice(title, msg, type)
      },
      msgAppend(msg) {
        App.methods.appendMsg(msg)
      },
    },
    render: h => h(App)
  }).$mount('#app')
})
