import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import './plugins/element.js'
import {Loading} from 'element-ui'
import './assets/css/global.css'
import './assets/css/ruoyi.css'

let loading

function startLoading() {
  loading = Loading.service({
    lock: true,
    text: '拼命加载中...',
    background: 'rgba(255,255,255,0.5)',
    target: document.querySelector('body')
  })
}

function endLoading() { //  关闭加载动画
  if (loading) {
    loading.close()
  }
}

Vue.config.productionTip = false

window.addEventListener('pywebviewready', function () {
  new Vue({
    router,
    store,
    render: h => h(App)
  }).$mount('#app')
})
