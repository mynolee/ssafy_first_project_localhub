<script setup>
import { computed, reactive, ref, watch } from 'vue'

import { resolveImageUrl } from '../api/client'
import { POST_CATEGORIES, REGIONS } from '../constants/categories'

const props = defineProps({
  initialPost: { type: Object, default: null },
  editing: Boolean,
  busy: Boolean,
  error: { type: String, default: '' },
})
const emit = defineEmits(['submit', 'cancel'])
const form = reactive({
  region: 'SEOUL',
  category: 'TOURIST',
  title: '',
  content: '',
  author: '익명',
  password: '',
})
const imageFile = ref(null)

const imagePreviewUrl = computed(() => {
  if (imageFile.value) return URL.createObjectURL(imageFile.value)
  return resolveImageUrl(props.initialPost?.imageUrl)
})

watch(
  () => props.initialPost,
  (post) => {
    if (!post) return
    form.region = post.region
    form.category = post.category
    form.title = post.title
    form.content = post.content
    form.author = post.author
  },
  { immediate: true },
)

function onImageChange(event) {
  imageFile.value = event.target.files[0] || null
}

function submit() {
  emit('submit', { ...form, author: form.author.trim() || '익명' }, imageFile.value)
}
</script>

<template>
  <form class="post-form card" @submit.prevent="submit">
    <div class="form-row">
      <div class="field">
        <label for="region">지역</label>
        <select id="region" v-model="form.region" required>
          <option v-for="item in REGIONS.slice(1)" :key="item.value" :value="item.value">
            {{ item.label }}
          </option>
        </select>
      </div>
      <div class="field field-category">
        <label for="category">카테고리</label>
        <select id="category" v-model="form.category" required>
          <option v-for="item in POST_CATEGORIES.slice(1)" :key="item.value" :value="item.value">
            {{ item.label }}
          </option>
        </select>
      </div>
    </div>
    <div class="field">
      <label for="author">작성자</label>
      <input id="author" v-model="form.author" maxlength="20" placeholder="익명" />
    </div>
    <div class="field">
      <label for="title">제목</label>
      <input id="title" v-model.trim="form.title" maxlength="100" placeholder="이웃에게 전할 이야기를 적어주세요" required />
      <span class="character-count">{{ form.title.length }} / 100</span>
    </div>
    <div class="field">
      <label for="content">내용</label>
      <textarea id="content" v-model.trim="form.content" maxlength="5000" rows="12" placeholder="직접 경험한 우리 지역의 장소와 팁을 나눠주세요." required></textarea>
      <span class="character-count">{{ form.content.length }} / 5000</span>
    </div>
    <div class="field">
      <label for="image">사진 첨부</label>
      <input id="image" type="file" accept="image/jpeg,image/png,image/webp,image/gif" @change="onImageChange" />
      <img v-if="imagePreviewUrl" :src="imagePreviewUrl" alt="첨부 이미지 미리보기" class="image-preview" />
      <small>JPEG, PNG, WEBP, GIF / 5MB 이하. 새 이미지를 선택하면 기존 이미지를 대체합니다.</small>
    </div>
    <div class="field password-field">
      <label for="password">수정용 비밀번호</label>
      <input id="password" v-model="form.password" type="password" minlength="4" maxlength="20" autocomplete="new-password" required />
      <small>{{ editing ? '글 작성 시 설정한 비밀번호를 입력하세요.' : '수정·삭제할 때 필요합니다. 별도로 안전하게 기억해 주세요.' }}</small>
    </div>
    <p v-if="error" class="form-error">{{ error }}</p>
    <div class="form-actions">
      <button class="button button-secondary" type="button" @click="emit('cancel')">취소</button>
      <button class="button" type="submit" :disabled="busy">
        {{ busy ? '저장 중...' : editing ? '수정 완료' : '글 등록' }}
      </button>
    </div>
  </form>
</template>
