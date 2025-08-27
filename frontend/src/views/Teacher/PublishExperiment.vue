<template>
  <div class="publish-set">
    <el-card class="set-card">
      <h2>{{ isEditMode ? '编辑实验' : '创建实验' }}</h2>
      <el-form :model="setForm" label-width="100px">
        <el-form-item label="实验名称" required>
          <el-input v-model="setForm.title" placeholder="如：数组与字符串题组" />
        </el-form-item>

        <el-form-item label="实验描述" required>
          <el-input v-model="setForm.description" placeholder="如：描述实验的目的和内容" />
        </el-form-item>

        <!-- 新增：开始时间 -->
        <el-form-item label="开始时间" required>
          <el-date-picker
            v-model="setForm.start_time"
            type="datetime"
            placeholder="选择开始时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="截止时间" required>
          <el-date-picker
            v-model="setForm.deadline"
            type="datetime"
            placeholder="选择截止时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>

        <el-form-item label="选择学生" required>
          <el-transfer
            v-model="setForm.selectedStudents"
            :data="allStudents"
            :titles="['未选学生', '已选学生']"
            :props="{ key: 'id', label: 'name' }"
          />
        </el-form-item>

        <el-form-item label="提交设置" class="compact-form-item">
          <div class="inline-settings">
            <el-switch
              v-model="setForm.allow_late_submission"
              active-text="允许补交"
              inactive-text="禁止补交"
            />

            <el-input-number
              v-if="setForm.allow_late_submission"
              v-model="setForm.late_submission_penalty"
              :min="0"
              :max="100"
              :step="5"
              size="small"
              style="width: 120px; margin-left: 15px"
            >
              <template #append>%</template>
            </el-input-number>

          </div>
          <span v-if="setForm.allow_late_submission" class="hint-text">
              设置补交时扣分比例（0%表示允许但不扣分）
          </span>
        </el-form-item>

        <el-divider>题目列表</el-divider>
        <div v-for="(q, index) in setForm.questions" :key="q.id" class="question-card">
          <el-card shadow="always" class="question-form">
            <template #header>
              <div class="q-header">
                <span>题目 {{ index + 1 }}</span>
                <el-button type="danger" size="small" @click="removeQuestion(index)"
                  >删除</el-button
                >
              </div>
            </template>

            <el-form-item label="题目类型" required>
              <el-select v-model="q.type" placeholder="选择类型">
                <el-option label="选择题" value="choice" />
                <el-option label="填空题" value="blank" />
                <el-option label="编程题" value="code" />
              </el-select>
            </el-form-item>

            <el-form-item label="题干" required>
              <el-input v-model="q.description" type="textarea" rows="3" placeholder="请输入题目描述" />
            </el-form-item>

            <el-form-item label="分值" required>
              <el-input-number v-model="q.score" :min="1" :max="100" />
            </el-form-item>

            <el-form-item label="题目顺序" required>
              <el-input-number v-model="q.order" :min="0" />
            </el-form-item>

            <!-- 选择题配置 -->
            <template v-if="q.type === 'choice'">
              <el-form-item label="选项" required>
                <div v-for="(opt, optIndex) in q.options" :key="optIndex">
                  <el-input v-model="opt.text" placeholder="选项文本" style="margin-bottom: 5px" />
                  <el-radio v-model="q.correct_answer" :label="String(opt.id)">
                    设置为正确答案
                  </el-radio>
                  <el-button type="danger" size="small" @click="removeOption(q, optIndex)">
                    删除选项
                  </el-button>
                </div>
                <el-button type="primary" size="small" @click="addOption(q)">
                  添加选项
                </el-button>
              </el-form-item>
            </template>

            <!-- 填空题 -->
            <template v-else-if="q.type === 'blank'">
              <el-form-item label="标准答案" required>
                <el-input v-model="q.correct_answer" placeholder="请输入标准答案" />
              </el-form-item>
            </template>

            <!-- 编程题 -->
            <template v-else-if="q.type === 'code'">
              <el-form-item label="时间限制" required>
                <el-input v-model.number="q.timeout" placeholder="请输入时间限制（秒）" />
              </el-form-item>
              <el-form-item label="内存限制" required>
                <el-input v-model.number="q.mem_limit" placeholder="请输入内存限制（MB）" />
              </el-form-item>
              <el-form-item label="添加测试点">
                <el-button type="primary" size="small" @click="addTestcase(q)"
                  >添加测试点</el-button
                >
              </el-form-item>
              <div v-for="(t, i) in q.test_cases" :key="i" class="testcase">
                <el-input
                  v-model="t.input"
                  placeholder="输入"
                  style="width: 45%; margin-right: 10px"
                />
                <el-input v-model="t.output" placeholder="期望输出" style="width: 45%" />
                <el-button type="danger" size="small" @click="q.test_cases.splice(i, 1)"
                  >删除</el-button
                >
              </div>
            </template>
          </el-card>
        </div>

        <el-form-item>
          <el-button type="primary" plain @click="addQuestion">添加题目</el-button>
        </el-form-item>

        <el-form-item>
          <el-button type="success" @click="submitSet">{{ isEditMode ? '更新实验' : '发布实验' }}</el-button>
          <el-button v-if="isEditMode" @click="cancelEdit">取消编辑</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 展示已发布实验 -->
    <el-divider />
    <div class="published-list">
      <h3>已发布实验</h3>
      <template v-if="publishedSets.length">
        <el-card
          v-for="set in publishedSets"
          :key="set.id"
          class="set-item"
          shadow="hover"
        >
          <div style="display: flex; justify-content: space-between; align-items: center; cursor: pointer" @click="editSet(set)">
            <div>
              <h4>{{ set.title || '未命名实验' }}</h4>
              <p>开始时间: {{ formatDateTime(set.start_time) }}</p>
              <p>截止时间: {{ formatDateTime(set.deadline) }}</p>
              <p>参与学生数量: {{ set.students?.length || 0 }}</p>
              <p class="teacher-info">发布教师: {{ set.teacher?.username || '未知' }}</p>
            </div>
            <el-button
              type="danger"
              size="small"
              @click.stop="deleteSet(set.id)"
              >删除</el-button>
          </div>
        </el-card>
      </template>
      <el-empty v-else description="暂无实验数据" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { NoticeApi } from '@/api/notice'

interface Student {
  id: number
  username: string
  name: string
}

interface TestCase {
  input: string
  output: string
}

interface BaseProblem {
  id?: number
  description: string
  score: number
  order: number
  type: 'choice' | 'blank' | 'code'  // <--- 必须有这个
}

interface ChoiceProblem extends BaseProblem {
  type: 'choice'
  correct_answer?: string
  options: { id: number; text: string }[]
}
interface FillProblem extends BaseProblem {
  type: 'blank'
  correct_answer?: string
}
interface CodingProblem extends BaseProblem {
  type: 'code'
  timeout?: number
  mem_limit?: number
  test_cases: TestCase[]
}

interface QuestionSet {
  id?: number
  title: string
  description: string // 新增实验描述字段
  start_time: string // 新增开始时间字段
  deadline: string
  teacher?: number
  students?: Student[] // 学生列表
  selectedStudents: number[]

  questions: (ChoiceProblem | FillProblem | CodingProblem)[]
  allow_late_submission: boolean  // 新增是否允许补交字段
  late_submission_penalty?: number // 迟交扣分比例
}

// 学生数据
const allStudents = ref<Student[]>([])

// 表单数据
const setForm = ref<QuestionSet>({
  title: '',
  description: '',
  start_time: '',
  deadline: '',
  selectedStudents: [],      // 只用 selectedStudents 作为选中学生ID数组
  students: [],  // 确保初始化为数组
  allow_late_submission: false,  // 新增是否允许补交字段
  late_submission_penalty: 0, // 迟交扣分比例
  questions: [   // 预置一个空题目
    {
      type: 'choice',
      description: '',
      correct_answer: '',
      score: 10,
      order: 1,
      options: [{ id: 1, text: '' }],
    }
  ]
})

// 已发布实验列表
const publishedSets = ref<QuestionSet[]>([])

// 是否处于编辑模式
const isEditMode = ref(false)
const editingSetId = ref<number | null>(null)

// 更完善的日期格式化
const formatDateTime = (dateString: string) => {
  if (!dateString) return '未设置';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).replace(/\//g, '-');
}
// 获取学生列表
const fetchStudents = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/students/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
      withCredentials: true // 跨域请求带上cookie
    });

    // 调试日志
    console.log('响应状态:', response.status);
    console.log('响应头:', response.headers);
    console.log('响应数据:', response.data);

    allStudents.value = response.data.map(student => ({
      id: student.id,
      username: student.username,
      name: student.username // 使用username作为name
    }));

  } catch (error) {
    console.error('获取学生列表失败:', {
      error: error.message,
      response: error.response
    });

    let errorMessage = '获取学生列表失败';
    if (error.response) {
      if (error.response.status === 401) {
        errorMessage = '认证失败，请重新登录';
      } else if (error.response.data) {
        errorMessage += `: ${JSON.stringify(error.response.data)}`;
      }
    } else {
      errorMessage += `: ${error.message}`;
    }

    ElMessage.error(errorMessage);
  }
}

// 获取已发布实验
const fetchPublishedSets = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/experiments/experiments/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
      withCredentials: true // 跨域请求带上cookie
    });

    // 调试日志
    console.log('实验列表响应状态:', response.status);
    console.log('实验列表响应头:', response.headers);
    console.log('实验列表响应数据:', response.data);

    publishedSets.value = response.data.map((set: any) => ({
      id: set.id,
      title: set.title,
      start_time: set.start_time, // 新增开始时间字段
      deadline: set.deadline,
      questions: set.questions,
      students: set.students,
      teacher: set.teacher,
      allow_late_submission: set.allow_late_submission,
      late_submission_penalty: set.late_submission_penalty,
      // 其他需要的字段...
    }));

  } catch (error) {
    console.error('获取实验列表失败:', {
      error: error.message,
      response: error.response
    });

    let errorMessage = '获取实验列表失败';
    if (error.response) {
      if (error.response.status === 401) {
        errorMessage = '认证失败，请重新登录';
      } else if (error.response.data) {
        errorMessage += `: ${JSON.stringify(error.response.data)}`;
      }
    } else {
      errorMessage += `: ${error.message}`;
    }

    ElMessage.error(errorMessage);
  }
}

// 创建新题目模板
const newQuestion = (type: 'choice' | 'blank' | 'code'): ChoiceProblem | FillProblem | CodingProblem => {
  const base = {
    description: '',
    correct_answer: '',
    score: 10,
    order: setForm.value.questions.length > 0
      ? Math.max(...setForm.value.questions.map(q => q.order)) + 1
      : 1,
    type
  }

  if (type === 'choice') {
    return {
      ...base,
      type: 'choice', // 需要明确指定
      options: [{ id: 1, text: '' }]
    }
  } else if (type === 'code') {
    return {
      ...base,
      type: 'code',
      timeout: 1,
      mem_limit: 128,
      test_cases: [{ input: '', output: '' }]
    }
  } else {
    return {
      ...base,
      type: 'blank' // 明确是填空题
    }
  }
}

// 添加题目
const addQuestion = () => {
  setForm.value.questions.push(newQuestion('choice'))
}

// 删除题目
// 删除题目（带确认对话框）
const removeQuestion = async (index: number) => {
  try {
    const question = setForm.value.questions[index];

    // 如果是编辑模式且题目有ID，弹出确认对话框
    if (isEditMode.value && question?.id) {
      await ElMessageBox.confirm(
        '确定要删除这个题目吗？此操作不可恢复。',
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      );

      // 调用API删除题目
      let endpoint = '';
      switch (question.type) {
        case 'choice':
          endpoint = 'choice-problems';
          break;
        case 'blank':
          endpoint = 'fill-problems';
          break;
        case 'code':
          endpoint = 'coding-problems';
          break;
      }

      await axios.delete(
        `http://127.0.0.1:8000/api/experiments/${endpoint}/${question.id}/`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          },
          withCredentials: true
        }
      );

      ElMessage.success('题目删除成功');
    }

    // 从当前表单中移除题目
    setForm.value.questions.splice(index, 1);

    // 更新题目顺序
    setForm.value.questions.forEach((q, i) => {
      q.order = i + 1;
    });

  } catch (error) {
    if (error !== 'cancel') { // 用户点击了取消按钮
      console.error('删除题目失败:', error);
      ElMessage.error('删除题目失败: ' + (error.response?.data?.message || error.message));
    }
  }
}

// 添加测试用例
const addTestcase = (q: CodingProblem) => {
  if (!q.test_cases) {
    q.test_cases = []
  }
  q.test_cases.push({ input: '', output: '' })
}

// 选择题：添加选项
const addOption = (q: ChoiceProblem) => {
  if (!q.options) q.options = []
  const newId = q.options.length > 0
    ? Math.max(...q.options.map(o => o.id)) + 1
    : 1
  const newOption = {
    id: q.options.length + 1,
    text: ''
  }
  q.options.push(newOption)
}

// 选择题：删除选项
const removeOption = (q: ChoiceProblem, optIndex: number) => {
if (q.correct_answer === String(q.options?.[optIndex]?.id)) {
    q.correct_answer = ''
  }
  q.options?.splice(optIndex, 1)
}

const noticeForm = ref({
  title: '',
  content: '',
  type: 2, // 默认设置为课程通知类型
})

// 提交实验
const submitSet = async () => {
  try {
    // 验证迟交设置
    if (setForm.value.allow_late_submission &&
        (setForm.value.late_submission_penalty === undefined ||
        setForm.value.late_submission_penalty < 0)) {
      ElMessage.error('请设置有效的迟交扣分比例')
      return
    }

    // 验证表单
    if (!setForm.value.title) {
      ElMessage.error('请输入实验名称')
      return
    }
    if (!setForm.value.start_time) {
      ElMessage.error('请设置开始时间')
      return
    }
    if (!setForm.value.deadline) {
      ElMessage.error('请设置截止时间')
      return
    }
    if (setForm.value.questions.length === 0) {
      ElMessage.error('请至少添加一个题目')
      return
    }
    if (setForm.value.selectedStudents.length === 0) {
      ElMessage.error('请至少选择一个学生')
      return
    }

    // 准备请求头
    const headers = {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    }

    // 1. 准备实验数据
    const experimentPayload = {
      title: setForm.value.title,
      description: setForm.value.description,
      start_time: setForm.value.start_time,
      deadline: setForm.value.deadline,
      students: setForm.value.selectedStudents,
      allow_late_submission: setForm.value.allow_late_submission,
      late_submission_penalty: setForm.value.late_submission_penalty || 0,
      questions: setForm.value.questions.map(q => ({
        id: q.id, // 保留题目ID
        type: q.type === 'blank' ? 'fill' : q.type,
        description: q.description,  // 使用description而不是prompt
        correct_answer: q.type ==='choice' || q.type === 'blank' ? q.correct_answer : undefined,
        score: q.score,
        order: q.order,
        test_cases: q.type === 'code' ? (q.test_cases || []) : undefined,
        options: q.type === 'choice' ? (q.options || []) : undefined,
        timeout: q.type === 'code' ? q.timeout : undefined,
        mem_limit: q.type === 'code' ? q.mem_limit : undefined
      }))
    }

    console.log('提交的数据:', JSON.stringify(experimentPayload, null, 2))

    // 获取当前实验的所有题目ID（编辑模式下）
    let currentQuestionIds: number[] = [];
    if (isEditMode.value && editingSetId.value) {
      const currentSet = publishedSets.value.find(s => s.id === editingSetId.value);
      currentQuestionIds = currentSet?.questions?.map(q => q.id) || [];
    }

    // 计算要删除的题目ID
    const deletedQuestionIds = currentQuestionIds.filter(
      id => !setForm.value.questions.some(q => q.id === id)
    );

    // 如果是编辑模式，添加删除的题目ID到payload
    if (isEditMode.value && editingSetId.value) {
      experimentPayload.deleted_questions = deletedQuestionIds;
    }

    let response;
    if (isEditMode.value && editingSetId.value) {
      // 更新实验 - 使用PUT
      response = await axios.put(
        `http://127.0.0.1:8000/api/experiments/experiments/${editingSetId.value}/`,
        {
          ...experimentPayload,
          deleted_questions: deletedQuestionIds
        },
        { headers }
      );
      ElMessage.success('实验更新成功');
    } else {
      // 创建实验 - 使用POST
      response = await axios.post(
        'http://127.0.0.1:8000/api/experiments/experiments/',
        experimentPayload,
        { headers }
      );
      ElMessage.success('实验创建成功');
      // 实验创建成功后，自动创建公告
      await createExperimentNotice(response.data.id);
    }

    // 2. 处理题目数据
    await processQuestions(editingSetId.value || response.data.id, headers)

    // 2. 重置表单并刷新
    resetForm()
    await fetchPublishedSets()


  } catch (error) {
    console.error('提交实验失败:', error)
    let errorMessage = '提交实验失败'
    if (error.response?.data) {
      errorMessage += `: ${JSON.stringify(error.response.data)}`
    }
    ElMessage.error(errorMessage)
  }
}

const processQuestions = async (experimentId: number, headers: any) => {
  const questionPromises = setForm.value.questions.map(async (q) => {
    const basePayload: any = {
      experiment: experimentId,
      description: q.description || '',
      score: Number(q.score) || 10,
      order: Number(q.order) || 0
    }

    if (q.type === 'choice') {
      const payload = {
        ...basePayload,
        correct_answer: q.correct_answer || '',
        options: q.options || []
      }
      if(q.id) {
        return axios.put(`http://127.0.0.1:8000/api/experiments/choice-problems/${q.id}/`, payload, { headers })
      } else {
        return axios.post('http://127.0.0.1:8000/api/experiments/choice-problems/', payload, { headers })
      }
    } else if (q.type === 'blank') {
      // 填空题 → API识别为 fill-problems
      basePayload.correct_answer = q.correct_answer || ''
      if(q.id) {
        return axios.put(`http://127.0.0.1:8000/api/experiments/fill-problems/${q.id}/`, basePayload, { headers })
      } else {
        return axios.post('http://127.0.0.1:8000/api/experiments/fill-problems/', basePayload, { headers })
      }
    } else if (q.type === 'code') {
      const payload = {
        ...basePayload,
        test_cases: q.test_cases || [],
        timeout: q.timeout || 1,
        mem_limit: q.mem_limit || 128
      }
      if(q.id) {
        return axios.put(`http://127.0.0.1:8000/api/experiments/coding-problems/${q.id}/`, payload, { headers })
      }else{
        return axios.post('http://127.0.0.1:8000/api/experiments/coding-problems/', payload, { headers })
      }
    }
    console.log("请求数据：", q.type, basePayload)
  })

  await Promise.all(questionPromises)
  ElMessage.success('题目处理成功')
  console.log('所有题目处理完成')
  // 重置题目顺序
  setForm.value.questions.forEach((q, index) => {
    q.order = index + 1
  })
  console.log('题目顺序已重置')
}

// 编辑实验
const editSet = async (set: QuestionSet) => {
  try {
    isEditMode.value = true
    editingSetId.value = set.id
    console.log('从服务器获取的数据:', {
      id: set.id,
      title: set.title,
      description: set.description,
      start_time: set.start_time,
      deadline: set.deadline,
      students: set.students,
      allow_late_submission: set.allow_late_submission,
      late_submission_penalty: set.late_submission_penalty || 0,
      questions: set.questions
    })

    // 从服务器获取完整实验数据
    const response = await axios.get(`http://127.0.0.1:8000/api/experiments/experiments/${set.id}/`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      }
    })

    const fullSetData = response.data

    // 安全处理 students 数据
    const students = Array.isArray(set.students) ?
      set.students.map((s: any) => s.id) :
      []

    // 安全处理 questions 数据
    const questions = []

    // 处理选择题
    if (fullSetData.choice_problems) {
      fullSetData.choice_problems.forEach((q: any) => {
        questions.push({
          id: q.id,
          type: 'choice',
          description: q.description,
          correct_answer: String(q.correct_answer),
          score: q.score,
          order: q.order,
          options: q.options || []
        })
      })
    }

    // 处理填空题
    if (fullSetData.fill_problems) {
      fullSetData.fill_problems.forEach((q: any) => {
        questions.push({
          id: q.id,
          type: 'blank',
          description: q.description,
          correct_answer: q.correct_answer,
          score: q.score,
          order: q.order
        })
      })
    }

    // 处理编程题
    if (fullSetData.coding_problems) {
      fullSetData.coding_problems.forEach((q: any) => {
        questions.push({
          id: q.id, // 确保编程题也有 id
          type: 'code',
          description: q.description,
          score: q.score,
          order: q.order,
          timeout: q.timeout,
          mem_limit: q.mem_limit,
          test_cases: q.test_cases || []
        })
      })
    }

     // 按order排序题目
    questions.sort((a, b) => a.order - b.order)

    // 填充表单
    setForm.value = {
      id: fullSetData.id,
      title: fullSetData.title,
      description: fullSetData.description || '',
      start_time: fullSetData.start_time,
      deadline: fullSetData.deadline,
      selectedStudents: fullSetData.students,
      students: fullSetData.students,
      allow_late_submission: fullSetData.allow_late_submission || false,
      late_submission_penalty: fullSetData.late_submission_penalty || 0,
      questions: questions
    }
  } catch (error) {
    console.error('加载实验详情失败:', error)
    ElMessage.error('加载实验详情失败')
  }
}

// 新增函数：创建实验公告
const createExperimentNotice = async (experimentId: number) => {
  try {
    // 获取实验详情以获取实验名称和时间
    const expResponse = await axios.get(
      `http://127.0.0.1:8000/api/experiments/experiments/${experimentId}/`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const experiment = expResponse.data;

    // 准备公告内容
    const noticeContent = `
      新实验已发布：${experiment.title}

      实验描述：${experiment.description}

      开始时间：${formatDateTime(experiment.start_time)}
      截止时间：${formatDateTime(experiment.deadline)}

      请按时完成实验！
    `;

    // 创建公告
    await NoticeApi.createNotice({
      title: `新实验发布：${experiment.title}`,
      content: noticeContent,
      type: 2, // 课程通知类型
      related_experiment: experimentId // 如果有关联实验的字段
    });

    ElMessage.success('实验公告已自动发布');
  } catch (error) {
    console.error('创建实验公告失败:', error);
    ElMessage.error('自动创建实验公告失败，请手动创建');
  }
}

// 取消编辑
const cancelEdit = () => {
  isEditMode.value = false
  editingSetId.value = null
  resetForm()
}

// 重置表单
const resetForm = () => {
  setForm.value = {
    title: '',
    start_time: '', // 新增开始时间字段
    deadline: '',
    description: '',
    selectedStudents: [],
    allow_late_submission: false,
    late_submission_penalty: 0,
    questions: []
  }
  isEditMode.value = false
  editingSetId.value = null
}

const route = useRoute()
// 在组件挂载时获取数据
onMounted(async () => {
  await fetchStudents()
  await fetchPublishedSets()

  // 检查是否有编辑参数

  if (route.params.id) {
    const setId = parseInt(route.params.id as string)
    const setToEdit = publishedSets.value.find(s => s.id === setId)
    if (setToEdit) {
      editSet(setToEdit)
    }
  }
})
// 删除实验（带确认对话框）
const deleteSet = async (id: number) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个实验吗？此操作不可恢复。',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );

    await axios.delete(
      `http://127.0.0.1:8000/api/experiments/experiments/${id}/`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        withCredentials: true
      }
    );

    ElMessage.success('删除成功');
    await fetchPublishedSets();
    if (editingSetId.value === id) {
      cancelEdit();
    }
  } catch (error) {
    if (error !== 'cancel') { // 用户点击了取消按钮
      console.error('删除实验失败:', error);
      ElMessage.error('删除实验失败: ' + (error.response?.data?.message || error.message));
    }
  }
}
</script>

<style scoped lang="scss">
.publish-set {
  padding: 20px;

  .set-card {
    margin-bottom: 30px;
  }

  .question-card {
    margin-bottom: 15px;
  }

  .q-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .testcase {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
  }

  .published-list {
    margin-top: 20px;

    .set-item {
      margin-bottom: 15px;
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }

      h4 {
        color: #409eff;
        margin-bottom: 10px;
      }

      p {
        margin: 6px 0;
        color: #666;
        font-size: 14px;

        &.teacher-info {
          color: #888;
          font-style: italic;
        }
      }
    }
  }
}
</style>
