
$(document).ready(function() {
    sendCurrentLocation();
    var minutes = 5
    setInterval(() => {
        sendCurrentLocation();
    }, 1000 * 60 * minutes)  

    putBotMessage("Hello, it's me, the PDA for your buerro. Ask me anything.")

    $("#prompt_input").keypress(function(e) {
        if(e.which == 13) {
            processUserPrompt($("#prompt_input").val());
            $("#prompt_input").val("");
        }
    });

    $("#submit-btn").click(function () {
        processUserPrompt($("#prompt_input").val());
        $("#prompt_input").val("");
    });
})


