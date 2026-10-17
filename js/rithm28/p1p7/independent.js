'use strict';
// Independent information-set minimax. Receipt records must predate decisions.
function solve(h,pattern,budget,certified=true){
 const worlds=[Array(h).fill(0),...Array.from({length:h},(_,i)=>Array.from({length:h},(_,j)=>+(i===j)))];
 const received=e=>pattern==='lag1'?e+1:pattern==='lag4'?e+4:pattern==='blackout'?h+5:pattern==='late'?(e===0?5:e+1):pattern==='reorder'?(e===0?4:e===1?2:e+2):NaN;
 for(let e=0;e<h;e++)if(received(e)<e+1)throw Error('receipt before publication');
 const observation=(t,w)=>certified?Array.from({length:h},(_,e)=>e).filter(e=>received(e)===t).map(e=>[e,w[e]]):[];
 const memo=new Map(),certificate=new Map();
 function rec(t,records,last,trained,spent){
  if(t===h)return records.every(([_,a,b])=>a===2&&b===2);
  const key=JSON.stringify([t,records,last,trained,spent]);if(memo.has(key))return memo.get(key);
  for(let target=0;target<2;target++)for(let boost=0;boost<=+(spent<budget);boost++){
   const switching=last!==2&&last!==target;
   const next=records.map(([i,a,b])=>{
    const cap=Math.max(0,1+boost-worlds[i][t]-+(switching&&trained===0));
    return target===0?[i,Math.min(2,a+cap),b]:[i,a,Math.min(2,b+cap)];
   });
   const groups=new Map();
   for(const r of next){const label=JSON.stringify(observation(t+1,worlds[r[0]]));
    if(!groups.has(label))groups.set(label,[]);groups.get(label).push(r);
   }
   if([...groups.values()].every(g=>rec(t+1,g,target,trained|+switching,spent+boost))){
    memo.set(key,true);certificate.set(key,[target,boost]);return true;
   }
  }
  memo.set(key,false);return false;
 }
 const won=rec(0,worlds.map((_,i)=>[i,0,0]),2,0,0);
 return {won,states:memo.size,certificate_nodes:certificate.size};
}
const expected={5:{lag1:1,lag4:1,reorder:1,late:1,blackout:2},6:{lag1:0,lag4:0,reorder:0,late:0,blackout:1}};
for(const h of [5,6])for(const [pattern,want] of Object.entries(expected[h])){
 const got=[0,1,2].find(b=>solve(h,pattern,b).won);
 if(got!==want)throw Error('independent mismatch');
 console.log(JSON.stringify({h,pattern,min_boost:got,...solve(h,pattern,got)}));
}
for(const h of [5,6]){
 const got=[0,1,2].find(b=>solve(h,'lag1',b,false).won);
 if(got!==(h===5?2:1))throw Error('uncertified signal used');
 console.log('uncertified',h,got);
}
