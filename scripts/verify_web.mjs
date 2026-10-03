import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const nodes=new Map();
const defaults={capacity:'10',success:'5',margin:'30',cost:'5',incentive:'10'};
const document={title:'',getElementById(id){if(!nodes.has(id))nodes.set(id,{innerHTML:'',textContent:'',value:defaults[id]||'',addEventListener(){}});return nodes.get(id);},addEventListener(){}};
const sandbox={console,document,location:{hash:''},addEventListener(){},AbortController};sandbox.window=sandbox;
const context=vm.createContext(sandbox);
for(const name of ['data.js','app.js'])vm.runInContext(fs.readFileSync(path.join(root,'web',name),'utf8'),context,{filename:name});
const pages=['overview','health','cohorts','survival','risk','value','priority','budget','customer'];
for(const page of pages){sandbox.location.hash='#'+page;if(page==='customer')document.getElementById('customer-id').value=sandbox.RETENTION_DATA.customer_scores[0].customer;assert.equal(sandbox.render(),page);assert.match(document.getElementById('content').innerHTML,/<h1>/);assert(!document.getElementById('content').innerHTML.includes('NaN'));}
const rows=sandbox.calculateScenario({capacity:.1,success:.05,cost:5,incentive:10,margin:.3});
const csv=fs.readFileSync(path.join(root,'artifacts/tables/simulation.csv'),'utf8').trim().split(/\r?\n/);const keys=csv.shift().split(',');const records=csv.map(line=>Object.fromEntries(line.split(',').map((value,i)=>[keys[i],value])));
for(const [name,strategy] of [['Churn risk','risk'],['Customer value','value'],['Risk × value','risk_value']]){const reference=records.find(r=>r.strategy===strategy&&+r.capacity===.1&&+r.contact_cost===5&&+r.assumed_success===.05&&+r.incentive===10);const actual=rows.find(r=>r.strategy===name);assert(Math.abs(actual.net-+reference.scenario_net_contribution)<1e-8);assert(Math.abs(actual.retained-+reference.scenario_retained_revenue)<1e-8);assert.equal(actual.contacts,36);}
assert(rows.every(r=>r.net<0));
for(const input of [{capacity:0,success:.05,cost:5,incentive:10,margin:.3},{capacity:.1,success:NaN,cost:5,incentive:10,margin:.3}])assert.throws(()=>sandbox.calculateScenario(input));
assert.throws(()=>sandbox.explore('not-a-customer'));
const selected=sandbox.RETENTION_DATA.customer_scores[0];sandbox.explore(selected.customer);document.getElementById('customer-id').value=selected.customer;assert.equal(sandbox.updateCustomer().customer,selected.customer);
for(const asset of ['style.css','app.js','data.js','figures/calibration.png','figures/cohort_retention.png','figures/survival.png'])assert(fs.existsSync(path.join(root,'web',asset)));
const result={page_render_checks:pages.length,scenario_parity:'PASS',invalid_input_checks:'PASS',customer_lookup:'PASS',local_assets:'PASS',webmcp_browser_validation:'Unavailable: no supported browser context is provided; optional tool registration was source reviewed.'};
fs.writeFileSync(path.join(root,'reports/web_validation.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));
