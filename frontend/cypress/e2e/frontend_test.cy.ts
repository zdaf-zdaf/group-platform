describe('前端关键流程测试', () => {
  it('访问首页', () => {
    cy.visit('http://localhost:8080')
    cy.contains('实验管理').should('be.visible')
  })

  it('模拟登录', () => {
    cy.get('#username').type('testuser')
    cy.get('#password').type('123456')
    cy.get('#loginBtn').click()
    cy.contains('实验列表').should('be.visible')
  })
})
