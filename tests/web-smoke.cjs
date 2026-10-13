/* Browser UI smoke tests without network or external packages. */
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const html = fs.readFileSync(path.join(__dirname, "../web/index.html"), "utf8");
const match = html.match(/<script>([\s\S]*?)<\/script>/i);
assert.ok(match, "inline simulator script must exist");
new vm.Script(match[1], {filename: "web/index.html"});

const defaults = {
  vk: '{"alpha":7,"beta":11,"gamma":5,"delta":3,"ic":[2,4],"mod":104729}',
  proof: '{"a":7,"b":11,"c":34626}', inputs: "[42]",
  primary: "29.4", secondary: "14.8", descriptor: "DISCORDANT_ANOMALY",
  task: "DEMO-001"
};
const elements = new Map();
for (const [id, value] of Object.entries(defaults)) elements.set(id, {value});
for (const id of ["verify", "audit", "tamper", "reset", "download", "status", "output", "critical"]) {
  if (!elements.has(id)) elements.set(id, {});
}
const $ = (id) => elements.get(id);
$("critical").checked = true;
for (const element of elements.values()) {
  element.addEventListener = function (name, fn) {
    assert.equal(name, "click");
    element.onClick = fn;
  };
}
const document = {getElementById: $, body: {appendChild() {}}, createElement() {return {click(){},remove(){}}}};
vm.runInNewContext(match[1], {document, Blob, URL, setTimeout, console});

$("verify").onClick();
assert.equal(JSON.parse($("output").textContent).is_valid, true, "known toy vector should match");
$("tamper").onClick();
assert.equal(JSON.parse($("output").textContent).is_valid, false, "altered public input must fail");
$("reset").onClick();
assert.equal(JSON.parse($("output").textContent).is_valid, true, "reset should restore valid vector");
$("vk").value = '{"alpha":7,"beta":11,"gamma":5,"delta":3,"ic":[2,4],"mod":9}';
$("verify").onClick();
assert.match($("status").textContent, /Input error/);
assert.equal($("download").disabled, true, "invalid results should not be downloadable");

$("audit").onClick();
let result = JSON.parse($("output").textContent);
assert.equal(result.overall_status, "CRITICAL_INTERVENTION_REQUIRED");
assert.equal(result.total_alerts, 3);
$("critical").checked = false;
$("primary").value = "10";
$("secondary").value = "4";
$("descriptor").value = "NOMINAL";
$("audit").onClick();
result = JSON.parse($("output").textContent);
assert.equal(result.overall_status, "NOMINAL_OPTIMAL");
assert.equal(result.total_alerts, 0);
$("primary").value = "NaN";
$("audit").onClick();
assert.match($("status").textContent, /Input error/);
console.log("Browser simulator smoke tests passed");
