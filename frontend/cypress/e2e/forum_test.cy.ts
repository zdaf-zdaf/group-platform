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
      // 兼容 window 上没有 VUE_APP_API_BASE_URL 的情况，避免 any
      const vueEnv = win as Window & { VUE_APP_API_BASE_URL?: string }
      cy.log('window.VUE_APP_API_BASE_URL:', vueEnv.VUE_APP_API_BASE_URL)
    })
    cy.readFile('src/api/auth.ts').then((content) => {
      const match = content.match(/baseURL:\s*([\'\"])(.*?)\1/)
      if (match) cy.log('axios baseURL:', match[2])
    })
  })
  let token = ''
  function login(user: { username: string; password: string }) {
    return cy.request('POST', 'http://127.0.0.1:8000/api/auth/login/', {
      username: user.username,
      password: user.password
    }).then((response) => {
      expect(response.status).to.eq(200);
      const accessToken = response.body.access;
      expect(accessToken, 'token should exist').to.not.equal(null);
      token = accessToken;
      cy.log(`最终 token: ${token}`);
      return cy.visit('/', {
        onBeforeLoad(win) {
          win.localStorage.setItem('token', token);
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
    }).then(() => {
      cy.wait(1000);
      cy.visit('/forum');
      cy.wait(2000);
      cy.reload();
      cy.wait(1000);
      return cy.window().then(win => {
        const savedToken = win.localStorage.getItem('token');
        cy.log('localStorage token:', savedToken);
        expect(savedToken).to.match(/^.+$/);
      });
    });
  }

  // 学生端发帖、点赞、评论、删除（全部接口流）
  it('学生端接口发帖、点赞、评论、删除', () => {
    login(student).then(() => {
      cy.log('token for student:', token)
      // 发帖
      cy.request({
        method: 'POST',
        url: 'http://127.0.0.1:8000/api/forum/questions/',
        headers: { Authorization: `Bearer ${token}` },
        body: {
          title: postTitle,
          content: postContent
        },
        failOnStatusCode: false
      }).then(res => {
        cy.log('发帖返回', res.status, JSON.stringify(res.body))
        expect(res.status).to.eq(201)
        const postId = res.body.id
        // 轮询接口直到新发帖出现
        function pollForumList(retry = 10) {
          if (retry <= 0) throw new Error('帖子列表接口始终无新发帖');
          cy.request({
            method: 'GET',
            url: 'http://127.0.0.1:8000/api/forum/questions/',
            headers: { Authorization: `Bearer ${token}` },
            failOnStatusCode: false
          }).then(res2 => {
            const postsArr = Array.isArray(res2.body) ? res2.body : (res2.body.data || [])
            if (postsArr.some(q => q.title === postTitle)) {
              cy.log('帖子列表接口包含新发帖')
            } else {
              cy.wait(1000).then(() => pollForumList(retry - 1))
            }
          })
        }
        pollForumList()

        // 点赞
        cy.request({
          method: 'PATCH',
          url: `http://127.0.0.1:8000/api/forum/questions/${postId}/toggle-like/`,
          headers: { Authorization: `Bearer ${token}` },
          failOnStatusCode: false
        }).then(likeRes => {
          expect([200, 201]).to.include(likeRes.status)
        })
        // 取消点赞
        cy.request({
          method: 'PATCH',
          url: `http://127.0.0.1:8000/api/forum/questions/${postId}/toggle-like/`,
          headers: { Authorization: `Bearer ${token}` },
          failOnStatusCode: false
        }).then(unlikeRes => {
          expect([200, 201]).to.include(unlikeRes.status)
        })

        // 评论
        cy.request({
          method: 'POST',
          url: `http://127.0.0.1:8000/api/forum/questions/${postId}/comments/`,
          headers: { Authorization: `Bearer ${token}` },
          body: { content: postComment },
          failOnStatusCode: false
        }).then(commentRes => {
          expect(commentRes.status).to.eq(201)
          const commentId = commentRes.body.id
          // 删除评论
          cy.request({
            method: 'DELETE',
            url: `http://127.0.0.1:8000/api/forum/comments/${commentId}/`,
            headers: { Authorization: `Bearer ${token}` },
            failOnStatusCode: false
          }).then(delCommentRes => {
            expect([200, 204, 202]).to.include(delCommentRes.status)
          })
        })

        // 删除帖子
        cy.request({
          method: 'DELETE',
          url: `http://127.0.0.1:8000/api/forum/questions/${postId}/`,
          headers: { Authorization: `Bearer ${token}` },
          failOnStatusCode: false
        }).then(delPostRes => {
          expect([200, 204, 202]).to.include(delPostRes.status)
        })
      })
    })
  })

  // 教师端接口置顶、点赞、评论、删除
  it('教师端接口置顶、点赞、评论、删除', () => {
    login(teacher).then(() => {
      cy.log('token for teacher:', token)
      // 发帖
      cy.request({
        method: 'POST',
        url: 'http://127.0.0.1:8000/api/forum/questions/',
        headers: { Authorization: `Bearer ${token}` },
        body: {
          title: postTitle,
          content: postContent
        },
        failOnStatusCode: false
      }).then(res => {
        cy.log('发帖返回', res.status, JSON.stringify(res.body))
        expect(res.status).to.eq(201)
        const postId = res.body.id
        // 轮询接口直到新发帖出现
        function pollForumList(retry = 10) {
          if (retry <= 0) throw new Error('帖子列表接口始终无新发帖');
          cy.request({
            method: 'GET',
            url: 'http://127.0.0.1:8000/api/forum/questions/',
            headers: { Authorization: `Bearer ${token}` },
            failOnStatusCode: false
          }).then(res2 => {
            const postsArr = Array.isArray(res2.body) ? res2.body : (res2.body.data || [])
            if (postsArr.some(q => q.title === postTitle)) {
              cy.log('帖子列表接口包含新发帖')
            } else {
              cy.wait(1000).then(() => pollForumList(retry - 1))
            }
          })
        }
        pollForumList()

        // 置顶
        cy.request({
          method: 'PATCH',
          url: `http://127.0.0.1:8000/api/forum/questions/${postId}/toggle-sticky/`,
          headers: { Authorization: `Bearer ${token}` },
          failOnStatusCode: false
        }).then(stickyRes => {
          expect([200, 201]).to.include(stickyRes.status)
        })
        // 取消置顶
        cy.request({
          method: 'PATCH',
          url: `http://127.0.0.1:8000/api/forum/questions/${postId}/toggle-sticky/`,
          headers: { Authorization: `Bearer ${token}` },
          failOnStatusCode: false
        }).then(unstickyRes => {
          expect([200, 201]).to.include(unstickyRes.status)
        })

        // 点赞
        cy.request({
          method: 'PATCH',
          url: `http://127.0.0.1:8000/api/forum/questions/${postId}/toggle-like/`,
          headers: { Authorization: `Bearer ${token}` },
          failOnStatusCode: false
        }).then(likeRes => {
          expect([200, 201]).to.include(likeRes.status)
        })
        // 取消点赞
        cy.request({
          method: 'PATCH',
          url: `http://127.0.0.1:8000/api/forum/questions/${postId}/toggle-like/`,
          headers: { Authorization: `Bearer ${token}` },
          failOnStatusCode: false
        }).then(unlikeRes => {
          expect([200, 201]).to.include(unlikeRes.status)
        })

        // 评论
        cy.request({
          method: 'POST',
          url: `http://127.0.0.1:8000/api/forum/questions/${postId}/comments/`,
          headers: { Authorization: `Bearer ${token}` },
          body: { content: teacherComment },
          failOnStatusCode: false
        }).then(commentRes => {
          expect(commentRes.status).to.eq(201)
          const commentId = commentRes.body.id
          // 删除评论
          cy.request({
            method: 'DELETE',
            url: `http://127.0.0.1:8000/api/forum/comments/${commentId}/`,
            headers: { Authorization: `Bearer ${token}` },
            failOnStatusCode: false
          }).then(delCommentRes => {
            expect([200, 204, 202]).to.include(delCommentRes.status)
          })
        })

        // 删除帖子
        cy.request({
          method: 'DELETE',
          url: `http://127.0.0.1:8000/api/forum/questions/${postId}/`,
          headers: { Authorization: `Bearer ${token}` },
          failOnStatusCode: false
        }).then(delPostRes => {
          expect([200, 204, 202]).to.include(delPostRes.status)
        })
      })
    })
  })
})
