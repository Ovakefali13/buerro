import { Selector, ClientFunction } from 'testcafe'; // first import testcafe selectors

const path = "http://localhost:" + process.env.FRONTEND_PORT;
fixture `Getting Started`// declare the fixture
    .page(path);  // specify the start page

const setLocalStorageItem = ClientFunction((prop, value) => {
    localStorage.setItem(prop, value);
});
const getLocalStorageItem = ClientFunction(prop => {
    return localStorage.getItem(prop);
});



//then create a test and place your code there
test('My first test', async t => {
    await t.expect(Selector("title").innerText).eql('buerro');

    const sayBtn = Selector('.chat-say-btn');
    await t.click(sayBtn)
        .expect(getLocalStorageItem('ttsEnabled')).eql('false');
});
