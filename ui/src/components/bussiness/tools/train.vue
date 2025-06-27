<template>
  <div>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>工具箱</el-breadcrumb-item>
      <el-breadcrumb-item>模型微调</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card>
      <el-alert :title="tips" type="warning">
      </el-alert>
      <el-tabs v-model="activeName" @tab-click="handleClick">
        <el-tab-pane label="简单模式" name="simple">
          <el-row>
            <el-col :span="12">
              <el-form ref="trainArgs" :rules="rules" :model="trainArgs" label-width="135px">
                <el-form-item label="模型路径" prop="modelPath">
                  <el-input v-model="trainArgs.modelPath" type="text" placeholder="模型路径"></el-input>
                </el-form-item>
                <el-form-item label="torch_dtype" prop="torchDtype">
                  <el-select v-model="trainArgs.torchDtype">
                    <el-option value="auto">auto</el-option>
                    <el-option value="bfloat16">bfloat16</el-option>
                    <el-option value="float16">float16</el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="训练输出目录" prop="trainOutputDir">
                  <el-input v-model="trainArgs.trainOutputDir" type="text" placeholder="训练输出目录"></el-input>
                </el-form-item>
                <el-form-item label="lora保存目录" prop="loraSaveDir">
                  <el-input v-model="trainArgs.loraSaveDir" type="text" placeholder="lora保存目录"></el-input>
                </el-form-item>
                <el-form-item label="微调模型保存目录" prop="finTuningMergeDir">
                  <el-input v-model="trainArgs.finTuningMergeDir" type="text"
                            placeholder="微调模型保存目录"></el-input>
                </el-form-item>
                <el-form-item label="数据集文件" prop="datasetPath">
                  <el-input type="text" disabled v-model="trainArgs.datasetPath" placeholder="数据集所在的文件目录">
                  </el-input>
                  <el-button size="small" type="primary" @click="openFileSelect('datasetPath')">选择文件</el-button>
                </el-form-item>
                <el-form-item label="测试集占比" prop="datasetTestSize">
                  <el-input type="text" v-model="trainArgs.datasetTestSize" placeholder="测试集占比"></el-input>
                </el-form-item>
                <el-form-item label="截断长度" prop="datasetMaxLength">
                  <el-input v-model="trainArgs.datasetMaxLength" type="text" placeholder="数据集最大长度"></el-input>
                </el-form-item>
                <el-form-item label="训练轮数" prop="numTrainEpochs">
                  <el-input-number v-model="trainArgs.numTrainEpochs" placeholder="训练轮数"></el-input-number>
                </el-form-item>
                <el-form-item label="训练批量大小" prop="perDeviceTrainBatchSize">
                  <el-input-number v-model="trainArgs.perDeviceTrainBatchSize"
                                   placeholder="训练批量大小"></el-input-number>
                </el-form-item>
                <el-form-item label="learning_rate" prop="learningRate">
                  <el-input v-model="trainArgs.learningRate" placeholder="学习率"></el-input>
                </el-form-item>
                <el-form-item label="lora_target" prop="loraTarget">
                  <el-input v-model="trainArgs.loraTarget" placeholder="lora target"></el-input>
                </el-form-item>
                <el-form-item label="lora_dropout" prop="loraDropout">
                  <el-input v-model="trainArgs.loraDropout" placeholder="lora dropout"></el-input>
                </el-form-item>
                <el-form-item label="bnb量化" prop="bnbConfig">
                  <el-select v-model="trainArgs.bnbConfig">
                    <el-option value="bnb_4bit">bnb_4bit</el-option>
                    <el-option value="bnb_8bit">bnb_8bit</el-option>
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="onSubmit('trainArgs')">提交</el-button>
                </el-form-item>
              </el-form>
            </el-col>
            <el-col :span="12">
              <div class="logBox">
                参数说明：
                <vue-markdown :source="markdownItContent" class="markdown-body"></vue-markdown>
              </div>
            </el-col>
          </el-row>
        </el-tab-pane>
        <el-tab-pane label="原生模式" name="origin">
          <h2>to-do 还没做😊</h2>
<!--          <el-button type="text" @click="openOrigin()">打开LlamaFactory原生网页</el-button>-->
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import VueMarkdown from 'vue-markdown';

import apis from "../../../common/apis";
import {endLoading, getDateString, startLoading, getRequestBodyJson} from "../../../common/common";

export default {
  name: "train",
  components: {
    VueMarkdown
  },
  data() {
    return {
      trainArgs: {
        modelPath: '',
        torchDtype: 'auto',
        trainOutputDir: '',
        loraSaveDir: '',
        finTuningMergeDir: '',
        datasetPath: '',
        datasetTestSize: 0.0,
        datasetMaxLength: 2048,
        numTrainEpochs: 3,
        perDeviceTrainBatchSize: 2,
        learningRate: 5e-5,
        loraTarget: 'all',
        loraDropout: 0.05
      },
      llamaFactoryUrl: '',
      markdownItContent: "**模型路径**: 加载模型的绝度路径地址\n\n **torch_dtype**: 加载模型的数据格式，使用bf16混合精度理论上会减少现存占用\n\n" +
        "**训练输出目录**: 本次训练结果输出保存的目录\n\n **lora保存目录**: 保存lora的目录\n\n **微调模型保存目录**: 原始模型合并lora之后的保存目录\n\n" +
        "**数据集文件**: 用于训练的数据集文件，只支持<a href='https://llamafactory.readthedocs.io/zh-cn/latest/getting_started/data_preparation.html#alpaca' target='_blank'>alpaca</a>格式\n\n" +
        "**测试集占比**: 用于测试的数据在数据集中的占比，0~1之间的小数。填0则代表数据集全用于训练。\n\n **截断长度**: 单条数据的最大长度，超过这个长度将会被截断处理\n\n" +
        "**训练轮次**: 训练的epochs,一般来说越大训练拟合度越高,训练的损失值越低。但过高的轮次也可能导致微调以后的模型过拟合\n\n" +
        "**训练批量大小**: 训练中每一个step训练的batch size。理论上越高的batch size训练速度越快，但也会加倍增加显存和算力的占用\n\n" +
        "**学习率**: AdamW 优化器的初始学习率。学习率即每一个训练的step调整的梯度 \n\n **lora_dropout**: lora微调过程中每次过滤掉一部分比例的参数量不参与训练。用于减少模型对某些参数的过渡依赖\n\n" +
        "**lora_target**: lora微调目标模型线性层集合。比如[\"q_proj\",\"v_proj\"]。all则表示将模型的所有线性层进行微调 \n\n **bnb量化**: bitAndByte量化策略，不选则不进行量化。可选4bit量化和8bit量化，可降低显存占用",
      tips: '可进行简单的lora微调，复杂的微调任务请使用llamafactory原生模式',
      activeName: 'simple',
      rules: {
        modelPath: [
          {required: true, message: '请输入模型路径', trigger: 'blur'}
        ]
        , torchDtype: [
          {required: true, message: '请输入模型路径torch_dtype', trigger: 'blur'}
        ],
        trainOutputDir: [
          {required: true, message: '请输入训练输出目录', trigger: 'blur'}
        ],
        loraSaveDir: [
          {required: true, message: '请输入lora保存目录', trigger: 'blur'}
        ],
        finTuningMergeDir: [
          {required: true, message: '微调保存目录', trigger: 'blur'}
        ],
        datasetPath: [
          {required: true, message: '请选择数据集文件', trigger: 'blur'}
        ],
        datasetTestSize: [
          {required: true, message: '请输入测试集占比', trigger: 'blur'},
          {pattern: /^(0(\.\d+)?|1(\.0+)?)$/, message: '请输入0.1-1.0之间的小数', trigger: 'blur'}
        ],
        datasetMaxLength: [
          {required: true, message: '请输入截断长度', trigger: 'blur'}
        ],
        numTrainEpochs: [
          {required: true, message: '训练轮次必填', trigger: 'blur'}
        ],
        perDeviceTrainBatchSize: [
          {required: true, message: '批次大小必填', trigger: 'blur'}
        ],
        learningRate: [
          {required: true, message: '学习率必填', trigger: 'blur'},
        ],
        loraDropout: [
          {required: true, message: 'lora_dropout必填', trigger: 'blur'},
          {pattern: /^(0(\.\d+)?|1(\.0+)?)$/, message: '请输入0.1-1.0之间的小数', trigger: 'blur'}
        ],
        loraTarget: [
          {required: true, message: 'lora_target必填', trigger: 'blur'},
        ]
      },
    }
  },
  created() {
    this.initDir()
    this.getLlamaFactoryUrl()
  },
  methods: {
    initDir() {
      let dateStr = getDateString()
      this.trainArgs.loraSaveDir = "./lora_" + dateStr
      this.trainArgs.trainOutputDir = "./train_" + dateStr
      this.trainArgs.finTuningMergeDir = "./final_" + dateStr
    },
    openFileSelect(val) {
      apis.openFileSelector().then(res => {
        if (res.length > 0) {
          this.trainArgs[val] = res[0]
        }
      }).catch(e => {
        this.$message.error(e)
      })
      return false
    },
    handleClick(tab, event) {
    },
    onSubmit(form) {
      this.$refs[form].validate((valid) => {
        if (valid) {
          const loading = startLoading("训练中...")
          apis.train(this.trainArgs).then(res => {
            console.log(res)
            endLoading(loading)
          }).catch(e => {
            endLoading(loading)
            this.$message.error(e)
          })
        }
      })
    },
    openOrigin() {
      if (this.llamaFactoryUrl.length > 0) {
        window.open(this.llamaFactoryUrl, '_blank')
      }
    },
    getLlamaFactoryUrl() {

    }
  }
}
</script>

<style>
.form {
  width: 600px;
}

.logBox {
  margin: auto 20px;
}
</style>
