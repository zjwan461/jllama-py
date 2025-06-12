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
  modelList(page, limit, search) {
    return window.pywebview.api.model_list({page: page, limit: limit, search: search})
  },
  createModel(modelInfo) {
    return window.pywebview.api.create_model(modelInfo)
  },
  searchModelFile(modelInfo) {
    return window.pywebview.api.search_model_file(modelInfo)
  },
  openFileSelector() {
    return window.pywebview.api.open_file_select()
  },
  createDownload(params) {
    return window.pywebview.api.create_download(params)
  },
  createBatchDownload(params) {
    return window.pywebview.api.create_batch_download(params)
  },
  getDownloadFiles(id) {
    return window.pywebview.api.get_download_files(id)
  },
  delFile(file_id) {
    return window.pywebview.api.delete_file_download(file_id)
  },
  delModel(params) {
    return window.pywebview.api.delete_model(params)
  },
  importFile(params) {
    return window.pywebview.api.import_file(params)
  },
}
