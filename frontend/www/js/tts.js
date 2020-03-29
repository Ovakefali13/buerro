var running = false;
function speak() {
    const div = document.getElementById('chatbubbles').lastElementChild
    text = div.textContent.trim();

    var regex = new RegExp('.*(?!http[^ ]*)');
    match = text.match(regex);
    if (match) {
       text = match[0];
    }
    const utterance = new SpeechSynthesisUtterance(text);
    var synth = window.speechSynthesis;
    utterance.lang = 'en-US';    

    if(running) {
        synth.cancel()
        running = false
    } else {
        running = true;                
        synth.speak(utterance);
        utterance.onend = function(event) {
            running = false;
        }
    }
}
