var running = false;
var synth = window.speechSynthesis;
var i = 0;

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
        if(i>=21)i=0;
        const div = document.getElementById('chatbubbles').lastElementChild
        text = div.textContent.trim()             
        l = speechSynthesis.getVoices();
        const utterance=new SpeechSynthesisUtterance(text);   
        utterance.voice=l[i];
        synth.speak(utterance);
        i++;
    }
}
