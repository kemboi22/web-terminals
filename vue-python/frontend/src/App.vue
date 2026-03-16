<script setup lang="ts">
import { init, Terminal } from "ghostty-web";
import { onMounted, onBeforeUnmount, ref } from "vue";

const terminalRef = ref<HTMLDivElement | null>(null);

let term: Terminal;
let ws: WebSocket;

onMounted(async () => {
  const server = "localhost:8765";

  await init();

  term = new Terminal({
    fontSize: 14,
    cursorBlink: true,
    cols: 80,
    rows: 40,
  });

  if (terminalRef.value) {
    term.open(terminalRef.value);
    term.write("Welcome to Ghostty web\r\n");
    term.write("Connecting...\r\n");
  }

  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${protocol}://${server}`);

  ws.onopen = () => {
    term.write("Connected\r\n");
  };

  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);

    if (msg.type === "data") {
      term.write(msg.data);
    }
  };

  ws.onerror = () => {
    term.write("\r\nWebSocket error\r\n");
  };

  ws.onclose = () => {
    term.write("\r\nConnection closed\r\n");
  };

  term.onData((data) => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(
        JSON.stringify({
          type: "command",
          data,
        }),
      );
    }
  });

  // Close websocket if page refreshes
  window.addEventListener("beforeunload", () => {
    ws.close();
  });
});

onBeforeUnmount(() => {
  if (ws) ws.close();
});
</script>
<template>
  <div><p>Simple web terminal implimntation using ghossty web</p></div>
  <div><div ref="terminalRef" /></div>
</template>
