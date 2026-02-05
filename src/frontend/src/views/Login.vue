<template>
  <div class="login-container">
    <div class="login-box">
      <h2 class="title">🏭 Mini-MES 系统</h2>
      <p class="subtitle">工业现场数据采集与追溯平台</p>
      
      <el-form :model="form" class="login-form">
        <el-form-item>
          <el-input 
            v-model="form.username" 
            placeholder="管理员账号" 
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        
        <el-form-item>
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="密码" 
            prefix-icon="Lock"
            show-password
            size="large"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-button 
          type="primary" 
          class="login-btn" 
          :loading="loading" 
          @click="handleLogin"
          size="large"
        >
          立即登录
        </el-button>
      </el-form>
      
      <div class="footer">
        © 2026 Mini-MES Project | v0.5
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)

const form = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入账号和密码')
    return
  }

  loading.value = true

  try {
    // 1. 发起请求
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })
    
    const data = await response.json()

    if (response.ok) {
      // 2. 登录成功：存 Token
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('username', form.value.username)
      
      ElMessage.success('登录成功，欢迎回来！')
      
      // 3. 跳转到首页
      router.push('/')
    } else {
      ElMessage.error(data.detail || '登录失败')
    }
  } catch (error) {
    ElMessage.error('网络连接错误，请检查后端服务')
    console.error(error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #2c3e50; /* 深色工业风背景 */
  background-image: radial-gradient(#34495e 1px, transparent 1px);
  background-size: 20px 20px;
}

.login-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  text-align: center;
}

.title {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.subtitle {
  margin-top: 10px;
  margin-bottom: 30px;
  color: #666;
  font-size: 14px;
}

.login-btn {
  width: 100%;
  margin-top: 10px;
  font-weight: bold;
}

.footer {
  margin-top: 30px;
  color: #999;
  font-size: 12px;
}
</style>