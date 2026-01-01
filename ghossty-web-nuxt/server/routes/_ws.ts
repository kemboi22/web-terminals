import * as pty from "node-pty";
import * as os from "node:os";

const shell = os.platform() === "win32" ? "powershell.exe" : "bash";

const ptys = new Map<string, pty.IPty>();

export default defineWebSocketHandler({
  open(peer) {
    console.log("Connection opened", peer.id);

    const ptyProcess = pty.spawn(shell, [], {
      name: "xterm-color",
      cols: 80,
      rows: 24,
      cwd: process.env.HOME,
      env: process.env,
    });

    ptys.set(peer.id, ptyProcess);

    ptyProcess.onData((data) => {
      console.log("PTY Process Data", data);
      peer.send(
        JSON.stringify({
          type: "data",
          data,
        }),
      );
    });
  },

  message(peer, message) {
    const ptyProcess = ptys.get(peer.id);
    if (!ptyProcess) return;

    const data = JSON.parse(message.text());

    if (data.type === "command") {
      ptyProcess.write(data.data);
    }

    if (data.type === "resize") {
      ptyProcess.resize(data.cols, data.rows);
    }
  },

  close(peer) {
    console.log("Connection closed", peer.id);

    const ptyProcess = ptys.get(peer.id);
    ptyProcess?.kill();
    ptys.delete(peer.id);
  },

  error(peer, error) {
    console.error("WS error", peer.id, error);

    const ptyProcess = ptys.get(peer.id);
    ptyProcess?.kill();
    ptys.delete(peer.id);
  },
});
