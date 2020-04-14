function putUserMessage(message) {
    var container = $(".bubblecontainer")
    container.append(generateChatBubble(false, message));

    container[0].scrollTop = container[0].scrollHeight
}

function putBotMessage(message) {
    if (message != "") {
        if (md_converter) {
            html = md_converter.makeHtml(message);
        }

        $('#submit-btn').val('Send');
        $('#loader').hide(100);

        var container = $(".bubblecontainer")
        container.append(generateChatBubble(true, html));

        speak();
        container[0].scrollTop = container[0].scrollHeight
        $('#prompt_input').focus();
    }
}


function processUserPrompt(prompt) {
    //Send to backend with async promise or something
    putUserMessage(prompt);
    getCurrentLocation(location => {
        return fetch('/api/message', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                   message: prompt,
                   'location': location
                })
            })
        .then(async response => {

            if (!response.ok) {

              message = undefined
              try {
                resp = await response.json()
                message = resp.error.message;
              } catch(e) {}
              if(message) {
                throw new Error('Bad server response: ', message);
              } else {
                throw new Error('Bad status code from server.');
              }

              putBotMessage("Server communication failed.");
            }

            return response.json();
        })
        .then(function(responseData) {
            if (!(responseData.success && responseData.data)) {
              throw new Error('Bad response from server.');
              putBotMessage("Server communication failed.");
            }

            putBotMessage(responseData.data.message);
        });
    });
}


function generateChatBubble(bot, text) {
    if(bot) {
        return "<div class='card bubble bubble-bot'><div class='card-body'>" + text + "</div></div>";
    } else {
        return "<div class='card bubble bubble-user'><div class='card-body'>" + text + "</div></div>";
    }
}
