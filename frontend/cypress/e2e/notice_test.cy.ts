/// <reference types="cypress" />

describe('公告模块功能测试', () => {
  const teacher = { username: 'tchTest', password: 'Test1234@' }
  const student = { username: 'stuTest', password: 'Test1234@' }
  const noticeTitle1 = '自动化测试公告1'
  const noticeContent1 = '这是自动化测试发布的公告内容1'
  const noticeTitle2 = '自动化测试公告2'
  const noticeContent2 = '这是自动化测试发布的公告内容2'
  const noticeEditTitle = '自动化测试公告1-已编辑'
  const noticeEditContent = '这是编辑后的公告内容1'

  // 教师端先发布两个公告，编辑第一个，然后筛选搜索
  it('教师端发布、编辑、筛选、搜索公告', () => {
    cy.visit('http://localhost:5173/login')
    cy.get('input[placeholder="请输入用户名"]').type(teacher.username)
    cy.get('input[placeholder="请输入密码"]').type(teacher.password)
    cy.get('input[type="checkbox"]').check({ force: true })
    cy.get('button').contains('立即登录').click()
    cy.url().should('include', '/profile')

    cy.contains('通知公告').click({ force: true })
    cy.url().should('include', '/notices')
    cy.get('.notice-page').should('exist')

    // 发布第一个公告
    cy.contains('发布公告').click({ force: true })
    cy.get('.set-card').should('exist')
    cy.get('input[placeholder="请输入公告标题"]').clear().type(noticeTitle1)
    cy.get('textarea[placeholder="请输入公告内容"]').clear().type(noticeContent1)
    cy.get('.set-card .el-select').click({ force: true })
    cy.get('.el-select-dropdown__item').contains('课程通知').click({ force: true })
    cy.get('.set-card').within(() => {
      cy.get('button').contains('发布公告').click({ force: true })
    })
    cy.contains('公告发布成功').should('be.visible')
    cy.get('.notice-list').should('contain.text', noticeTitle1)

    // 发布第二个公告
    cy.contains('发布公告').click({ force: true })
    cy.get('.set-card').should('exist')
    cy.get('input[placeholder="请输入公告标题"]').clear().type(noticeTitle2)
    cy.get('textarea[placeholder="请输入公告内容"]').clear().type(noticeContent2)
    cy.get('.set-card .el-select').click({ force: true })
    cy.get('.el-select-dropdown__item').contains('安全公告').click({ force: true })
    cy.get('.set-card').within(() => {
      cy.get('button').contains('发布公告').click({ force: true })
    })
    cy.contains('公告发布成功').should('be.visible')
    cy.get('.notice-list').should('contain.text', noticeTitle2)

    // 编辑第一个公告
    cy.get('.notice-list .notice-item').contains(noticeTitle1).parents('.notice-item').within(() => {
      cy.contains('编辑').click({ force: true })
    })
    cy.get('.set-card').should('exist')
    cy.get('input[placeholder="请输入公告标题"]').clear().type(noticeEditTitle)
    cy.get('textarea[placeholder="请输入公告内容"]').clear().type(noticeEditContent)
    cy.get('.set-card .el-select').click({ force: true })
    cy.get('.el-select-dropdown__item').contains('设备维护').click({ force: true })
    cy.get('.set-card').within(() => {
      cy.get('button').contains('更新公告').click({ force: true })
    })
    cy.contains('公告更新成功').should('be.visible')
    cy.get('.notice-list').should('contain.text', noticeEditTitle)


    // 筛选类型
    cy.get('.filter-bar .el-select').click({ force: true })
    cy.get('.el-select-dropdown__item').contains('设备维护').click({ force: true })
    cy.get('.notice-list').should('contain.text', noticeEditTitle)

    // 清空筛选类型（重置下拉框）
    cy.get('.filter-bar .el-select').trigger('mouseenter') // 先让清空按钮出现
    cy.get('.filter-bar .el-select .el-select__clear').click({ force: true }) // 点击清空按钮

    // 校验 placeholder 恢复为“全部类型”，说明筛选已清空
    cy.get('.filter-bar .el-select .el-select__placeholder')
      .should('contain.text', '全部类型')

    // 列表应恢复到未筛选状态
    cy.get('.notice-list').should('contain.text', noticeEditTitle)
    // 搜索
    cy.get('input[placeholder="搜索公告..."]').clear().type('已编辑')
    cy.get('.notice-list').should('contain.text', noticeEditTitle)
    cy.get('input[placeholder="搜索公告..."]').clear()
  })

  // 学生端查看公告、标记已读、未读数刷新、筛选和搜索
  it('学生端查看公告、标记已读、未读数刷新、筛选和搜索', () => {
    cy.visit('http://localhost:5173/login')
    cy.get('input[placeholder="请输入用户名"]').type(student.username)
    cy.get('input[placeholder="请输入密码"]').type(student.password)
    cy.get('input[type="checkbox"]').check({ force: true })
    cy.get('button').contains('立即登录').click()
    cy.url().should('include', '/profile')

    cy.contains('公告').click({ force: true })
    cy.url().should('include', '/notices')
    cy.get('.notice-page').should('exist')

    // 检查未读数显示，兼容无未读公告的情况，自动等待未读数变化
    cy.get('.unread-info .unread-count').invoke('text').then(countText => {
      const unreadBefore = parseInt(countText)
      if (unreadBefore > 0) {
        cy.get('.notice-list .notice-item.unread').first().within(() => {
          cy.get('.notice-header .title').click({ force: true })
        })
        // 自动等待未读数变小
        cy.get('.unread-info .unread-count').should($span => {
          const countAfter = parseInt($span.text())
          expect(countAfter).to.be.lessThan(unreadBefore)
        })
      } else {
        cy.log('无未读公告，跳过已读数减少断言')
      }
    })

    // 筛选类型
    cy.get('.filter-bar .el-select').click({ force: true })
    cy.get('.el-select-dropdown__item').contains('设备维护').click({ force: true })
    cy.get('.notice-list').should('exist')

    // 搜索
    cy.get('input[placeholder="搜索公告..."]').clear().type('公告')
    cy.get('.notice-list').should('exist')
    cy.get('input[placeholder="搜索公告..."]').clear()
  })

  // 教师端删除发布的两个公告
  it('教师端删除发布的两个公告', () => {
    cy.visit('http://localhost:5173/login')
    cy.get('input[placeholder="请输入用户名"]').type(teacher.username)
    cy.get('input[placeholder="请输入密码"]').type(teacher.password)
    cy.get('input[type="checkbox"]').check({ force: true })
    cy.get('button').contains('立即登录').click()
    cy.url().should('include', '/profile')

    cy.contains('通知公告').click({ force: true })
    cy.url().should('include', '/notices')
    cy.get('.notice-page').should('exist')

    // 删除已编辑的公告
    cy.get('.notice-list .notice-item').contains(noticeEditTitle).parents('.notice-item').within(() => {
      cy.contains('删除').click({ force: true })
    })
    cy.contains('公告删除成功').should('be.visible')
    cy.get('.notice-list').should('not.contain.text', noticeEditTitle)

    // 删除第二个公告
    cy.get('.notice-list .notice-item').contains(noticeTitle2).parents('.notice-item').within(() => {
      cy.contains('删除').click({ force: true })
    })
    cy.contains('公告删除成功').should('be.visible')
    cy.get('.notice-list').should('not.contain.text', noticeTitle2)

  })
})
