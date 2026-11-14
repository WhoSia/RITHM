const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");

const html = fs.readFileSync(path.join(__dirname, "r42_pilot.html"), "utf8");
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];

async function run(signal, marker, blocks) {
  const nodes = new Map();
  const payloads = [];
  const document = {
    getElementById(id) {
      if (!nodes.has(id)) nodes.set(id, {
        hidden: id !== "setup",
        callbacks: {},
        addEventListener(event, callback) { this.callbacks[event] = callback; },
      });
      return nodes.get(id);
    },
    createElement() { return {click() {}}; },
  };
  const get = id => document.getElementById(id);
  vm.runInNewContext(script, {
    document, Blob, performance, setTimeout: action => action(),
    URL: {createObjectURL(blob) { payloads.push(blob); return "blob:mock"; }, revokeObjectURL() {}},
  });
  for (const [id, value] of Object.entries({seed: "42", initial: "5", signal, marker, horizon: blocks})) {
    get(id).value = value;
  }
  get("config").callbacks.submit({preventDefault() {}});
  for (let i = 0; i < blocks*6; i++) {
    assert.equal(get("handoff").hidden, false);
    get("ready").callbacks.click();
    const marks = ["mark-a", "mark-b"].filter(id => get(id).textContent === "현재 경로").length;
    assert.equal(marks, Number(marker === "on"));
    assert.match(get("current").textContent, /[AB]$/);
    get("b").callbacks.click();
    get("b").callbacks.click(); // late duplicate click cannot commit a second action
  }
  assert.equal(get("end").hidden, false);
  get("export").callbacks.click();
  const result = JSON.parse(await payloads[0].text());
  assert.equal(result.events.length, blocks*6);
  assert.equal(result.summaries[0].end_A, 0);
  assert.equal(result.summaries[0].hit_then_lost, true);
  for (let block = 1; block <= blocks; block++) {
    const rows = result.events.filter(event => event.block === block);
    assert.deepEqual(rows.map(row => row.seat).sort(), [1, 2, 3, 4, 5, 6]);
    for (const row of rows) {
      assert.equal(row.disclosed_A, signal === "live" ? row.actual_A_before : rows[0].actual_A_before);
    }
  }
  return result;
}

(async () => {
  const fixed = await run("frozen", "off", 1);
  const live = await run("live", "on", 5);
  await run("live", "off", 39);
  assert.deepEqual(fixed.initialRoutes, live.initialRoutes);
  assert.deepEqual(fixed.events.map(row => row.seat), live.events.slice(0, 6).map(row => row.seat));
  console.log("3 rehearsal logic runs passed (1, 5, 39 blocks)");
})().catch(error => {console.error(error); process.exitCode = 1;});
