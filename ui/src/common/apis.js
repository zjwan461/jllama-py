import {Loading, Message} from 'element-ui'


export default {
  showTips() {
    window.pywebview.api.show_tips().then(res => {
      Message.info(res)
    })
  },
  getNav() {
    return window.pywebview.api.get_nav()
  },
  getSysInfo() {
    return window.pywebview.api.get_sys_info()
  },
  initEnv() {
    return window.pywebview.api.init_env()
  },
}
