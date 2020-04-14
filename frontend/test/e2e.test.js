const pti = require('puppeteer-to-istanbul')

describe('Title', () => {
    beforeAll(async () => {
        path = HOST + ":" + process.env.FRONTEND_PORT;
        await page.goto(path, { waitUntil: 'load' });
        // Enable both JavaScript and CSS coverage
        await Promise.all([
            page.coverage.startJSCoverage(),
            page.coverage.startCSSCoverage()
        ]);

    });

    it('should be titled "buerro"', async () => {
        await expect(page.title()).resolves.toMatch('buerro');
    });

    it('can send location', async () => {
        await page.setGeolocation({
            latitude: 48.773466,
            longitude: 9.170824
        });

        await page.evaluate(() => {
            return sendCurrentLocation();
        })
        .catch(err => {
            console.log('Failed to send location ', err);
        })
        .then(response => {
            expect(response).toBeDefined();
            expect(response.success).toBeTruthy();
        });
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

