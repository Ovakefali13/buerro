var running = false;
var enabled = true;
var synth = window.speechSynthesis;

function toggle_speech() {
    if(enabled) {
        if(running) {
            synth.cancel()
            running = false
        }
        enabled = false;
        $("#speak").css("background-color","Gray");
    } else {
        enabled = true;
        $("#speak").css("background-color","Green");  
    }
}

function speak() {
    if(enabled) {
        const div = document.getElementById('chatbubbles').lastElementChild
        const utterance = new SpeechSynthesisUtterance(div.textContent.trim());        
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
}
