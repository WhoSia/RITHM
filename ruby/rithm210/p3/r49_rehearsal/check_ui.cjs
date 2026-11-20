// Execute the shipped UI's event handlers against HTTP and a minimal DOM.
const assert = require("node:assert/strict");
const { spawn, execFileSync } = require("node:child_process");
const fs = require("node:fs");
const { tmpdir } = require("node:os");
const path = require("node:path");
const { createInterface } = require("node:readline");
const { createContext, runInContext } = require("node:vm");
const { randomUUID } = require("node:crypto");

const python = process.env.PYTHON || "python";
const html = fs.readFileSync(path.join(__dirname, "r49_pilot.html"), "utf8");
const source = html.match(/<script>([\s\S]+)<\/script>/)[1];

function openUI(host, storage) {
  const elements = new Map([...html.matchAll(/<(\w+)\b[^>]*\bid="([^"]+)"[^>]*>/g)]
    .map(([raw, tag, id]) => [id, {
      tag, hidden: /\bhidden\b/.test(raw), disabled: false, textContent: "",
      addEventListener(name, handler) { this["on" + name] = handler; },
    }]));
  let downloaded;
  const context = createContext({
    document: {
      getElementById: id => elements.get(id),
      querySelectorAll: tag => [...elements.values()].filter(e => e.tag === tag),
      createElement() { return { click() {} }; },
    },
    localStorage: {
      getItem: key => storage.get(key) ?? null,
      setItem: (key, value) => storage.set(key, value),
      removeItem: key => storage.delete(key),
    },
    fetch: (url, options) => fetch(host + url, options),
    crypto: { randomUUID }, Blob,
    URL: { createObjectURL(blob) { downloaded = blob; return "local-download"; }, revokeObjectURL() {} },
    setTimeout() {},
  });
  runInContext(source, context);
  async function click(id) {
    const el = elements.get(id);
    assert.equal(el.disabled, false, id);
    await el.onclick();
    assert.equal(elements.get("alert").textContent, "");
  }
  return {
    elements, click,
    async start(start) {
      elements.get("start").value = String(start);
      elements.get("rounds").value = "5";
      await elements.get("config").onsubmit({ preventDefault() {} });
      assert.equal(elements.get("alert").textContent, "");
      assert.equal(elements.get("handoff").hidden, false);
    },
    async downloaded() { return downloaded.text(); },
  };
}

async function run(frame, start) {
  const scratch = fs.mkdtempSync(path.join(tmpdir(), "rithm-r49-"));
  const app = spawn(python, ["-u", "-c", [
    "from test_r49 import FixedDraws",
    "from r49_server import server",
    "from r49_store import Ledger",
    "import sys",
    "with server(Ledger(sys.argv[1], FixedDraws(sys.argv[2], -4))) as app:",
    " print(app.server_port)",
    " app.serve_forever()",
  ].join("\n"), path.join(scratch, "r49.sqlite3"), frame], {
    cwd: __dirname, stdio: ["ignore", "pipe", "inherit"],
  });
  try {
    const port = await new Promise((resolve, reject) => {
      const lines = createInterface({ input: app.stdout });
      const timer = setTimeout(() => reject(new Error("rehearsal server failed to start")), 4000);
      lines.once("line", line => { clearTimeout(timer); lines.close(); resolve(Number(line)); });
      app.once("error", error => { clearTimeout(timer); reject(error); });
      app.once("exit", code => { clearTimeout(timer); reject(new Error("server exited " + code)); });
    });
    const storage = new Map();
    const host = "http://127.0.0.1:" + port;
    let ui = openUI(host, storage);
    await ui.start(start);
    for (let i = 0; i < 2; i++) {
      await ui.click("open");
      await ui.click("routeA");
    }
    assert.equal(ui.elements.get("handoff").hidden, true);
    assert.equal(ui.elements.get("receipt").hidden, true);
    await ui.click("issue");
    const shown = ui.elements.get("amount").textContent;
    assert.match(shown, frame === "route" ? /^A 경로 보수 조정 -4점$/ : /^별도 실험 정산 -4점$/);

    ui = openUI(host, storage);
    await ui.click("resume");
    assert.equal(ui.elements.get("receipt").hidden, true);
    await ui.click("issue");
    assert.equal(ui.elements.get("amount").textContent, shown);
    await ui.click("ack");
    assert.equal(ui.elements.get("amount").textContent, "");
    assert.equal(ui.elements.get("handoff").hidden, false);
    for (let i = 0; i < 3; i++) {
      await ui.click("open");
      await ui.click("routeA");
    }
    await ui.click("export");
    const exported = path.join(scratch, "ui-export.json");
    fs.writeFileSync(exported, await ui.downloaded());
    const result = JSON.parse(fs.readFileSync(exported, "utf8"));
    const verified = JSON.parse(execFileSync(python, [path.join(__dirname, "r49_audit.py"), exported],
      { encoding: "utf8" }));
    assert.deepEqual(verified.settlement_order, [5, 6, 7, 8, 9]);
    assert.equal(verified.choices, 5);
    assert.equal(result.events.filter(e => e.type === "settlement_assigned").length, 1);
    assert.equal(result.events.filter(e => e.type === "settlement_issued").length, 1);
    return { start, frame, shown, ...verified, outcome: result.outcome };
  } finally {
    const exited = app.exitCode === null && app.signalCode === null
      ? new Promise(resolve => app.once("exit", resolve)) : Promise.resolve();
    app.kill();
    await exited;
    fs.rmSync(scratch, { recursive: true, force: true });
  }
}

(async () => {
  const runs = [await run("route", 5), await run("wallet", 4)];
  process.stdout.write(JSON.stringify(runs, null, 2) + "\n");
})().catch(error => { console.error(error); process.exitCode = 1; });
