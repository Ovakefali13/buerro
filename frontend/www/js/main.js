$(document).ready(function() {
    sendCurrentLocation();
    var minutes = 5
    setInterval(() => {
        sendCurrentLocation();
    }, 1000 * 60 * minutes)  

    putBotMessage("Hello, it's me, the PDA for your buerro. Ask me _anything_.")

    $("#prompt_input").keypress(function(e) {
        if(e.which == 13) {
            e.preventDefault();
            if(!$('#submit-btn').prop('disabled')) {
                stop_record()    
                processUserPrompt($("#prompt_input").val());
                $('#loader').show(100);
                $('#submit-btn').val('Loading');
                $('#submit-btn').prop('disabled',true);
                $("#prompt_input").val("");
            }
        }
    });

    $('#submit-btn').prop('disabled',true);
    $("#submit-btn").click(function () {        
        stop_record()        
        processUserPrompt($("#prompt_input").val());        
        $('#loader').show(100);
        $('#submit-btn').val('Loading');
        $('#submit-btn').prop('disabled',true);
        $("#prompt_input").val("");
    });
    
    $("#prompt_input").on('change input', function() {
        if (!$.trim($("#prompt_input").val())) {
            $('#submit-btn').prop('disabled', true)
        } else {
            $('#submit-btn').prop('disabled', false)
        }
    })

    $('#prompt_input').focus();

    navigator.serviceWorker.addEventListener('message', event => {
        if(event.data.options.data) {
            if(event.data.options.data.message) {
                putBotMessage(event.data.options.data.message);
            }
        }
    });
})

