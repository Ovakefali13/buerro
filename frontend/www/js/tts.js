var running = false;
var synth = window.speechSynthesis;

enabled = !(window.localStorage.getItem('ttsEnabled') == 'false')

$(document).ready(() => {
    if (!enabled) {
        $("#speak").css("background-color","Gray");
    }
});

function toggle_speech() {
    if(enabled) {
        synth.cancel()
        enabled = false;
        window.localStorage.setItem('ttsEnabled', false);
        $("#speak").css("background-color","Gray");
    } else {
        enabled = true;
        window.localStorage.setItem('ttsEnabled', true);
        $("#speak").css("background-color","Green");  
    }
}

function speak() {
    if(enabled) {
        const div = document.getElementById('chatbubbles').lastElementChild
        const utterance = new SpeechSynthesisUtterance(div.textContent.trim());        
        utterance.lang = 'en-US';    

        synth.speak(utterance);
    }
}
