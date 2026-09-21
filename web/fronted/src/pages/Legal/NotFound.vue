<template>
  <div class="notfound-page">
    <div class="card">
      <div class="code">404</div>
      <h1>页面不存在</h1>
      <p>你访问的地址没有对应的页面，可能是链接输入有误或页面已移除。</p>
      <router-link class="home-link" to="/">返回首页</router-link>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'NotFound'
})
</script>

<style scoped>
.notfound-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: var(--space-6);
}

.card {
  width: 100%;
  max-width: 420px;
  padding: var(--space-8) var(--space-6);
  text-align: center;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
}

.code {
  font-size: 56px;
  font-weight: var(--font-bold);
  line-height: 1;
  color: var(--primary);
  margin-bottom: var(--space-4);
}

.card h1 {
  font-size: var(--font-xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.card p {
  font-size: var(--font-sm);
  line-height: 1.7;
  color: var(--text-tertiary);
  margin-bottom: var(--space-6);
}

.home-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 10px 24px;
  background: var(--primary);
  color: #fff;
  border-radius: var(--radius-md);
  font-size: var(--font-sm);
  font-weight: var(--font-semibold);
  transition: background var(--transition);
}

.home-link:hover {
  background: var(--primary-dark);
  color: #fff;
}
</style>
