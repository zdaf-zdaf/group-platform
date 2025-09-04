/// <reference types="cypress" />

// ========================
// 全局变量提升，保证所有用例一致
// ========================
const API_BASE_URL = 'http://127.0.0.1:8000'
let token = ''
const studentUsername = `stu${Date.now() % 10000}`
const teacherUsername = `tch${Date.now() % 10000}`
let teacherPwd = 'Test1234@'
const experimentTitle = 'Cypress全流程实验'
const experimentDescription = '自动化测试实验描述'
const startTime = '2025-08-27 15:00:00'
const deadlineTime = '2025-08-28 23:59:59'
const codeSample =
`
a, b = map(int, input().split())
print(a + b)
`
const password = 'Test1234@'

describe('灵狐智验前端完整流程集成测试', () => {
  // 通用登录函数，直接请求后端并注入 token 和 userInfo
  function login(user) {
    cy.request('POST', `${API_BASE_URL}/api/auth/login/`, {
      username: user.username,
      password: user.password
    }).then((response) => {
      expect(response.status).to.eq(200)
      token = response.body.access || response.body.token || response.body.data?.token
      expect(token, 'token should exist').to.not.equal(null)
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
  // 学生注册
  // ========================
  it('学生注册流程', () => {
    cy.visit('/register')
    cy.get('form', { timeout: 10000 }).should('exist')
    cy.get('input[placeholder="请输入3-16位用户名"]').type(studentUsername)
    cy.get('input[placeholder="请输入邮箱地址"]').type(`${studentUsername}@example.com`)
    cy.get('input[placeholder="请输入6-18位密码"]').type(password)
    cy.get('input[placeholder="请再次输入密码"]').type(password)
    cy.get('.el-select').click()
    cy.get('.el-select-dropdown__item').contains('学生').click({ force: true })
    cy.get('input[type="checkbox"]').check({ force: true })
    cy.intercept('POST', '/api/auth/register/').as('registerApi')
    cy.get('button').contains('注册账号').click()
    cy.wait('@registerApi', { timeout: 10000 }).then((res) => {
      cy.log('注册接口响应:', JSON.stringify(res && res.response))
      expect(res && res.response && res.response.statusCode).to.be.oneOf([200, 201])
    })
    // 注册成功后直接点击“立即登录”跳转
    cy.get('.auth-footer .auth-link').click({ force: true })
    cy.url({ timeout: 8000 }).should('include', '/login')
  })

  // ========================
  // 教师注册+登录+修改个人信息和密码
  // ========================
  it('教师注册后登录并修改个人信息和密码', () => {
    // 注册
    cy.visit('/register')
    cy.get('input[placeholder="请输入3-16位用户名"]').type(teacherUsername)
    cy.get('input[placeholder="请输入邮箱地址"]').type(`${teacherUsername}@example.com`)
    cy.get('input[placeholder="请输入6-18位密码"]').type(password)
    cy.get('input[placeholder="请再次输入密码"]').type(password)
    cy.get('.el-select').click()
    cy.get('.el-select-dropdown__item').contains('教师').click({ force: true })
    cy.get('input[type="checkbox"]').check({ force: true })
    cy.intercept('POST', '/api/auth/register/').as('registerApi')
    cy.get('button').contains('注册账号').click()
    cy.wait('@registerApi', { timeout: 10000 }).then((res) => {
      cy.log('注册接口响应:', JSON.stringify(res && res.response))
      expect(res && res.response && res.response.statusCode).to.be.oneOf([200, 201])
    })
    // 注册成功后直接点击“立即登录”跳转
    cy.get('.auth-footer .auth-link').click({ force: true })
    cy.url({ timeout: 8000 }).should('include', '/login')

    // 登录（统一用 cy.request 注入 token）
    login({ username: teacherUsername, password: teacherPwd })
    cy.url({ timeout: 8000 }).should('include', '/profile')

    // 进入个人信息页
    cy.contains('个人信息').click({ force: true })
    cy.url().should('include', '/profile')
    cy.get('.personal-info').should('exist')

    // 点击编辑信息
    cy.contains('编辑信息').click({ force: true })

    // 生成学工号 2337+用户名
    const teacherId = `2337${teacherUsername}`
    cy.get('input[placeholder="请输入学工号"]').clear().type(teacherId, { force: true })
    cy.get('input[placeholder="请输入学院名称"]').clear().type('软件学院', { force: true })

    // 保存信息
    cy.contains('保存信息').click({ force: true })
    cy.contains('个人信息已保存').should('be.visible')
    cy.get('input[placeholder="请输入学工号"]').should('have.value', teacherId)
    cy.get('input[placeholder="请输入学院名称"]').should('have.value', '软件学院')

    // 修改密码
    cy.contains('修改密码').click({ force: true })
    cy.get('input[placeholder="请输入当前密码"]').type(password, { force: true })
    cy.get('input[placeholder="8-20位字母数字组合"]').type('TTest1234', { force: true })
    cy.get('input[placeholder="请再次输入新密码"]').type('TTest1234', { force: true })
    cy.contains('确认修改').click({ force: true })
    cy.contains('密码修改成功').should('be.visible')
    // 密码修改后同步更新全局变量
    teacherPwd = 'TTest1234'

  // 退出登录并用新密码登录验证
  cy.contains('退出登录').click({ force: true })
  // 弹窗点击“确定”按钮
  cy.get('.el-message-box').should('be.visible')
  cy.get('.el-message-box__btns button').contains('确定').click({ force: true })
  cy.contains('已安全退出').should('be.visible')
  })

  // ========================
  // 教师登录并创建实验
  // ========================
  it('教师登录并创建实验（接口）', () => {
    // 登录获取 token
    cy.request('POST', `${API_BASE_URL}/api/auth/login/`, {
      username: teacherUsername,
      password: teacherPwd
    }).then((response) => {
      expect(response.status).to.eq(200)
      const teacherToken = response.body.access || response.body.token || response.body.data?.token
      expect(teacherToken).to.not.equal(null)
      // 创建实验
      cy.request({
        method: 'POST',
        url: `${API_BASE_URL}/api/experiments/experiments/`,
        headers: { Authorization: `Bearer ${teacherToken}` },
        body: {
          title: experimentTitle,
          description: experimentDescription,
          start_time: '2025-08-27 15:00:00',
          deadline: '2025-08-28 23:59:59',
          students: [],
          questions: [
            {
              type: 'choice',
              description: '选择题示例题干',
              score: 10,
              options: ['选项A', '选项B', '选项C'],
              answer: 0
            },
            {
              type: 'fill',
              description: '填空题示例题干',
              score: 5,
              answer: '标准答案'
            },
            {
              type: 'coding',
              description: '编程题示例题干',
              score: 20,
              time_limit: 2,
              memory_limit: 256,
              testcases: [
                { input: '1 2', output: '3' }
              ]
            }
          ]
        }
      }).then((resp) => {
        expect([200, 201]).to.include(resp.status)
        const experimentId = resp.body.id || resp.body.data?.id
        expect(experimentId).to.not.equal(undefined)
        // 校验实验已创建
        cy.request({
          method: 'GET',
          url: `${API_BASE_URL}/api/experiments/experiments/`,
          headers: { Authorization: `Bearer ${teacherToken}` }
        }).then((resp2) => {
          expect([200, 201]).to.include(resp2.status)
          const found = Array.isArray(resp2.body) ? resp2.body : (resp2.body?.data || [])
          expect(found.some(e => e.title === experimentTitle)).to.equal(true)
        })
      })
    })
  })

  // ========================
  // 学生登录完成实验
  // ========================
  it('学生登录完成实验（接口）', () => {
    // 登录获取 token
    cy.request('POST', `${API_BASE_URL}/api/auth/login/`, {
      username: studentUsername,
      password: password
    }).then((response) => {
      expect(response.status).to.eq(200)
      const studentToken = response.body.access || response.body.token || response.body.data?.token
      expect(studentToken).to.not.equal(null)
      // 查询实验ID
      cy.request({
        method: 'GET',
        url: `${API_BASE_URL}/api/experiments/experiments/`,
        headers: { Authorization: `Bearer ${studentToken}` }
      }).then((resp) => {
        expect([200, 201]).to.include(resp.status)
        const found = Array.isArray(resp.body) ? resp.body : (resp.body?.data || [])
        const exp = found.find(e => e.title === experimentTitle)
        expect(exp).to.not.equal(undefined)
        const experimentId = exp.id
        // 完成实验提交
        cy.request({
          method: 'POST',
          url: `${API_BASE_URL}/api/experiments/submit/`,
          headers: { Authorization: `Bearer ${studentToken}` },
          body: {
            experiment: experimentId,
            answers: [
              { type: 'choice', answer: 0 },
              { type: 'fill', answer: '答案' },
              { type: 'coding', code: 'a, b = map(int, input().split())\nprint(a + b)\n' }
            ]
          }
        }).then((resp2) => {
          expect([200, 201]).to.include(resp2.status)
        })
      })
    })
  })
  // ========================
  // 教师查看学生提交记录与详情
  // ========================
  it('教师查看学生提交记录与详情并删除实验（接口）', () => {
    // 登录获取 token
    cy.request('POST', `${API_BASE_URL}/api/auth/login/`, {
      username: teacherUsername,
      password: teacherPwd
    }).then((response) => {
      expect(response.status).to.eq(200)
      const teacherToken = response.body.access || response.body.token || response.body.data?.token
      expect(teacherToken).to.not.equal(null)
      // 查询提交记录
      cy.request({
        method: 'GET',
        url: `${API_BASE_URL}/api/experiments/submissions/`,
        headers: { Authorization: `Bearer ${teacherToken}` }
      }).then((resp) => {
        expect([200, 201]).to.include(resp.status)
        const found = Array.isArray(resp.body) ? resp.body : (resp.body?.data || [])
        expect(found.length).to.be.greaterThan(0)
        // 检查内容字段
        expect(found[0]).to.have.property('student')
        expect(found[0]).to.have.property('experiment')
        expect(found[0]).to.have.property('submit_time')
        // 查询实验ID
        cy.request({
          method: 'GET',
          url: `${API_BASE_URL}/api/experiments/experiments/`,
          headers: { Authorization: `Bearer ${teacherToken}` }
        }).then((resp2) => {
          expect([200, 201]).to.include(resp2.status)
          const foundExp = Array.isArray(resp2.body) ? resp2.body : (resp2.body?.data || [])
          const exp = foundExp.find(e => e.title === experimentTitle)
          expect(exp).to.not.equal(undefined)
          const experimentId = exp.id
          // 删除实验
          cy.request({
            method: 'DELETE',
            url: `${API_BASE_URL}/api/experiments/experiments/${experimentId}/`,
            headers: { Authorization: `Bearer ${teacherToken}` }
          }).then((resp3) => {
            expect([200, 204, 202]).to.include(resp3.status)
          })
        })
      })
    })
  })
})
