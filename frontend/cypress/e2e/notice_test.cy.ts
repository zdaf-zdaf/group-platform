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

  const API_BASE_URL = 'http://127.0.0.1:8000'
  // 登录函数封装，token提升为全局变量
  let token = ''
  function login(user: { username: string; password: string }) {
    cy.intercept('POST', '/api/auth/login/').as('loginApi')
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

  // 教师端先发布两个公告，编辑第一个，然后筛选搜索
  it('教师端发布、编辑、筛选、搜索公告', () => {
    login(teacher)

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
  // 临时拦截所有 POST 请求，便于定位实际 API 路径
  cy.intercept('POST', '**').as('anyPostApi')
    cy.get('.set-card').within(() => {
      cy.get('button').contains('发布公告').click({ force: true })
    })
    cy.wait('@anyPostApi')
    cy.wait(2000)
    cy.contains('公告发布成功').should('be.visible')
    cy.get('.notice-list').should('contain.text', noticeTitle1)

    // 发布第二个公告
    cy.contains('发布公告').click({ force: true })
    cy.get('.set-card').should('exist')
    cy.get('input[placeholder="请输入公告标题"]').clear().type(noticeTitle2)
    cy.get('textarea[placeholder="请输入公告内容"]').clear().type(noticeContent2)
    cy.get('.set-card .el-select').click({ force: true })
    cy.get('.el-select-dropdown__item').contains('安全公告').click({ force: true })
  cy.intercept('POST', '**').as('anyPostApi')
    cy.get('.set-card').within(() => {
      cy.get('button').contains('发布公告').click({ force: true })
    })
    cy.wait('@anyPostApi')
    cy.wait(2000)
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
    cy.intercept('PUT', /\/api\/notices\/\d+\//).as('editNoticeApi')
    cy.get('.set-card').within(() => {
      cy.get('button').contains('更新公告').click({ force: true })
    })
    cy.wait('@editNoticeApi')
  cy.contains('公告更新成功').should('be.visible')
  cy.wait(2000)
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
    login(student)

    cy.contains('公告').click({ force: true })
    cy.url().should('include', '/notices')
    cy.get('.notice-page').should('exist')

    // 检查未读数显示，兼容无未读公告的情况，自动等待未读数变化
    cy.intercept('GET', '/api/notices/unread_count/').as('getUnreadCountApi')
    cy.get('.unread-info .unread-count').invoke('text').then(countText => {
      const unreadBefore = parseInt(countText)
      if (unreadBefore > 0) {
        // 拦截“标记已读”接口
        cy.get('.notice-list .notice-item.unread').first().within(() => {
          cy.intercept('POST', /\/api\/notices\/\d+\/mark_as_read\//).as('markAsReadApi')
          cy.get('.notice-header .title').click({ force: true })
        })
        cy.wait('@markAsReadApi').then(({ response }) => {
          cy.log('标记已读接口状态:', response?.statusCode)
          cy.log('标记已读接口body:', JSON.stringify(response?.body))
          expect(response?.statusCode, '标记已读接口状态码').to.be.oneOf([200, 201])
        })
        // 自动等待未读数变小，并断言“获取未读数量”接口
        cy.wait('@getUnreadCountApi').then(({ response }) => {
          cy.log('获取未读数量接口状态:', response?.statusCode)
          cy.log('获取未读数量接口body:', JSON.stringify(response?.body))
          expect(response?.statusCode, '获取未读数量接口状态码').to.be.oneOf([200, 201])
        })
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
    login(teacher)

    cy.contains('通知公告').click({ force: true })
    cy.url().should('include', '/notices')
    cy.get('.notice-page').should('exist')

    // 删除已编辑的公告
    cy.wait(2000)
    cy.get('.notice-list .notice-item').contains(noticeEditTitle).parents('.notice-item').within(() => {
      cy.intercept('DELETE', /\/api\/notices\/\d+\//).as('deleteNoticeApi')
      cy.contains('删除').click({ force: true })
    })
    cy.wait('@deleteNoticeApi')
    cy.contains('公告删除成功').should('be.visible')
    cy.wait(2000)
    cy.get('.notice-list').should('not.contain.text', noticeEditTitle)

    // 删除第二个公告
    cy.wait(2000)
    cy.get('.notice-list .notice-item').contains(noticeTitle2).parents('.notice-item').within(() => {
      cy.intercept('DELETE', /\/api\/notices\/\d+\//).as('deleteNoticeApi')
      cy.contains('删除').click({ force: true })
    })
    cy.wait('@deleteNoticeApi')
    cy.contains('公告删除成功').should('be.visible')
    cy.wait(2000)
    cy.get('.notice-list').should('not.contain.text', noticeTitle2)

  })
})
