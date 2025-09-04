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
      expect(token, 'token should exist').to.not.equal(null)

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

  // 教师端接口方式发布、编辑、筛选、搜索公告
  it('教师端接口发布、编辑、筛选、搜索公告', () => {
    login(teacher)

    // 发布第一个公告
    cy.request({
      method: 'POST',
      url: `${API_BASE_URL}/api/notices/`,
      headers: { Authorization: `Bearer ${token}` },
      body: {
        title: noticeTitle1,
        content: noticeContent1,
        type: 'course', // 假设后端 type 字段为英文
      },
      failOnStatusCode: false
    }).then(res => {
      expect([200, 201]).to.include(res.status)
    })
    // 轮询接口直到新公告出现
    function pollNoticeList1(retry = 20) {
      if (retry <= 0) throw new Error('公告列表接口始终无新公告1');
      cy.request({
        method: 'GET',
        url: `${API_BASE_URL}/api/notices/`,
        headers: { Authorization: `Bearer ${token}` },
        failOnStatusCode: false
      }).then(res => {
        const noticesArr = Array.isArray(res.body) ? res.body : (res.body.data || [])
        if (noticesArr.some(n => n.title === noticeTitle1)) {
          cy.log('后端已包含新公告1')
        } else {
          cy.wait(1000).then(() => pollNoticeList1(retry - 1))
        }
      })
    }
    pollNoticeList1()

    // 发布第二个公告
    cy.request({
      method: 'POST',
      url: `${API_BASE_URL}/api/notices/`,
      headers: { Authorization: `Bearer ${token}` },
      body: {
        title: noticeTitle2,
        content: noticeContent2,
        type: 'security', // 假设后端 type 字段为英文
      },
      failOnStatusCode: false
    }).then(res => {
      expect([200, 201]).to.include(res.status)
    })
    function pollNoticeList2(retry = 20) {
      if (retry <= 0) throw new Error('公告列表接口始终无新公告2');
      cy.request({
        method: 'GET',
        url: `${API_BASE_URL}/api/notices/`,
        headers: { Authorization: `Bearer ${token}` },
        failOnStatusCode: false
      }).then(res => {
        const noticesArr = Array.isArray(res.body) ? res.body : (res.body.data || [])
        if (noticesArr.some(n => n.title === noticeTitle2)) {
          cy.log('后端已包含新公告2')
        } else {
          cy.wait(1000).then(() => pollNoticeList2(retry - 1))
        }
      })
    }
    pollNoticeList2()

    // 编辑第一个公告
    cy.request({
      method: 'GET',
      url: `${API_BASE_URL}/api/notices/`,
      headers: { Authorization: `Bearer ${token}` },
      failOnStatusCode: false
    }).then(res => {
      const noticesArr = Array.isArray(res.body) ? res.body : (res.body.data || [])
      const notice1 = noticesArr.find(n => n.title === noticeTitle1)
      expect(notice1, '后端应有第一个公告').to.not.equal(undefined)
      cy.request({
        method: 'PUT',
        url: `${API_BASE_URL}/api/notices/${notice1.id}/`,
        headers: { Authorization: `Bearer ${token}` },
        body: {
          title: noticeEditTitle,
          content: noticeEditContent,
          type: 'maintenance', // 假设后端 type 字段为英文
        },
        failOnStatusCode: false
      }).then(editRes => {
        expect([200, 201]).to.include(editRes.status)
      })
      // 轮询接口直到编辑后的公告出现
      function pollNoticeEdit(retry = 20) {
        if (retry <= 0) throw new Error('公告编辑后接口始终无新标题');
        cy.request({
          method: 'GET',
          url: `${API_BASE_URL}/api/notices/`,
          headers: { Authorization: `Bearer ${token}` },
          failOnStatusCode: false
        }).then(res2 => {
          const arr2 = Array.isArray(res2.body) ? res2.body : (res2.body.data || [])
          if (arr2.some(n => n.title === noticeEditTitle)) {
            cy.log('后端已包含编辑后的公告')
          } else {
            cy.wait(1000).then(() => pollNoticeEdit(retry - 1))
          }
        })
      }
      pollNoticeEdit()
    })

    // 筛选类型和搜索直接用接口断言
    cy.request({
      method: 'GET',
      url: `${API_BASE_URL}/api/notices/?type=maintenance`,
      headers: { Authorization: `Bearer ${token}` },
      failOnStatusCode: false
    }).then(res => {
      const arr = Array.isArray(res.body) ? res.body : (res.body.data || [])
      expect(arr.some(n => n.title === noticeEditTitle)).to.equal(true)
    })
    cy.request({
      method: 'GET',
      url: `${API_BASE_URL}/api/notices/?search=已编辑`,
      headers: { Authorization: `Bearer ${token}` },
      failOnStatusCode: false
    }).then(res => {
      const arr = Array.isArray(res.body) ? res.body : (res.body.data || [])
      expect(arr.some(n => n.title === noticeEditTitle)).to.equal(true)
    })
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

  // 教师端接口方式删除发布的两个公告
  it('教师端接口删除发布的两个公告', () => {
    login(teacher)

    // 删除已编辑的公告
    cy.request({
      method: 'GET',
      url: `${API_BASE_URL}/api/notices/`,
      headers: { Authorization: `Bearer ${token}` },
      failOnStatusCode: false
    }).then(res => {
      const noticesArr = Array.isArray(res.body) ? res.body : (res.body.data || [])
      const editNotice = noticesArr.find(n => n.title === noticeEditTitle)
      expect(editNotice, '后端应有编辑后的公告').to.not.equal(undefined)
      cy.request({
        method: 'DELETE',
        url: `${API_BASE_URL}/api/notices/${editNotice.id}/`,
        headers: { Authorization: `Bearer ${token}` },
        failOnStatusCode: false
      }).then(delRes => {
        expect([200, 204, 202]).to.include(delRes.status)
      })
      // 轮询接口，直到该公告消失
      function pollDelete1(retry = 20) {
        if (retry <= 0) throw new Error('删除后公告仍存在');
        cy.request({
          method: 'GET',
          url: `${API_BASE_URL}/api/notices/`,
          headers: { Authorization: `Bearer ${token}` },
          failOnStatusCode: false
        }).then(res2 => {
          const arr2 = Array.isArray(res2.body) ? res2.body : (res2.body.data || [])
          if (!arr2.some(n => n.title === noticeEditTitle)) {
            cy.log('后端已删除编辑后的公告')
          } else {
            cy.wait(1000).then(() => pollDelete1(retry - 1))
          }
        })
      }
      pollDelete1()
    })
    // 删除第二个公告
    cy.request({
      method: 'GET',
      url: `${API_BASE_URL}/api/notices/`,
      headers: { Authorization: `Bearer ${token}` },
      failOnStatusCode: false
    }).then(res => {
      const noticesArr = Array.isArray(res.body) ? res.body : (res.body.data || [])
      const notice2 = noticesArr.find(n => n.title === noticeTitle2)
      expect(notice2, '后端应有第二个公告').to.not.equal(undefined)
      cy.request({
        method: 'DELETE',
        url: `${API_BASE_URL}/api/notices/${notice2.id}/`,
        headers: { Authorization: `Bearer ${token}` },
        failOnStatusCode: false
      }).then(delRes => {
        expect([200, 204, 202]).to.include(delRes.status)
      })
      // 轮询接口，直到该公告消失
      function pollDelete2(retry = 20) {
        if (retry <= 0) throw new Error('删除后公告2仍存在');
        cy.request({
          method: 'GET',
          url: `${API_BASE_URL}/api/notices/`,
          headers: { Authorization: `Bearer ${token}` },
          failOnStatusCode: false
        }).then(res2 => {
          const arr2 = Array.isArray(res2.body) ? res2.body : (res2.body.data || [])
          if (!arr2.some(n => n.title === noticeTitle2)) {
            cy.log('后端已删除第二个公告')
          } else {
            cy.wait(1000).then(() => pollDelete2(retry - 1))
          }
        })
      }
      pollDelete2()
    })
  })
})
