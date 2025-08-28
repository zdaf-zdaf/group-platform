/// <reference types="cypress" />

describe('灵狐智验前端完整流程集成测试', () => {

  const studentUsername = `stu${Date.now() % 10000}`
  const teacherUsername = `tch${Date.now() % 10000}`
  const experimentTitle = 'Cypress全流程实验'
  const experimentDescription = '自动化测试实验描述'
  const startTime = '2025-08-27 15:00:00'
  const deadlineTime = '2025-08-28 23:59:59'
  const codeSample =
`
a, b = map(int, input().split())
print(a + b)

`
  const password = 'Test1234@'

  // ========================
  // 学生注册
  // ========================
  it('学生注册流程', () => {
    cy.visit('http://localhost:5173/register')
    cy.get('input[placeholder="请输入3-16位用户名"]').type(studentUsername)
    cy.get('input[placeholder="请输入邮箱地址"]').type(`${studentUsername}@example.com`)
    cy.get('input[placeholder="请输入6-18位密码"]').type(password)
    cy.get('input[placeholder="请再次输入密码"]').type(password)
    cy.get('.el-select').click()
    cy.get('.el-select-dropdown__item').contains('学生').click({ force: true })
    cy.get('input[type="checkbox"]').check({ force: true })
    cy.get('button').contains('注册账号').click()
    cy.contains('注册成功！').should('be.visible')
  })

  // ========================
  // 教师注册
  // ========================
  it('教师注册流程', () => {
    cy.visit('http://localhost:5173/register')
    cy.get('input[placeholder="请输入3-16位用户名"]').type(teacherUsername)
    cy.get('input[placeholder="请输入邮箱地址"]').type(`${teacherUsername}@example.com`)
    cy.get('input[placeholder="请输入6-18位密码"]').type(password)
    cy.get('input[placeholder="请再次输入密码"]').type(password)
    cy.get('.el-select').click()
    cy.get('.el-select-dropdown__item').contains('教师').click({ force: true })
    cy.get('input[type="checkbox"]').check({ force: true })
    cy.get('button').contains('注册账号').click()
    cy.contains('注册成功！').should('be.visible')
  })

  // ========================
  // 教师登录并创建实验
  // ========================
  it('教师登录并创建实验', () => {
    cy.visit('http://localhost:5173/login')
    cy.get('input[placeholder="请输入用户名"]').type(teacherUsername)
    cy.get('input[placeholder="请输入密码"]').type(password)
    cy.get('input[type="checkbox"]').check({ force: true })
    cy.get('button').contains('立即登录').click()
    cy.url().should('include', '/profile')

    cy.contains('创建实验').click({ force: true })
    cy.get('.publish-set .set-card', { timeout: 10000 }).should('be.visible')

    // 填写实验信息
    cy.get('.publish-set .set-card').within(() => {
      cy.get('input[placeholder^="如：数组与字符串题组"]').type(experimentTitle)
      cy.get('input[placeholder^="如：描述实验的目的和内容"]').type(experimentDescription)

      // 修改开始时间选择方式 - 使用原生Date对象
      const now = new Date()
      const startTime = new Date(now.getTime() + 60 * 60 * 1000) // 当前时间+1小时
      const startTimeStr = startTime.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      }).replace(/\//g, '-')

      // 修改截止时间选择方式 - 使用原生Date对象
      const deadlineTime = new Date(now.getTime() + 25 * 60 * 60 * 1000) // 当前时间+25小时
      const deadlineTimeStr = deadlineTime.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      }).replace(/\//g, '-')

      cy.get('input[placeholder="选择开始时间"]').clear({ force: true }).type(startTimeStr, { force: true })
      cy.get('input[placeholder="选择截止时间"]').clear({ force: true }).type(deadlineTimeStr, { force: true })


      // 等待学生数据加载完成
      cy.get('.el-transfer-panel__list').should('be.visible')
      cy.get('.el-transfer-panel__item').should('have.length.gt', 0)

      // 根据图片修改学生选择逻辑
      // 1. 先点击"未选学生"左侧的全选复选框
      cy.get('.el-transfer-panel__header input[type="checkbox"]').first().check({ force: true })

      // 2. 然后点击向右箭头按钮（第二个按钮）
      cy.get('.el-transfer__buttons button').eq(1).click({ force: true })
    })

    // 选择题
    cy.get('.publish-set .set-card .question-card').last().within(() => {
      // 打开“题目类型”下拉框
      cy.get('.el-select').click({ force: true })
      // 直接在当前上下文里找 dropdown（因为 teleported=false）
      cy.get('.el-select__popper')
        .should('exist')
        .within(() => {
          cy.get('.el-select-dropdown__item').contains('选择题').click({ force: true })
        })

      // 断言
      cy.get('.el-select').should('contain.text', '选择题')

      cy.get('textarea[placeholder="请输入题目描述"]').type('选择题示例题干', { force: true })

      // 填写分值（第一个数字输入框是分值）
      cy.get('.el-input-number input')
        .first()
        .clear()
        .type('10', { force: true })

      // 添加选项 A
      cy.get('input[placeholder="选项文本"]').last().type('选项A', { force: true })
      cy.contains('button', '添加选项').click({ force: true })
      cy.get('input[placeholder="选项文本"]').last().type('选项B', { force: true })

      // 添加选项 B
      cy.contains('button', '添加选项').click({ force: true })
      cy.get('input[placeholder="选项文本"]').last().type('选项C', { force: true })

      // 设置正确答案（选择第一个单选框）
      cy.get('.el-radio__original').first().check({ force: true })
    })

    // 添加题目（填空题）
    cy.get('.publish-set .set-card').contains('添加题目').click({ force: true })
    cy.get('.publish-set .set-card .question-card').last().within(() => {
      cy.get('.el-select').click({ force: true })
      cy.get('.el-select__popper')
        .should('exist')
        .within(() => {
          cy.get('.el-select-dropdown__item').contains('填空题').click({ force: true })
        })
      cy.get('.el-select').should('contain.text', '填空题')
      cy.get('textarea[placeholder="请输入题目描述"]').type('填空题示例题干', { force: true })
      cy.get('.el-input-number input').first().clear().type('5', { force: true })
      cy.get('input[placeholder="请输入标准答案"]').type('标准答案', { force: true })
    })

    // 添加题目（编程题）
    cy.get('.publish-set .set-card').contains('添加题目').click({ force: true })
    cy.get('.publish-set .set-card .question-card').last().within(() => {
      cy.get('.el-select').click({ force: true })
      cy.get('.el-select__popper')
        .should('exist')
        .within(() => {
          cy.get('.el-select-dropdown__item').contains('编程题').click({ force: true })
        })
      cy.get('.el-select').should('contain.text', '编程题')

      cy.get('textarea[placeholder="请输入题目描述"]').type('编程题示例题干', { force: true })
      cy.get('.el-input-number input').first().clear().type('20', { force: true })
      cy.get('input[placeholder="请输入时间限制（秒）"]').type('2', { force: true })
      cy.get('input[placeholder="请输入内存限制（MB）"]').type('256', { force: true })

      // 添加测试点
      cy.get('.el-button').contains('添加测试点').click({ force: true })
      cy.get('input[placeholder="输入"]').last().type('1 2', { force: true })
      cy.get('input[placeholder="期望输出"]').last().type('3', { force: true })
    })


    cy.get('.publish-set .set-card').contains('发布实验').click({ force: true })
    cy.contains(experimentTitle).should('be.visible')
  })

  // ========================
  // 学生登录完成实验
  // ========================
  it('学生登录完成实验', () => {
    cy.visit('http://localhost:5173/login')
    cy.get('input[placeholder="请输入用户名"]').type(studentUsername)
    cy.get('input[placeholder="请输入密码"]').type(password)
    cy.get('input[type="checkbox"]').check({ force: true })
    cy.get('button').contains('立即登录').click()
    cy.url().should('include', '/profile')

    cy.contains('实验中心').click({ force: true })
    cy.contains(experimentTitle).click({ force: true })

     // ========================
      // 选择题完成
      // ========================
      cy.get('#choice-section .question-card').each($card => {
        cy.wrap($card).within(() => {
          cy.get('input[type="radio"]').first().check({ force: true })
        })
      })

      // ========================
      // 填空题完成
      // ========================
      cy.get('#fill-section .question-card').each($card => {
        cy.wrap($card).within(() => {
          cy.get('input[placeholder="请输入答案"]').type('答案')
        })
      })

      // ========================
      // 编程题完成
      // ========================
      cy.get('#coding-section .question-card').each($card => {
        cy.wrap($card).within(() => {
           cy.intercept('GET', '**/coding/*').as('fetchProblem')
          // 点击开始编程
          cy.contains('开始编程').click()
        })
          // 等待新页面跳转并加载编辑器
        cy.url({ timeout: 10000 }).should('include', '/coding/')
        // 等待编程题接口返回，保证题目加载完成

        cy.wait('@fetchProblem', { timeout: 20000 }).its('response.statusCode').should('eq', 200)

        // 确保编辑器与题干渲染出来
        cy.get('.coding-editor', { timeout: 30000 }).should('be.visible')
        cy.get('.editor-panel', { timeout: 30000 }).should('exist').and('be.visible')

        // Monaco Editor 输入代码 - 使用更可靠的选择器
        cy.get('.editor-panel textarea', { timeout: 15000 })
          .should('be.visible')
          .type(codeSample, {
            parseSpecialCharSequences: false,
            delay: 5,
            force: true
          })

          // 上传文件
        const filePath = 'cypress/fixtures/test.py' // 确保文件存在于这个路径
        cy.readFile(filePath, 'utf8').then(fileContent => {
          cy.get('.problem-panel input[type="file"]').selectFile({
            contents: Cypress.Buffer.from(fileContent),
            fileName: 'test.py',
            mimeType: 'text/x-python'
          }, { force: true })
        })
        // 提交代码并等待接口响应
        cy.intercept('POST', '**/experiments/judge/').as('submitCode')
        cy.contains('提交代码').click()
        cy.wait('@submitCode').its('response.statusCode').should('eq', 200)

        // 等待结果面板出现
        cy.get('.result-panel .el-alert', { timeout: 30000 }).should('exist')

        // 返回实验详情
        cy.contains('返回实验详情').click()
      })
      cy.url().should('include', '/experiment/')

      // ========================
      // 返回实验详情并提交实验
      // ========================
      cy.contains('提交实验').click()
      cy.get('.el-dialog__footer').within(() => {
        cy.contains('确认提交').click({ force: true })
      })
      cy.contains('总得分').should('be.visible')

  })
  // ========================
  // 教师查看学生提交记录与详情
  // ========================
  it('教师查看学生提交记录与详情', () => {
    // 教师登录
    cy.visit('http://localhost:5173/login')
    cy.get('input[placeholder="请输入用户名"]').type(teacherUsername)
    cy.get('input[placeholder="请输入密码"]').type(password)
    cy.get('input[type="checkbox"]').check({ force: true })
    cy.get('button').contains('立即登录').click()
    cy.url().should('include', '/profile')

    // 进入“实验管理”或“批改作业”页面（假设有入口按钮/菜单）
    cy.contains('查看学生提交').click({ force: true })

    // 等待提交卡片加载
    cy.get('.submission-card', { timeout: 10000 }).should('exist')

    // 检查至少有一条提交记录，且包含学生名、题组、提交时间等
    cy.get('.submission-card').first().within(() => {
      cy.contains('学生：').should('exist')
      cy.contains('题组：').should('exist')
      cy.contains('提交时间：').should('exist')
    })

    // 点击第一条提交，进入详情页
    cy.get('.submission-card').first().click()

    // 检查详情页内容
    cy.url().should('include', 'submission-detail')
    cy.get('.submission-detail').should('exist')
    cy.get('.student-info').should('contain.text', '学生：')
    cy.get('.student-info').should('contain.text', '提交时间：')
    cy.get('.question-card').should('exist')
    cy.get('.q-header').should('exist')
    cy.get('.q-content').should('exist')

    // 检查保存批改结果按钮
    cy.contains('保存批改结果').should('exist')
  })
})
