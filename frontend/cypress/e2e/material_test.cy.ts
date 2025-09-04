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
    // 检查 token 注入
    cy.window().then(win => {
      const tk = win.localStorage.getItem('token')
      const info = win.localStorage.getItem('userInfo')
      cy.log('localStorage token:', tk)
      cy.log('localStorage userInfo:', info)
      expect(tk, 'token存在').to.match(/^.+$/)
      expect(info, 'userInfo存在').to.match(/^.+$/)
    })

    cy.contains('学习资料').click({ force: true })
    cy.url().should('include', '/studyfile')
    cy.get('.material-page').should('exist')

    const types = [
      { label: 'PDF文档', value: 'pdf', file: 'test.pdf' },
      { label: '文档资料', value: 'doc', file: 'test.docx' },
      { label: '图表素材', value: 'image', file: 'test.png' },
      { label: '视频教程', value: 'video', file: 'test.mp4' }
    ];

    types.forEach((item) => {
      const title = `自动化测试资料${item.label}`;
      cy.fixture(item.file, 'base64').then(fileContent => {
        const formData = new FormData();
        formData.append('title', title);
        formData.append('description', `这是${item.label}类型的测试资料`);
        formData.append('type', item.value);
        // 转成 blob
        const byteCharacters = atob(fileContent);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray]);
        formData.append('file', blob, item.file.split('/').pop());
        cy.request({
          method: 'POST',
          url: `${API_BASE_URL}/materials/`,
          headers: {
            Authorization: `Bearer ${token}`
          },
          body: formData,
          // 关键：Cypress 12+ 支持 formData 直接传递
          form: true
        }).then(res => {
          expect([200, 201]).to.include(res.status);
        });
      });
      // 轮询资料列表接口，直到新资料出现
      function pollMaterialList(retry = 30) {
        if (retry <= 0) throw new Error('资料列表接口始终无新资料');
        cy.request({
          method: 'GET',
          url: `${API_BASE_URL}/materials/`,
          headers: { Authorization: `Bearer ${token}` },
          failOnStatusCode: false
        }).then(res => {
          const materialsArr = Array.isArray(res.body) ? res.body : (res.body.data || []);
          if (materialsArr.some(m => m.title === title)) {
            cy.log('资料列表接口包含新资料');
          } else {
            cy.wait(2000).then(() => pollMaterialList(retry - 1));
          }
        });
      }
      pollMaterialList();
      // 用接口校验资料已发布
      cy.request({
        method: 'GET',
        url: `${API_BASE_URL}/materials/`,
        headers: { Authorization: `Bearer ${token}` },
        failOnStatusCode: false
      }).then(res => {
        const materialsArr = Array.isArray(res.body) ? res.body : (res.body.data || []);
        expect(materialsArr.some(m => m.title === title), '后端资料列表包含新资料').to.equal(true);
      });
    });
  })

  // ========================
  // 学生端查看并预览四种类型资料，下载第一个
  // ========================
  it('学生端查看并预览四种类型资料，下载第一个', () => {
    login(student)

    cy.contains('学习资料').click({ force: true })
    cy.url().should('include', '/studyfile')
    cy.get('.material-page').should('exist')

    // 轮询资料列表接口，直到有资料
    function pollMaterialList(retry = 30) {
      if (retry <= 0) throw new Error('资料列表接口始终无数据');
      cy.request({
        method: 'GET',
        url: `${API_BASE_URL}/materials/`,
        headers: { Authorization: `Bearer ${token}` },
        failOnStatusCode: false
      }).then(res => {
        const materialsArr = Array.isArray(res.body) ? res.body : (res.body.data || []);
        if (materialsArr.length > 0) {
          cy.log('资料列表接口有数据');
        } else {
          cy.wait(2000).then(() => pollMaterialList(retry - 1));
        }
      });
    }
    pollMaterialList();
    cy.reload()
    // 依次预览四种类型（UI操作）
    const previewTypes = ['PDF文档', '文档资料', '图表素材', '视频教程']
    previewTypes.forEach(label => {
      cy.get('.material-list .material-item').contains(label).parents('.material-item').then($item => {
        cy.wrap($item).contains('在线预览').click({ force: true })
        cy.wait(1000)
      })
    })
    // 下载第一个资料（UI操作）
    cy.get('.material-list .material-item').first().within(() => {
      cy.contains('下载文件').click({ force: true })
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

    // 轮询资料列表接口，直到有资料
    function pollMaterialList(retry = 30) {
      if (retry <= 0) throw new Error('资料列表接口始终无数据');
      cy.request({
        method: 'GET',
        url: `${API_BASE_URL}/materials/`,
        headers: { Authorization: `Bearer ${token}` },
        failOnStatusCode: false
      }).then(res => {
        const materialsArr = Array.isArray(res.body) ? res.body : (res.body.data || []);
        if (materialsArr.length > 0) {
          cy.log('资料列表接口有数据');
        } else {
          cy.wait(2000).then(() => pollMaterialList(retry - 1));
        }
      });
    }
    pollMaterialList();
    cy.reload()
    // 用接口查找并删除自动化测试发布的四个资料
    const titles = [
      '自动化测试资料PDF文档',
      '自动化测试资料文档资料',
      '自动化测试资料图表素材',
      '自动化测试资料视频教程'
    ]
    cy.request({
      method: 'GET',
      url: `${API_BASE_URL}/materials/`,
      headers: { Authorization: `Bearer ${token}` },
      failOnStatusCode: false
    }).then(res => {
      const materialsArr = Array.isArray(res.body) ? res.body : (res.body.data || [])
      titles.forEach(title => {
        const mat = materialsArr.find(m => m.title === title)
        expect(mat, `后端资料列表应包含${title}`).to.not.equal(undefined)
        // 直接用接口删除
        cy.request({
          method: 'DELETE',
          url: `${API_BASE_URL}/materials/${mat.id}/`,
          headers: { Authorization: `Bearer ${token}` },
          failOnStatusCode: false
        }).then(delRes => {
          expect([200, 204, 202]).to.include(delRes.status)
        })
      })
    })
  })
})
