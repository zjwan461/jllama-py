<template>
  <div>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>AI推理</el-breadcrumb-item>
      <el-breadcrumb-item>本地部署</el-breadcrumb-item>
    </el-breadcrumb>
  </div>
</template>

<script>

export default {
  name: "deploy",
  data() {
    return {
      deployType: "llama.cpp",
      deployTypeList: ["llama.cpp", "ollama"]
    }
  },
  methods: {}
}
</script>


<style scoped>

</style>
