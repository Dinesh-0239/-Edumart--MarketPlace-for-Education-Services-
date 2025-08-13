document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-box");
    const messageInput = document.getElementById("message-input");
    const sendButton = document.getElementById("send-button");
    const chatForm = document.getElementById("chat-form");
    const bookingId = chatBox.dataset.bookingId;
    const currentUser = chatBox.dataset.currentUser;
    const receiverId = chatBox.dataset.receiverId;
    let chatSocket;

    function connectWebSocket() {
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        chatSocket = new WebSocket(`${protocol}://${window.location.host}/ws/chat/${bookingId}/`);

        chatSocket.onopen = function () {
            console.log("WebSocket connected.");
        };

        chatSocket.onmessage = function (event) {
            const data = JSON.parse(event.data);
            const isSender = data.sender === currentUser; // ✅ Check sender
            appendMessage(data.message, data.timestamp, isSender);
        };

        chatSocket.onclose = function (event) {
            console.log("WebSocket disconnected.", event);
            setTimeout(connectWebSocket, 3000); // Attempt to reconnect after 3 seconds
        };

        chatSocket.onerror = function (error) {
            console.error("WebSocket error:", error);
            chatSocket.close();
        };
    }

    function appendMessage(message, timestamp, isSender) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("chat-message", isSender ? "sent" : "received"); // ✅ Sender/Receiver check
        messageDiv.innerHTML = `
            <p class="message-text">${message}</p>
            <span class="timestamp">${timestamp}</span>
        `;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    chatForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const message = messageInput.value.trim();
        if (message !== "" && receiverId) {
            chatSocket.send(JSON.stringify({
                message: message,
                receiver_id: receiverId
            }));
            messageInput.value = "";
        } else {
            console.error("Message is empty or receiver ID is missing!");
        }
    });

    chatBox.scrollTop = chatBox.scrollHeight;
    connectWebSocket();
});
