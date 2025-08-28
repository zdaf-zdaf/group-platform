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
});
