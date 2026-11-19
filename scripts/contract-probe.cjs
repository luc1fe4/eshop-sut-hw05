// Only sanitized evidence is written; credentials/tokens remain in memory.
const fs = require('fs');
const crypto = require('crypto');
async function main() {
 const email = `m5-probe-${crypto.randomUUID()}@example.invalid`;
 const initial = 'Aa1!' + crypto.randomBytes(12).toString('hex');
 const next = 'Bb2!' + crypto.randomBytes(12).toString('hex');
 const evidence = {time:new Date().toISOString(),timezone:'Asia/Ho_Chi_Minh',base:'http://127.0.0.1:3000',steps:[]};
 async function request(path,body,token) {
  const res = await fetch(evidence.base+path,{method:body?'POST':'GET',headers:{'Content-Type':'application/json',...(token?{Authorization:`Bearer ${token}`}:{})},...(body?{body:JSON.stringify(body)}:{})});
  const data = await res.json();
  evidence.steps.push({path,status:res.status,keys:Object.keys(data)});
  if(res.status!==200) throw new Error('Probe failed at '+path);
  return data;
 }
 const a = await request('/api/register',{name:'M5 Contract Probe',email,password:initial});
 const b = await request('/api/forgot-password',{email});
 evidence.reset_token = {type:typeof b.resetToken,length:b.resetToken.length,digits_only:/^\d+$/.test(b.resetToken)};
 await request('/api/reset-password',{email,resetToken:b.resetToken,newPassword:next});
 const d = await request('/api/login',{email,password:next});
 evidence.identity_matches = d.user.id === a.id && d.user.email === email;
 evidence.jwt_three_segments = d.token.split('.').length === 3;
 evidence.login_response_contains_password_field = Object.hasOwn(d.user,'password');
 const e = await request('/api/cart',null,d.token);
 evidence.cart = {is_array:Array.isArray(e),length:e.length,sanitized_body:e};
 fs.writeFileSync(process.argv[2],JSON.stringify(evidence,null,2));
 console.log('Sanitized contract evidence saved; no credentials printed.');
}
main().catch(()=>{console.error('Probe failed (contents redacted)');process.exitCode=1;});
