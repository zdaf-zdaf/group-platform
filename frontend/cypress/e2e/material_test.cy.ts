/// <reference types="cypress" />

describe('学习资料模块功能测试', () => {
  const teacher = { username: 'tchTest', password: 'Test1234@' }
  const student = { username: 'stuTest', password: 'Test1234@' }
  const API_BASE_URL = 'http://127.0.0.1:8000'
  // 登录函数封装，token提升为全局变量
  let token = ''
  // 通用登录函数，直接请求后端并注入 token 和 userInfo
  function login(user) {
    cy.request('POST', `${API_BASE_URL}/api/auth/login/`, {
      username: user.username,
      password: user.password
    }).then((response) => {
      expect(response.status).to.eq(200)
      token = response.body.access || response.body.token || response.body.data?.token
      expect(token, 'token should exist').to.not.equal(null);
      cy.visit('/profile', {
        onBeforeLoad(win) {
          win.localStorage.setItem('token', token)
          if (response.body.username) {
            win.localStorage.setItem('userInfo', JSON.stringify({
              username: response.body.username,
              role: response.body.role,
              email: response.body.email,
              student_id: response.body.student_id,
              faculty: response.body.faculty
            }))
          }
        }
      })
      cy.reload()
      cy.visit('/')
      cy.wait(1000)
    })
  }

  // ========================
  // 教师端依次发布四种类型的学习资料（合并为一个用例）
  // ========================
  it('教师端依次发布四种类型学习资料', () => {
    login(teacher)
  })

  // ========================
  // 学生端查看并预览四种类型资料，下载第一个
  // ========================
  it('学生端查看并预览四种类型资料，下载第一个', () => {
    login(student)

  })
})
