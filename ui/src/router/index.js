import Vue from 'vue'
import VueRouter from 'vue-router'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

Vue.use(VueRouter)

const routes = [{
  path: '/',
  redirect: '/home'
},
  {
    path: '/home',
    name: 'home',
    component: () => import('../components/home.vue'),
    redirect: '/welcome',
    children: [{
      path: '/welcome',
      name: 'welcome',
      component: () => import('../components/welcome.vue')
    }, {
      path: '/setting',
      name: 'setting',
      component: () => import('../components/setting.vue')
    }, {
      path: '/watch',
      name: 'watch',
      component: () => import('../components/bussiness/watch.vue')
    }, {
      path: '/deploy',
      name: 'deploy',
      component: () => import('../components/bussiness/deploy.vue')
    }, {
      path: '/mgn/model-download',
      name: 'model-download',
      component: () => import('../components/bussiness/mgn/model-download.vue')
    }, {
      path: '/mgn/model-import',
      name: 'model-import',
      component: () => import('../components/bussiness/mgn/model-import.vue')
    }, {
      path: '/history',
      name: 'watch',
      component: () => import('../components/bussiness/history.vue')
    }, {
      path: '/tools/split-merge',
      name: 'split-merge',
      component: () => import('../components/bussiness/tools/split-merge.vue')
    }, {
      path: '/tools/quantization',
      name: 'quantization',
      component: () => import('../components/bussiness/tools/quantization.vue')
    }, {
      path: '/tools/convert',
      name: 'convert',
      component: () => import('../components/bussiness/tools/convert.vue')
    }, {
      path: '/tools/train',
      name: 'train',
      component: () => import('../components/bussiness/tools/train.vue')
    },
      {
        path: '/ai/chat',
        name: 'AIChat',
        component: () => import('../components/bussiness/ai-chat.vue')
      }
    ]
  }]

const router = new VueRouter({
  routes
})

NProgress.configure({
  easing: 'ease', // 动画方式
  speed: 100, // 递增进度条的速度
  showSpinner: false, // 是否显示加载ico
  trickleSpeed: 200, // 自动递增间隔
  minimum: 0.3 // 初始化时的最小百分比
})

router.beforeEach((to, from, next) => {
  NProgress.start()
  next()
})

router.afterEach(() => {
  NProgress.done() // 关闭进度条
})

export default router
