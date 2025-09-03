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
      expect(token, 'token should exist').to.not.be.null
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

    cy.contains('学习资料').click({ force: true })
    cy.url().should('include', '/studyfile')
    cy.get('.material-page').should('exist')

    const types = [
      { label: 'PDF文档', file: 'cypress/fixtures/test.pdf' },
      { label: '文档资料', file: 'cypress/fixtures/test.docx' },
      { label: '图表素材', file: 'cypress/fixtures/test.png' },
      { label: '视频教程', file: 'cypress/fixtures/test.mp4' }
    ]

    types.forEach((item) => {
      const title = `自动化测试资料${item.label}`
      cy.contains('发布学习资料').click({ force: true })
      cy.get('.set-card').should('exist')
      cy.get('input[placeholder="请输入资料标题"]').clear().type(title)
      cy.get('textarea[placeholder="请输入资料描述"]').clear().type(`这是${item.label}类型的测试资料`)
      cy.get('.set-card .el-select').click({ force: true })
      cy.get('.el-select-dropdown__item').contains(item.label).click({ force: true })
      cy.get('.el-upload input[type="file"]').selectFile(item.file, { force: true })
      cy.intercept('POST', '/api/materials/material/').as('publishMaterialApi')
      cy.contains('发布资料').click({ force: true })
      cy.wait('@publishMaterialApi')
      cy.contains('资料发布成功').should('be.visible')
      cy.get('.material-list').should('contain.text', title)
    })
  })

  // ========================
  // 学生端查看并预览四种类型资料，下载第一个
  // ========================
  it('学生端查看并预览四种类型资料，下载第一个', () => {
    login(student)

    cy.contains('学习资料').click({ force: true })
    cy.url().should('include', '/studyfile')
    cy.get('.material-page').should('exist')

    // 依次预览四种类型
    const previewTypes = ['PDF文档', '文档资料', '图表素材', '视频教程']
    previewTypes.forEach(label => {
      cy.get('.material-list .material-item').contains(label).parents('.material-item').then($item => {
        cy.intercept('GET', '/api/materials/material/*').as('previewMaterialApi')
        cy.wrap($item).contains('在线预览').click({ force: true })
        cy.wait('@previewMaterialApi')
        cy.wait(1000) // 等待新窗口弹出
      })
    })
    // 下载第一个资料
    cy.get('.material-list .material-item').first().within(() => {
      cy.intercept('GET', '/api/materials/material/*/download/').as('downloadMaterialApi')
      cy.contains('下载文件').click({ force: true })
      cy.wait('@downloadMaterialApi')
    })
  })

  // ========================
  // 教师端删除资料
  // ========================
  it('教师端删除学习资料', () => {
    login(teacher)

    cy.contains('学习资料').click({ force: true })
    cy.url().should('include', '/studyfile')
    cy.get('.material-page').should('exist')

    // 删除自动化测试发布的四个资料
    const titles = [
      '自动化测试资料PDF文档',
      '自动化测试资料文档资料',
      '自动化测试资料图表素材',
      '自动化测试资料视频教程'
    ]
    titles.forEach(title => {
      cy.get('.material-list .material-item').contains(title).parents('.material-item').within(() => {
        cy.intercept('DELETE', '/api/materials/material/*/').as('deleteMaterialApi')
        cy.contains('删除').click({ force: true })
      })
      cy.get('.el-message-box').should('be.visible')
      cy.get('.el-message-box__btns button').contains('确定删除').click({ force: true })
      cy.wait('@deleteMaterialApi')
      cy.contains('删除成功').should('be.visible')
    })
  })
})
