var final_transcript = '';
var recognizing = false;
var ignore_onend;
var start_timestamp;
if (!('webkitSpeechRecognition' in window)) {
  upgrade();
} else {
  var recognition = new webkitSpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;

  recognition.onstart = function() {
    $("#record").css("background-color","Crimson");
    recognizing = true;
  };

  recognition.onerror = function(event) {
    if (event.error == 'no-speech') {      
      showInfo('info_no_speech');
      ignore_onend = true;
    }
    if (event.error == 'audio-capture') {
      showInfo('info_no_microphone');
      ignore_onend = true;
    }
    if (event.error == 'not-allowed') {
      if (event.timeStamp - start_timestamp < 100) {
        showInfo('info_blocked');
      } else {
        showInfo('info_denied');
      }
      ignore_onend = true;
    }
  };

  recognition.onend = function() {
    recognizing = false;
    if (ignore_onend) {
      return;
    } 
    if (window.getSelection) {
      window.getSelection().removeAllRanges();
      var range = document.createRange();
      range.selectNode(document.getElementById('prompt_input'));
      window.getSelection().addRange(range);
      $("#prompt_input").val("");
    }    
  };

  recognition.onresult = function(event) {
    var interim_transcript = '';
    if (typeof(event.results) == 'undefined') {
      recognition.onend = null;
      recognition.stop();
      upgrade();
      return;
    }
    for (var i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        final_transcript += event.results[i][0].transcript;
      } else {
        interim_transcript += event.results[i][0].transcript;
      }
    }
    final_transcript = capitalize(final_transcript);        
    document.getElementById('prompt_input').value = linebreak(final_transcript);
    if (interim_transcript) document.getElementById('prompt_input').value = linebreak(final_transcript) + linebreak(interim_transcript);
    if (document.getElementById('prompt_input').value != '' && !$('#loader').is(':visible')) $('#submit-btn').prop('disabled',false);
  };
}

var two_line = /\n\n/g;
var one_line = /\n/g;
function linebreak(s) {
  return s.replace(two_line, '<p></p>').replace(one_line, '<br>');
}

var first_char = /\S/;
function capitalize(s) {
  return s.replace(first_char, function(m) { return m.toUpperCase(); });
}

function stop_record() {
  recognition.stop();
  $("#record").css("background-color","GoldenRod");  
}

function record(event) {
  if (recognizing) {
    recognition.stop();
    $("#record").css("background-color","GoldenRod");    
    return;
  }
  final_transcript = '';
  recognition.lang = 'en-US'
  recognition.start();
  ignore_onend = false;
  start_timestamp = event.timeStamp;
}

