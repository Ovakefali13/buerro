const pti = require('puppeteer-to-istanbul')

describe('Title', () => {
    beforeAll(async () => {
        await page.goto(PATH, { waitUntil: 'load' });
        // Enable both JavaScript and CSS coverage
        await Promise.all([
            page.coverage.startJSCoverage(),
            page.coverage.startCSSCoverage()
        ]);
    });

    it('should be titled "buerro"', async () => {
        await expect(page.title()).resolves.toMatch('buerro');
    });

    afterAll(async () => {
        // Disable both JavaScript and CSS coverage
        const [jsCoverage, cssCoverage] = await Promise.all([
            page.coverage.stopJSCoverage(),
            page.coverage.stopCSSCoverage(),
        ]);
        pti.write([...jsCoverage, ...cssCoverage])
    });
});

