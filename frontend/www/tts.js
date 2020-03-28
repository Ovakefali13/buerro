function speak() {
    const toSay = document.getElementById('prompt_input').value.trim();
    const utterance = new SpeechSynthesisUtterance(toSay);
    utterance.lang = 'en-US';    
    speechSynthesis.speak(utterance);
}
