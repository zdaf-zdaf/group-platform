import { defineConfig } from "cypress";

export default defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
    specPattern: "cypress/e2e/**/*.cy.{js,ts}", // 可根据你的项目调整
  },
  video: true,                       // 开启录像
  videosFolder: "cypress/videos",    // 视频保存路径
  reporter: 'mocha-multi-reporters',
  reporterOptions: {
    reporterEnabled: 'mochawesome, mocha-junit-reporter',
    mochawesomeReporterOptions: {
      reportDir: 'cypress/cypress-report',
      overwrite: false,
      html: true,
      json: true
    },
    mochaJunitReporterReporterOptions: {
      mochaFile: 'cypress/cypress-report/junit-[hash].xml',
      toConsole: false
    }
  },
});
