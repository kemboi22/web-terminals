<script setup lang="ts">
import { init, Terminal } from "ghostty-web";

const terminalRef = ref<HTMLDivElement | null>(null);
let term: Terminal;
let ws: WebSocket;

onMounted(async () => {
  await init();
  term = new Terminal({
    fontSize: 14,
    cursorBlink: true,
    cols: 80,
    rows: 40,
  });

  if (terminalRef.value) {
    term.open(terminalRef.value);
    term.write("Welcome to Ghostty web \r \n");
    term.write("Connecting.... \r\n");
  }
  let protocol = window.location.protocol;
  ws = new WebSocket(
    `${protocol == "https" ? "wss" : "ws"}://${window.location.host}/_ws`,
  );

  ws.onopen = (e) => {
    term.write("Connected\r\n");
  };

  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    if (msg.type == "data") {
      term.write(msg.data);
    }
  };

  ws.onerror = () => {
    term.write("\r\nWebSocket error \r\n");
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
</script>
<template>
  <div>
    <NuxtRouteAnnouncer />
    <div ref="terminalRef" />
  </div>
</template>
