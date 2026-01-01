<script setup lang="ts">
import { Terminal } from "@xterm/xterm";
import "@xterm/xterm/css/xterm.css";

const terminalRef = ref<HTMLDivElement | null>(null);
let ws: WebSocket;
let term: Terminal;

onMounted(() => {
  term = new Terminal({
    cursorBlink: true,
    fontSize: 14,
  });

  if (terminalRef.value) {
    term.open(terminalRef.value);
    term.write("Connecting...\r\n");
  }

  let protocol = window.location.protocol;
  ws = new WebSocket(
    `${protocol == "https" ? "wss" : "ws"}://${window.location.host}/_ws`,
  );

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

  term.onData((data) => {
    ws.send(
      JSON.stringify({
        type: "command",
        data,
      }),
    );
  });
});

onBeforeUnmount(() => {
  ws?.close();
  term?.dispose();
});
</script>

<template>
  <div class="terminal-wrapper">
    <div ref="terminalRef" class="terminal"></div>
  </div>
</template>

<style scoped></style>
