var running = false;
function speak() {
    const div = document.getElementById('chatbubbles').lastElementChild    
    const utterance = new SpeechSynthesisUtterance(div.textContent.trim());
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
