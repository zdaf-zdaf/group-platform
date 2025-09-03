/// <reference types="cypress" />

describe('论坛模块功能测试', () => {
  const teacher = { username: 'tchTest', password: 'Test1234@' }
  const student = { username: 'stuTest', password: 'Test1234@' }
  const postTitle = '自动化测试论坛帖'
  const postContent = '这是自动化测试发布的论坛内容，内容不少于10字。'
  const postComment = '自动化测试评论内容'
  const teacherComment = '教师自动化评论内容'

  // 输出环境变量和 axios baseURL，便于调试
  before(() => {
    cy.log('process.env.VUE_APP_API_BASE_URL:', Cypress.env('VUE_APP_API_BASE_URL'))
    cy.window().then(win => {
      cy.log('window.VUE_APP_API_BASE_URL:', win.VUE_APP_API_BASE_URL)
    })
    cy.readFile('src/api/auth.ts').then((content) => {
      const match = content.match(/baseURL:\s*([\'\"])(.*?)\1/)
      if (match) cy.log('axios baseURL:', match[2])
    })
  })
  let token = ''
  function login(user: { username: string; password: string }) {
    cy.request('POST', 'http://127.0.0.1:8000/api/auth/login/', {
      username: user.username,
      password: user.password
    }).then((response) => {
      expect(response.status).to.eq(200);
      const accessToken = response.body.access;
      expect(accessToken, 'token should exist').to.not.be.null;

      token = accessToken; // 只存 accessToken，不加 Bearer
      cy.log(`最终 token: ${token}`);

      // 测试 token 是否可用
      cy.request({
        method: 'GET',
        url: 'http://127.0.0.1:8000/api/forum/questions/',
        headers: { Authorization: `Bearer ${token}` },
        failOnStatusCode: false
      }).then(res => {
        cy.log('登录后立即测试 token 结果:', JSON.stringify(res.body));
        cy.log('测试请求状态码:', res.status);
      });

      // 先设置 localStorage，再访问页面，避免 token 丢失
      cy.visit('/', {
        onBeforeLoad(win) {
          win.localStorage.setItem('token', token); // 只存 accessToken
          if (response.body.username) {
            win.localStorage.setItem('userInfo', JSON.stringify({
              username: response.body.username,
              role: response.body.role,
              email: response.body.email,
              student_id: response.body.student_id,
              faculty: response.body.faculty
            }));
          }
        }
      });
      cy.wait(1000);
      cy.visit('/forum');
      cy.wait(2000);
      cy.reload();
      cy.wait(1000);
      cy.window().then(win => {
        const savedToken = win.localStorage.getItem('token');
        cy.log('localStorage token:', savedToken);
        expect(savedToken).to.match(/^.+$/); // 只要有内容即可
      });
    });
  }

  // 学生端发帖、点赞、评论、删除
  it('学生端发帖、点赞、评论、删除', () => {
    login(student)

    // 页面缓冲，确保渲染和数据加载完成
    cy.wait(3000)
    cy.get('.forum', { timeout: 20000 }).should('exist')
    cy.wait(2000)

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
        url: 'http://127.0.0.1:8000/api/forum/questions/',
        headers: { Authorization: `Bearer ${token}` },
        failOnStatusCode: false // CI 调试用，避免非200直接失败
      }).then(res => {
  // ...日志已移除...
        expect(res.body.some(q => q.title === postTitle)).to.be.true
      })
    })
    cy.wait(5000); // 发帖后等待更久
    cy.reload();
    cy.wait(3000);
    cy.reload();
    cy.wait(2000);

    cy.get('.post-card', { timeout: 30000 }).should('exist');
    cy.get('.post-card').should('contain.text', postTitle);

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
        url: 'http://127.0.0.1:8000/api/forum/questions/',
        headers: { Authorization: `Bearer ${token}` },
        failOnStatusCode: false // CI 调试用，避免非200直接失败
      }).then(res => {
        expect(res.body.some(q => q.title === postTitle)).to.be.true
      })
    })
    cy.wait(5000); // 发帖后等待更久
    cy.reload();
    cy.wait(3000);
    cy.reload();
    cy.wait(2000);

    cy.get('.post-card', { timeout: 30000 }).should('exist');
    cy.get('.post-card').should('contain.text', postTitle);

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
