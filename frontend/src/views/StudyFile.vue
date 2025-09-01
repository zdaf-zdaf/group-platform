<template>
  <div class="material-page">
    <!-- 搜索过滤栏 -->
    <div class="filter-bar">
      <el-input
        v-model="searchText"
        placeholder="搜索资料名称/描述..."
        clearable
        style="width: 300px"
        @change="loadMaterials"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-select
        v-model="filterType"
        placeholder="全部类型"
        clearable
        style="margin-left: 15px; width: 150px"
        @change="loadMaterials"
      >
        <el-option
          v-for="type in materialTypes"
          :key="type.value"
          :label="type.label"
          :value="type.value"
        />
      </el-select>
      <!-- 发布资料按钮 -->
      <el-button v-if="!authStore.isStudent" type="primary" style="margin-left: 15px" @click="toggleMaterialForm">
        发布学习资料
      </el-button>
    </div>

    <!-- 加载状态 -->
    <el-skeleton :rows="5" animated v-if="loading" />

    <!-- 错误提示 -->
    <el-alert v-if="error" :title="error" type="error" show-icon closable />

    <!-- 发布学习资料表单 -->
    <el-card v-if="isMaterialFormVisible" class="set-card">
      <h2>{{ materialForm.isEdit ? '编辑学习资料' : '发布学习资料' }}</h2>
      <el-form :model="materialForm" label-width="100px">
        <el-form-item label="资料标题" required>
          <el-input v-model="materialForm.title" placeholder="请输入资料标题" />
        </el-form-item>

        <el-form-item label="资料描述">
          <el-input
            v-model="materialForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入资料描述"
          />
        </el-form-item>

        <el-form-item label="资料类型" required>
          <el-select v-model="materialForm.type" placeholder="选择资料类型" :teleported="false">
            <el-option
              v-for="type in materialTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="materialForm.isEdit ? '更新文件' : '资料文件'" required>
          <el-upload
            class="upload-demo"
            action="#"
            :on-change="handleMaterialChange"
            :file-list="materialForm.files"
            :auto-upload="false"
            :limit="1"
            accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.mp4"
          >
            <template #trigger>
              <el-button type="primary">选择文件</el-button>
            </template>
            <template #tip>
              <div class="el-upload__tip">
                支持PDF、Word、图片和视频文件，大小不超过100MB
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitMaterial" :loading="submitting">
            {{ materialForm.isEdit ? '更新资料' : '发布资料' }}
          </el-button>
          <el-button @click="isMaterialFormVisible = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 资料列表 -->
    <el-scrollbar height="calc(100vh - 180px)" v-if="!loading && !error">
      <div class="material-list">
        <el-card
          v-for="material in filteredMaterials"
          :key="material.id"
          class="material-item"
          shadow="hover"
        >
          <div class="material-header">
            <!-- 类型图标 -->
            <el-icon :size="28" :color="materialTypeMap[material.type].color">
              <component :is="materialTypeMap[material.type].icon" />
            </el-icon>
            <div class="title-wrapper">
              <h3 class="title">{{ material.title }}</h3>
              <div class="meta">
                <span class="size">{{ formatFileSize(material.size) }}</span>
                <el-divider direction="vertical" />
                <span class="downloads">下载 {{ material.downloads }} 次</span>
                <el-divider direction="vertical" />
                <span class="date">{{ material.formatted_date }}</span>
              </div>
            </div>
            <el-tag
              :type="materialTypeMap[material.type].tagType"
              effect="light"
              class="type-tag"
            >
              {{ materialTypeMap[material.type].label }}
            </el-tag>
          </div>

          <!-- 资料描述 -->
          <div class="description">{{ material.description }}</div>

          <!-- 预览与操作 -->
          <div class="preview-section">
            <!-- PDF预览 - 改为链接方式 -->
            <div v-if="material.type === 'pdf'" class="pdf-preview">
              <!-- 修复：将 type="text" 改为 link -->
              <el-button type="link" @click="handlePreview(material)">
                <el-icon><Document /></el-icon> 点击查看PDF
              </el-button>
            </div>

            <!-- 视频预览 -->
            <div v-else-if="material.type === 'video'" class="video-preview">
              <video controls :src="material.previewUrl" style="max-height: 300px">
                您的浏览器不支持视频播放
              </video>
            </div>

            <!-- 图片预览 -->
            <div v-else-if="material.type === 'image'" class="image-preview">
              <el-image
                :src="material.previewUrl"
                :preview-src-list="[material.previewUrl]"
                fit="contain"
                style="max-height: 300px;"
              />
            </div>

            <!-- 通用文件操作 -->
            <div class="actions">
              <el-button
                type="primary"
                @click="handleDownload(material)"
                :icon="Download"
                :loading="downloadingId === material.id"
              >
                下载文件
              </el-button>
              <el-button
                @click="handlePreview(material)"
                :icon="View"
              >
                在线预览
              </el-button>
              <!-- 编辑和删除按钮 -->
              <el-button
                v-if="!authStore.isStudent"
                size="small"
                @click="editMaterial(material)"
              >
                编辑
              </el-button>
              <el-button
                v-if="!authStore.isStudent"
                size="small"
                type="danger"
                @click="deleteMaterial(material.id)"
              >
                删除
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search, Download, View, Document, VideoPlay, Picture } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/authStore'
import { MaterialApi, type LearningMaterial } from '@/api/material'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadFile } from 'element-plus'

const authStore = useAuthStore()
const loading = ref(false)
const submitting = ref(false)
const downloadingId = ref<number | null>(null)
const error = ref<string | null>(null)

// 类型配置
const materialTypes = [
  { value: 'pdf', label: 'PDF文档', icon: Document, color: '#f56c6c', tagType: 'danger' },
  { value: 'video', label: '视频教程', icon: VideoPlay, color: '#e6a23c', tagType: 'warning' },
  { value: 'doc', label: '文档资料', icon: Document, color: '#409eff', tagType: 'primary' },
  { value: 'image', label: '图表素材', icon: Picture, color: '#67c23a', tagType: 'success' }
]

const materialTypeMap = Object.fromEntries(
  materialTypes.map(t => [t.value, t])
)

// 数据
const materials = ref<LearningMaterial[]>([])
const searchText = ref('')
const filterType = ref<string | null>(null)
const isMaterialFormVisible = ref(false)
const materialForm = ref({
  id: 0,
  title: '',
  description: '',
  type: 'pdf',
  files: [] as UploadFile[],
  isEdit: false
})

// 加载学习资料
const loadMaterials = async () => {
  try {
    loading.value = true
    error.value = null
    const data = await MaterialApi.getMaterials(searchText.value, filterType.value || undefined)

    materials.value = data.map(item => ({
      ...item,
      // 关键修复：直接使用后端提供的URL，不做额外编码
      previewUrl: `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'}${item.file_url}`,
      formatted_date: formatDate(item.created_at)
    }))
  } catch (err: any) {
    console.error('加载学习资料失败:', err)
    error.value = err.response?.data?.message || err.message || '加载资料失败，请稍后重试'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// 初始化加载数据
onMounted(loadMaterials)

// 搜索过滤
const filteredMaterials = computed(() => {
  return materials.value.filter(m => {
    const matchText = searchText.value
      ? m.title.toLowerCase().includes(searchText.value.toLowerCase()) ||
        m.description.toLowerCase().includes(searchText.value.toLowerCase())
      : true

    const matchType = filterType.value
      ? m.type === filterType.value
      : true

    return matchText && matchType
  }).sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
})

const toggleMaterialForm = () => {
  isMaterialFormVisible.value = !isMaterialFormVisible.value
  if (!isMaterialFormVisible.value) {
    resetForm()
  }
}

// 处理上传的文件
const handleMaterialChange = (file: UploadFile) => {
  // 检查文件大小 (100MB限制)
  if (file.size && file.size > 100 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过100MB')
    return false
  }

  // 检查文件类型
  const allowedTypes = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'mp4']
  const fileExt = file.name.split('.').pop()?.toLowerCase()
  if (!fileExt || !allowedTypes.includes(fileExt)) {
    ElMessage.error('不支持的文件类型')
    return false
  }

  materialForm.value.files = [file]
}

// 提交学习资料
const submitMaterial = async () => {
  try {
    // 验证表单
    if (!materialForm.value.title.trim()) {
      ElMessage.warning('请输入资料标题')
      return
    }

    if (!materialForm.value.type) {
      ElMessage.warning('请选择资料类型')
      return
    }

    // 关键修改：编辑时允许不重新上传文件
    if (!materialForm.value.files.length && !materialForm.value.isEdit) {
      ElMessage.warning('请上传资料文件')
      return
    }

    submitting.value = true;
    const formData = new FormData();

    // 添加基本字段
    formData.append('title', materialForm.value.title);
    formData.append('description', materialForm.value.description);
    formData.append('type', materialForm.value.type);

    // 文件处理
    if (materialForm.value.files[0]?.raw) {
      formData.append('file', materialForm.value.files[0].raw);
    }else if (materialForm.value.isEdit) {
      // 编辑操作但没有选择新文件
      ElMessage.warning('暂不更新文件内容');
    }

    try {
      const response = materialForm.value.isEdit
        ? await MaterialApi.updateMaterial(materialForm.value.id, formData)
        : await MaterialApi.createMaterial(formData);

      ElMessage.success(materialForm.value.isEdit ? '资料更新成功' : '资料发布成功');
      await loadMaterials();
      resetForm();
      isMaterialFormVisible.value = false;
    } catch (err: any) {
      // 针对编辑操作但没有选择文件的特殊处理
      if (materialForm.value.isEdit && !materialForm.value.files.length) {
        ElMessage.error('请重新选择文件或点击"更新资料"保存其他修改');
      } else {
        const errorMsg = err.response?.data?.file?.[0] ||
                        err.response?.data?.error || // 关键修改：使用后端返回的error字段
                        err.response?.data?.detail ||
                        err.message ||
                        '操作失败，请检查数据';
        ElMessage.error(errorMsg);
      }
    }
  } catch (err: any) {
    console.error('提交失败:', err);
    ElMessage.error('提交过程中发生错误，请重试');
  } finally {
    submitting.value = false;
  }
};

// 重置表单
const resetForm = () => {
  materialForm.value = {
    id: 0,
    title: '',
    description: '',
    type: 'pdf',
    files: [],
    isEdit: false
  }
}

// 编辑学习资料
const editMaterial = (material: LearningMaterial) => {
  materialForm.value = {
    id: material.id,
    title: material.title,
    description: material.description,
    type: material.type,
    files: [],
    isEdit: true
  }
  isMaterialFormVisible.value = true
}

// 删除学习资料
const deleteMaterial = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定删除该学习资料吗？此操作不可撤销', '警告', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    })

    await MaterialApi.deleteMaterial(id)
    ElMessage.success('删除成功')
    await loadMaterials()
  } catch (err: any) {
    if (err !== 'cancel') {
      console.error('删除学习资料失败:', err)
      ElMessage.error(err.message || '删除失败')
    }
  }
}

// 下载文件
const handleDownload = async (material: LearningMaterial) => {
    downloadingId.value = material.id;

    // 获取文件Blob
    const response = await fetch(material.previewUrl);
    const blob = await response.blob();

    // 创建下载链接
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', material.file_name || `material_${material.id}`);
    document.body.appendChild(link);
    link.click();

    // 清理
    window.URL.revokeObjectURL(url);
    document.body.removeChild(link);

    // 更新下载计数
    await MaterialApi.incrementDownloadCount(material.id);
    material.downloads += 1;
}

// 预览文件
const handlePreview = (material: LearningMaterial) => {
  if (!material.previewUrl) {
    ElMessage.warning('该文件不支持预览');
    return;
  }

  try {
    // 特殊处理文档类型
    if (['doc', 'docx'].includes(material.type)) {
      // 使用Office Online预览
      const officePreviewUrl = `https://view.officeapps.live.com/op/view.aspx?src=${material.previewUrl}`;
      window.open(officePreviewUrl, '_blank');
      return;
    }

    // 其他文件类型直接在新标签页打开
    window.open(material.previewUrl, '_blank');
  } catch (err) {
    ElMessage.error('预览失败，请稍后重试');
  }
}

// 辅助函数 - 格式化文件大小
const formatFileSize = (bytes: number) => {
  const units = ['B', 'KB', 'MB', 'GB'];
  if (bytes === 0) return '0 B';

  const exponent = Math.floor(Math.log(bytes) / Math.log(1024));
  const size = parseFloat((bytes / Math.pow(1024, exponent)).toFixed(1));

  return `${size} ${units[exponent]}`;
}

// 辅助函数 - 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString);

  // 格式化为: YYYY-MM-DD HH:MM
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');

  return `${year}-${month}-${day} ${hours}:${minutes}`;
}
</script>

<style scoped lang="scss">
.material-page {
  padding: 20px;
  height: 100%;

  .filter-bar {
    margin-bottom: 20px;
    display: flex;
    align-items: center;
  }

  .set-card {
    margin-bottom: 20px;

    h2 {
      margin-bottom: 20px;
      color: var(--el-text-color-primary);
    }
  }

  .material-list {
    padding-right: 15px;

    .material-item {
      margin-bottom: 15px;
      transition: transform 0.3s;

      &:hover {
        transform: translateY(-3px);
        box-shadow: var(--el-box-shadow-light);
      }

      .material-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 12px;

        .title-wrapper {
          flex: 1;

          .title {
            margin: 0;
            font-size: 18px;
            color: var(--el-text-color-primary);
          }

          .meta {
            font-size: 12px;
            color: var(--el-text-color-secondary);
            margin-top: 4px;
            display: flex;
            align-items: center;

            .date {
              color: var(--el-text-color-secondary);
              white-space: nowrap;
            }
          }
        }

        .type-tag {
          margin-left: auto;
          white-space: nowrap;
        }
      }

      .description {
        color: var(--el-text-color-regular);
        line-height: 1.6;
        margin-bottom: 16px;
      }

      .preview-section {
        .pdf-preview {
          margin-bottom: 10px;
        }

        .image-preview {
          margin-bottom: 10px;
        }

        .video-preview {
          margin-bottom: 10px;

          video {
            width: 100%;
            max-height: 300px;
            border-radius: 4px;
          }
        }

        .actions {
          margin-top: 10px;
          display: flex;
          gap: 10px;
          flex-wrap: wrap;

          @media (max-width: 768px) {
            flex-direction: column;
          }
        }
      }
    }
  }
}

.el-upload__tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 7px;
}
</style>
