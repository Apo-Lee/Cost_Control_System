import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/LoginView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('../components/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/dashboard/DashboardView.vue'),
      },
      {
        path: 'expenses',
        name: 'Expenses',
        component: () => import('../views/expense/ExpenseList.vue'),
      },
      {
        path: 'budgets',
        name: 'Budgets',
        component: () => import('../views/budget/BudgetList.vue'),
      },
      {
        path: 'approvals',
        name: 'Approvals',
        component: () => import('../views/approval/ApprovalList.vue'),
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('../views/report/ReportView.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫：未登录自动跳转登录页
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth !== false && !authStore.token) {
    next({ name: 'Login' })
  } else if (to.name === 'Login' && authStore.token) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
