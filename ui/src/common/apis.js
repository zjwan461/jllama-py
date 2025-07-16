import {Loading, Message} from 'element-ui'
import {startLoading} from "./common";


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
  delFile(fileId) {
    return window.pywebview.api.delete_file_download(fileId)
  },
  delModel(params) {
    return window.pywebview.api.delete_model(params)
  },
  importFile(params) {
    return window.pywebview.api.import_file(params)
  },
  fileList(params) {
    return window.pywebview.api.file_list(params)
  },
  getModel(modelId) {
    return window.pywebview.api.get_model(modelId)
  },
  runModel(params) {
    return window.pywebview.api.run_model(params)
  },
  listRunningModel(params) {
    return window.pywebview.api.list_running_model(params)
  },
  stopRunningModel(execLogId) {
    return window.pywebview.api.stop_running_model(execLogId)
  },
  listRunningModeHistory(params) {
    return window.pywebview.api.list_running_model_history(params)
  },
  delRunningModel(id) {
    return window.pywebview.api.del_running_model(id)
  },
  showTk() {
    return window.pywebview.api.show_tk()
  },
  splitMergeGguf(params) {
    return window.pywebview.api.split_merge_gguf(params)
  },
  listSplitMerge(params) {
    return window.pywebview.api.list_split_merge(params)
  },
  listQuantize(params) {
    return window.pywebview.api.list_quantize(params)
  },
  listQuantizeParams() {
    return window.pywebview.api.list_quantize_params()
  },
  quantize(params) {
    return window.pywebview.api.quantize(params)
  },
  convertHfToGguf(params) {
    return window.pywebview.api.convert_hf_to_gguf(params)
  },
  listConvertModel(params) {
    return window.pywebview.api.list_covert_model(params)
  },
  getSetting() {
    return window.pywebview.api.get_setting()
  },
  saveSetting(params) {
    return window.pywebview.api.save_setting(params)
  },
  getLlamaCppConfig() {
    return window.pywebview.api.get_llama_cpp_config()
  },
  saveLlamaCppConfig(content) {
    return window.pywebview.api.save_llama_cpp_config(content)
  },
  getLLamaServerInfo() {
    return window.pywebview.api.get_llama_server_info()
  },
  startLLamaServer() {
    return window.pywebview.api.start_llama_server()
  },
  stopLLamaServer() {
    return window.pywebview.api.stop_llama_server()
  },
  openFileInSysEdit(filePath) {
    return window.pywebview.api.open_file_in_sys_edit(filePath)
  },
  async train(params) {
    // window.pywebview.api.train(params)
    return new Promise((resolve, reject) => {
      window.pywebview.api.train(params).then(res => {
        resolve(res)
      }).catch(err => {
        reject(err)
      })
    })
  },
  getTrainList(page, limit) {
    return window.pywebview.api.get_train_list(page, limit)
  },
  deleteTrainRecord(id) {
    return window.pywebview.api.delete_train_record(id)
  },
  generateTrainCode(params) {
    return window.pywebview.api.generate_train_code(params)
  },
  checkSshConnection(hostname, port, username, password) {
    return window.pywebview.api.check_ssh_connection(hostname, port, username, password)
  },
  async remoteTrain(params) {
    // return window.pywebview.api.remote_train(params)
    return new Promise((resolve, reject) => {
      window.pywebview.api.remote_train(params).then(res => {
        resolve(res)
      }).catch(err => {
        reject(err)
      })
    })
  },
  getLlamaFactoryInfo() {
    return window.pywebview.api.get_llamafactory_info()
  },
  installLlamaFactory() {
    return window.pywebview.api.install_llamafactory()
  },
  installLlamafactoryManual() {
    return window.pywebview.api.install_llamafactory_manual()
  },
  reloadInstallState() {
    return window.pywebview.api.reload_install_state()
  },
  isTraining() {
    return window.pywebview.api.is_training()
  },
  stopTrain() {
    return window.pywebview.api.stop_train()
  },
  getAiChatUrl() {
    return window.pywebview.api.get_ai_chat_url()
  },
  startLlamafactory() {
    return window.pywebview.api.start_lf_webui()
  },
  stopLlamafactory() {
    return window.pywebview.api.stop_lf_webui()
  },
  isLlamafactoryRunning() {
    return window.pywebview.api.is_lf_running()
  },
  getRecentServerInfo() {
    return window.pywebview.api.get_recent_server_info()
  },
  getSdInfo() {
    return window.pywebview.api.get_sd_info()
  },
  initSd() {
    return window.pywebview.api.init_sd()
  },
  sdGeneratePic(params) {
    return window.pywebview.api.sd_generate_pic(params)
  },
  saveImages(base64) {
    return window.pywebview.api.save_image(base64)
  },
  sdPicToPic(params) {
    return window.pywebview.api.sd_pic_to_pic(params)
  },
  initIpAdapter() {
    return window.pywebview.api.init_ip_adapter()
  },
  initIpAdapterFaceid() {
    return window.pywebview.api.init_ip_adapter_faceid()
  },
  getIpAdapterModels() {
    return window.pywebview.api.get_ip_adapter_models()
  },
}
