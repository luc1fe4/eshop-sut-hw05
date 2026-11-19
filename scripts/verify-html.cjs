// Headless verification of exported HTML; not a desktop resource screenshot.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1118-904-0_26.1118.904.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/playwright');
const fs=require('fs');const path=require('path');const {pathToFileURL}=require('url');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const results=[];
 try {
  for(const folder of process.argv.slice(2)){
   const page=await browser.newPage({viewport:{width:1440,height:1000}});
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(pathToFileURL(path.resolve(folder,'dashboard.html')).href);
   await page.waitForTimeout(2000);
   const details=await page.evaluate(()=>({title:document.title,text:document.body.innerText.slice(0,5000),canvas:document.querySelectorAll('canvas').length,svg:document.querySelectorAll('svg').length}));
   await page.screenshot({path:path.join(folder,'dashboard-browser-check.png'),fullPage:true});
   const record={...details,errors,headless:true,note:'Actual exported HTML opened in headless Edge; not Task Manager desktop evidence'};
   fs.writeFileSync(path.join(folder,'html-verification.json'),JSON.stringify(record,null,2));
   results.push({folder,canvas:details.canvas,svg:details.svg,errors});await page.close();
  }
 } finally { await browser.close(); }
 console.log(JSON.stringify(results,null,2));
})().catch(e=>{console.error(e.message);process.exitCode=1;});
