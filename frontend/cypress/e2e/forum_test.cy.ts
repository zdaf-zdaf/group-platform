/// <reference types="cypress" />

describe('论坛模块功能测试', () => {
  const teacher = { username: 'tchTest', password: 'Test1234@' }
  const student = { username: 'stuTest', password: 'Test1234@' }
  const postTitle = '自动化测试论坛帖'
  const postContent = '这是自动化测试发布的论坛内容，内容不少于10字。'
  const postComment = '自动化测试评论内容'
  const teacherComment = '教师自动化评论内容'

  // 登录函数封装，token提升为全局变量
  let token = ''
  function login(user: { username: string; password: string }) {
    cy.request('POST', 'http://localhost:8000/api/auth/login/', {
      username: user.username,
      password: user.password
    }).then((response) => {
      expect(response.status).to.eq(200)
      token = response.body.access || response.body.token || response.body.data?.token
      expect(token, 'token should exist').to.not.be.null

      cy.visit('/profile', {
        onBeforeLoad(win) {
          win.localStorage.setItem('token', token)
          // 写入 userInfo，便于前端鉴权
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

  // 学生端发帖、点赞、评论、删除
  it('学生端发帖、点赞、评论、删除', () => {
    login(student)

    cy.contains('答疑论坛').click({ force: true })
    cy.url({ timeout: 15000 }).should('include', '/forum')
    cy.get('.forum').should('exist')

    // 发布帖子
    cy.intercept('POST', '/api/forum/questions/').as('postQuestion')
    cy.get('.publish-card input[placeholder="请输入问题标题"]').clear().type(postTitle)
    cy.get('.publish-card textarea[placeholder="请输入问题内容"]').clear().type(postContent)
    cy.get('.publish-card button').contains('发布问题').click({ force: true })
    cy.wait('@postQuestion').then(interception => {
      const status = interception.response?.statusCode
      const body = interception.response?.body
      cy.log('发帖响应:', JSON.stringify(body))
      cy.log('发帖状态:', status)
      if (status !== 201) {
        throw new Error('发帖接口返回非201: ' + status + ', body: ' + JSON.stringify(body))
      }
      // 新增：发帖后请求帖子列表并输出日志，便于CI调试
      cy.request({
        method: 'GET',
        url: 'http://localhost:8000/api/forum/questions/',
        headers: { Authorization: `Bearer ${token}` }
      }).then(res => {
        cy.log('帖子列表:', JSON.stringify(res.body))
      })
    })
    cy.reload()
    cy.wait(2000)
      cy.get('.post-card', { timeout: 20000 }).should('exist')
      cy.get('.post-card').should('contain.text', postTitle)

    // 点赞和取消点赞
    cy.get('.post-card').contains(postTitle).parents('.post-card').within(() => {
      cy.get('button').contains(/点赞|取消点赞/).click({ force: true })
      cy.wait(500)
      cy.get('button').contains(/点赞|取消点赞/).click({ force: true })
    })

    // 评论
    cy.get('.post-card').contains(postTitle).parents('.post-card').within(() => {
      cy.get('input[placeholder="写下你的评论..."]').type(postComment + '{enter}')
    })
  cy.get('.post-card').contains(postComment).should('exist')
    cy.get('.post-card').contains(postComment).should('exist')

    // 删除评论
    cy.get('.post-card').contains(postComment).parents('.comment').within(() => {
      cy.get('button').contains('删除评论').click({ force: true })
    })
  cy.get('.post-card').contains(postComment).should('not.exist')

    // 删除帖子
    cy.get('.post-card').contains(postTitle).parents('.post-card').within(() => {
      cy.get('button').contains('删除').click({ force: true })
    })
    cy.wait(1500)
    cy.reload()
    cy.contains('.post-card', postTitle).should('not.exist')
  })

  // 教师端置顶、点赞、评论、删除
  it('教师端置顶、点赞、评论、删除', () => {
    login(teacher)

    cy.contains('答疑论坛').click({ force: true })
    cy.url({ timeout: 15000 }).should('include', '/forum')
    cy.get('.forum').should('exist')

    // 发布帖子
    cy.intercept('POST', '/api/forum/questions/').as('postQuestion')
    cy.get('.publish-card input[placeholder="请输入问题标题"]').clear().type(postTitle)
    cy.get('.publish-card textarea[placeholder="请输入问题内容"]').clear().type(postContent)
    cy.get('.publish-card button').contains('发布问题').click({ force: true })
    cy.wait('@postQuestion').then(interception => {
      const status = interception.response?.statusCode
      const body = interception.response?.body
      cy.log('发帖响应:', JSON.stringify(body))
      cy.log('发帖状态:', status)
      if (status !== 201) {
        throw new Error('发帖接口返回非201: ' + status + ', body: ' + JSON.stringify(body))
      }
      // 新增：发帖后请求帖子列表并输出日志，便于CI调试
      cy.request({
        method: 'GET',
        url: 'http://localhost:8000/api/forum/questions/',
        headers: { Authorization: `Bearer ${token}` }
      }).then(res => {
        cy.log('帖子列表:', JSON.stringify(res.body))
      })
    })
    cy.reload()
    cy.wait(2000)
      cy.get('.post-card', { timeout: 20000 }).should('exist')
      cy.get('.post-card').should('contain.text', postTitle)

    // 置顶和取消置顶
    cy.get('.post-card').first().within(() => {
      cy.get('button').contains(/置顶|取消置顶/).click({ force: true })
      cy.wait(500)
      cy.get('button').contains(/置顶|取消置顶/).click({ force: true })
    })

    // 点赞和取消点赞
    cy.get('.post-card').first().within(() => {
      cy.get('button').contains(/点赞|取消点赞/).click({ force: true })
      cy.wait(500)
      cy.get('button').contains(/点赞|取消点赞/).click({ force: true })
    })

    // 评论
    cy.get('.post-card').first().within(() => {
      cy.get('input[placeholder="写下你的评论..."]').type(teacherComment + '{enter}')
    })
  cy.get('.post-card').contains(teacherComment).should('exist')
    cy.get('.post-card').contains(teacherComment).should('exist')

    // 删除评论
    cy.get('.post-card').contains(teacherComment).parents('.comment').within(() => {
      cy.get('button').contains('删除评论').click({ force: true })
    })
  cy.get('.post-card').contains(teacherComment).should('not.exist')

    // 删除帖子
    cy.get('.post-card').first().within(() => {
      cy.get('button').contains('删除').click({ force: true })
    })
    cy.wait(1500)
    cy.reload()
    cy.contains('.post-card', postTitle).should('not.exist')
  })
})
