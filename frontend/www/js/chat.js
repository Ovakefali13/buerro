
function putUserMessage(message) {
    var container = $(".bubblecontainer")
    container.append(generateChatBubble(false, message));

    container[0].scrollTop = container[0].scrollHeight
}

function putBotMessage(message) {
    var container = $(".bubblecontainer")
    container.append(generateChatBubble(true, message));

    container[0].scrollTop = container[0].scrollHeight
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
        .then(function(response) {
            if (!response.ok) {
              console.error(response.json())
              throw new Error('Bad status code from server.');
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
