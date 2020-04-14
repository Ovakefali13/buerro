const { teardown: teardownPuppeteer } = require('jest-environment-puppeteer')

module.exports = async function globalTeardown(globalConfig) {
  // Your global teardown
  await teardownPuppeteer(globalConfig)
}
