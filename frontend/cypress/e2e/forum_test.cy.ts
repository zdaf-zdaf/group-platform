/// <reference types="cypress" />

describe('论坛模块功能测试', () => {
  const teacher = { username: 'tchTest', password: 'Test1234@' }
  const student = { username: 'stuTest', password: 'Test1234@' }
  const postTitle = '自动化测试论坛帖'
  const postContent = '这是自动化测试发布的论坛内容，内容不少于10字。'
  const postComment = '自动化测试评论内容'
  const teacherComment = '教师自动化评论内容'

  // 学生端发帖、点赞、评论、删除
  it('学生端发帖、点赞、评论、删除', () => {
    cy.visit('http://localhost:5173/login')
    cy.get('input[placeholder="请输入用户名"]').type(student.username)
    cy.get('input[placeholder="请输入密码"]').type(student.password)
    cy.get('input[type="checkbox"]').check({ force: true })
    cy.get('button').contains('立即登录').click()
    cy.url().should('include', '/profile')

    cy.contains('答疑论坛').click({ force: true })
    cy.url().should('include', '/forum')
    cy.get('.forum').should('exist')

    // 发布帖子
    cy.get('.publish-card input[placeholder="请输入问题标题"]').clear().type(postTitle)
    cy.get('.publish-card textarea[placeholder="请输入问题内容"]').clear().type(postContent)
    cy.get('.publish-card button').contains('发布问题').click({ force: true })
    cy.contains('问题发布成功').should('be.visible')
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
    cy.contains('评论添加成功').should('be.visible')
    cy.get('.post-card').contains(postComment).should('exist')

    // 删除评论
    cy.get('.post-card').contains(postComment).parents('.comment').within(() => {
      cy.get('button').contains('删除评论').click({ force: true })
    })
    cy.contains('评论已删除').should('be.visible')

    // 删除帖子
    cy.get('.post-card').contains(postTitle).parents('.post-card').within(() => {
      cy.get('button').contains('删除').click({ force: true })
    })
    cy.contains('问题已删除').should('be.visible')
  })

  // 教师端置顶、点赞、评论、删除
  it('教师端置顶、点赞、评论、删除', () => {
    cy.visit('http://localhost:5173/login')
    cy.get('input[placeholder="请输入用户名"]').type(teacher.username)
    cy.get('input[placeholder="请输入密码"]').type(teacher.password)
    cy.get('input[type="checkbox"]').check({ force: true })
    cy.get('button').contains('立即登录').click()
    cy.url().should('include', '/profile')

    cy.contains('答疑论坛').click({ force: true })
    cy.url().should('include', '/forum')
    cy.get('.forum').should('exist')

    // 发布帖子
    cy.get('.publish-card input[placeholder="请输入问题标题"]').clear().type(postTitle)
    cy.get('.publish-card textarea[placeholder="请输入问题内容"]').clear().type(postContent)
    cy.get('.publish-card button').contains('发布问题').click({ force: true })
    cy.contains('问题发布成功').should('be.visible')
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
    cy.contains('评论添加成功').should('be.visible')
    cy.get('.post-card').contains(teacherComment).should('exist')

    // 删除评论
    cy.get('.post-card').contains(teacherComment).parents('.comment').within(() => {
      cy.get('button').contains('删除评论').click({ force: true })
    })
    cy.contains('评论已删除').should('be.visible')

    // 删除帖子
    cy.get('.post-card').first().within(() => {
      cy.get('button').contains('删除').click({ force: true })
    })
    cy.contains('问题已删除').should('be.visible')
  })
})
