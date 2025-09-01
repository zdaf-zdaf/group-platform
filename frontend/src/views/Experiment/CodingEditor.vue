<template>
  <div class="coding-editor">
    <!-- 问题描述面板 -->
    <div class="problem-panel">
      <el-button @click="goBack" type="default" plain style="margin-bottom: 15px;">
        返回实验详情
      </el-button>
      <h2>{{ problem.title }}</h2>
      <div class="problem-description" v-html="problem.description" />

      <!-- 上传代码按钮 -->
      <el-upload
        :show-file-list="false"
        accept=".py"
        :before-upload="handleFileUpload"
      >
        <el-button type="primary" plain style="margin-top: 10px;">
          <el-icon><Upload /></el-icon>
          导入 .py 文件
        </el-button>
      </el-upload>

      <!-- 提交按钮 -->
      <el-button type="success" @click="submitCode" :loading="submitting" style="margin-top: 20px">
        <el-icon><Upload /></el-icon>
        {{ submitting ? '正在提交...' : '提交代码' }}
      </el-button>
      <!-- 自动保存时间 -->
      <p style="margin-top: 10px; color: #909399; font-size: 13px;">
        上次自动保存时间：{{ lastSavedTime || '暂无记录' }}
      </p>
      <!-- 评测结果 -->
      <div v-if="result" class="result-panel">
        <el-alert :type="result.passed === result.total ? 'success' : 'error'">
          <template #title>
            测试结果：{{ result.passed }} / {{ result.total }} 通过
            <span v-if="executionTime">(耗时: {{ executionTime.toFixed(2) }}ms)</span>
          </template>
        </el-alert>

        <el-collapse v-if="result.details.length > 0">
          <el-collapse-item title="测试用例详情">
            <div v-for="(detail, index) in result.details" :key="index" class="case-item">
              <el-tag :type="detail.is_passed ? 'success' : 'danger'">
                用例 {{ index + 1 }}
              </el-tag>
              <div class="io-grid">
                <div class="io-cell">
                  <label>输入：</label>
                  <pre>{{ detail.input }}</pre>
                </div>
                <div class="io-cell">
                  <label>预期输出：</label>
                  <pre>{{ detail.expected }}</pre>
                </div>
                <div class="io-cell">
                  <label>实际输出：</label>
                  <pre :class="{ error: !detail.is_passed }">{{ detail.actual }}</pre>
                </div>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>

    <!-- 代码编辑器 -->
    <div class="editor-panel">
      <VueMonacoEditor
        :value="code"
        @update:value="handleCodeUpdate"
        language="python"
        theme="vs-dark"
        :options="editorOptions"
        style="height: 100%"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { VueMonacoEditor } from '@guolao/vue-monaco-editor'
import { Upload } from '@element-plus/icons-vue'
import { ElIcon, ElMessage } from 'element-plus'
import axios from 'axios'
import { useRoute } from 'vue-router'
import { useRouter } from 'vue-router'

// 定义评测结果类型
interface JudgeResult {
  passed: number
  total: number
  details: Array<{
    input: string
    expected: string
    actual: string
    is_passed: boolean
  }>
}

// 定义编程题类型
interface CodingProblem {
  id: number
  title: string
  description: string
  test_cases: Array<{
    input: string
    output: string
  }>
  timeout: number
  mem_limit: number
}

// 定义错误响应类型
interface ErrorResponse {
  status: number
  data: {
    error?: string
    detail?: string
    message?: string
  }
}

// 定义Axios错误类型
interface AxiosError {
  response?: ErrorResponse
  message: string
}

const route = useRoute()
const router = useRouter()
const experimentId = computed(() => route.params.id)
const problemId = computed(() => route.params.questionId)
const code = ref<string>('# 在这里编写你的代码\n')
const submitting = ref<boolean>(false)
const executionTime = ref<number>(0)
const result = ref<JudgeResult | null>(null)
const problem = ref<CodingProblem>({
  id: 0,
  title: '',
  description: '',
  test_cases: [],
  timeout: 10,
  mem_limit: 512,
})

const goBack = () => {
  saveAutosave() // 确保在返回前保存当前进度
  router.push(`/experiment/${experimentId.value}`)
}

const editorOptions = ref({
  automaticLayout: true,
  minimap: { enabled: true },
  fontSize: 14,
  tabSize: 4,
})
console.log(route.params)

console.log('experimentId:', experimentId.value, 'problemId:', problemId.value)

// 从API获取编程题详情
const fetchProblem = async () => {
  try {
    const response = await axios.get(
      `http://127.0.0.1:8000/api/experiments/experiments/${experimentId.value}/coding/${problemId.value}/`,
    )
    problem.value = response.data
  } catch (error) {
    ElMessage.error('获取题目信息失败')
    console.error('获取题目信息错误:', error)
  }
}

// 自动保存功能
const storageKey = computed(() => `autosave-code-problem-${problemId.value}`)
const lastSavedTime = ref<string>('')

const loadAutosave = () => {
  const savedCode = localStorage.getItem(storageKey.value)
  if (savedCode) {
    code.value = savedCode
    updateSavedTime()
  }
}

const updateSavedTime = () => {
  const now = new Date()
  lastSavedTime.value = `${now.getHours().toString().padStart(2, '0')}:${now
    .getMinutes()
    .toString()
    .padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
}

const saveAutosave = () => {
  localStorage.setItem(storageKey.value, code.value)
  updateSavedTime()
}

// 防抖处理
let saveTimeout: number | null = null
const debounceSave = () => {
  if (saveTimeout) clearTimeout(saveTimeout)
  saveTimeout = window.setTimeout(saveAutosave, 300)
}

const handleCodeUpdate = (newCode: string) => {
  code.value = newCode
  debounceSave()
}

// 上传文件读取
const handleFileUpload = (file: File) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    code.value = e.target?.result as string
    debounceSave() // 上传后立即保存
    ElMessage.success('代码已从文件导入')
  }
  reader.readAsText(file)
  return false // 阻止自动上传
}


// 提交代码并获取评测结果
const submitCode = async () => {
  if (!code.value.trim()) {
    ElMessage.warning('请编写代码后再提交')
    return
  }

  try {
    submitting.value = true
    executionTime.value = 0
    const startTime = performance.now()
    console.log('提交评测请求体:', {
      problemId: problem.value.id,
      code: code.value,
    })

    console.log('problem.value:', problem.value)
    console.log('problem.value.id:', problem.value.id)
    console.log('problemId.value:', problemId.value)

    const response = await axios.post('http://127.0.0.1:8000/api/experiments/judge/', {
      problemId: Number(problem.value.id),
      code: code.value,
    }, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })

    console.log("后端响应：", response.data);

    executionTime.value = performance.now() - startTime
    result.value = response.data.result

    // 显示评测结果
    if (result.value?.passed === result.value?.total) {
      ElMessage.success(`恭喜！全部 ${result.value?.total} 个测试用例通过`)
    } else {
      ElMessage.warning(`通过 ${result.value?.passed}/${result.value?.total} 个测试用例`)
    }
  } catch (error: unknown) {
    const err = error as AxiosError
    if (err.response) {
      const { status, data } = err.response
      if (status === 400) {
        ElMessage.error(`提交错误: ${data.error}`)
      } else if (status === 404) {
        ElMessage.error('题目不存在')
      } else {
        ElMessage.error(`评测失败: ${data.detail || '未知错误'}`)
      }
    } else {
      ElMessage.error('网络连接失败，请检查网络后重试')
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchProblem()
  loadAutosave()
  window.addEventListener('beforeunload', saveAutosave)
})

onUnmounted(() => {
  window.removeEventListener('beforeunload', saveAutosave)
  saveAutosave() // 确保在离开页面前保存
})
</script>

<style scoped>
.coding-editor {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  height: calc(100vh - 64px);
}

.problem-panel {
  overflow-y: auto;
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.editor-panel {
  background: #1e1e1e;
  border-radius: 8px;
  overflow: hidden;
  padding: 5px;
}

.result-panel {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.case-item {
  margin: 15px 0;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.io-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
  margin-top: 10px;
}

.io-cell {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 0.9em;
}

.io-cell label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
  font-size: 0.8em;
  color: #606266;
}

.io-cell pre {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  white-space: pre-wrap;
  background: #fff;
  padding: 5px;
  border-radius: 3px;
  margin: 0;
  max-height: 150px;
  overflow: auto;
}

.error {
  color: #f56c6c;
}
</style>
