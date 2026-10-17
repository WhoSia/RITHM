'use strict';
// P1-P8 independent JavaScript minimax, no shared Ruby implementation.
function minimum(h,kind){
 const worlds=[Array(h).fill(0),...Array.from({length:h},(_,i)=>Array.from({length:h},(_,j)=>+(i===j)))];
 const records=Array.from({length:h},(_,i)=>({id:i,declared:i,p:i+1,r:i+1,trust:true}));
 if(kind==='duplicate')records.push({...records[0]});
 if(kind==='missing')records[0].r=h+100;
 if(kind==='untrusted')records.forEach(x=>x.trust=false);
 if(kind==='mislabel')records[0].declared=h+10;
 if(kind==='reorder'){records[0].r=4;records[1].r=2}
 if(records.some(x=>x.r<x.p||x.p<x.id+1))throw Error('clock violation');
 const observe=(t,w)=>records.filter(x=>x.trust&&x.r===t&&x.declared===x.id)
   .map(x=>[x.id,w[x.id]]).sort((a,b)=>a[0]-b[0]).filter((x,i,a)=>i===0||x[0]!==a[i-1][0]);
 function win(budget){
  const memo=new Map();
  function go(t,items,last,trained,used){
   if(t===h)return items.every(([_,a,b])=>a===2&&b===2);
   const key=JSON.stringify([t,items,last,trained,used]);if(memo.has(key))return memo.get(key);
   for(let who=0;who<2;who++)for(let boost=0;boost<=+(used<budget);boost++){
    const sw=last!==2&&last!==who;
    const next=items.map(([i,a,b])=>{const cap=Math.max(0,1+boost-worlds[i][t]-+(sw&&trained===0));return who===0?[i,Math.min(2,a+cap),b]:[i,a,Math.min(2,b+cap)]});
    const groups=new Map();
    for(const r of next){const label=JSON.stringify(observe(t+1,worlds[r[0]]));if(!groups.has(label))groups.set(label,[]);groups.get(label).push(r)}
    if([...groups.values()].every(g=>go(t+1,g,who,trained|+sw,used+boost))){memo.set(key,true);return true}
   }
   memo.set(key,false);return false;
  }
  return go(0,worlds.map((_,i)=>[i,0,0]),2,0,0);
 }
 return [0,1,2].find(win);
}
const expected={5:{clean:1,duplicate:1,missing:1,untrusted:2,mislabel:1,reorder:1},6:{clean:0,duplicate:0,missing:0,untrusted:1,mislabel:0,reorder:0}};
for(const [h,scenarios] of Object.entries(expected))for(const [s,want] of Object.entries(scenarios)){
 const value=minimum(+h,s);if(value!==want)throw Error('P1-P8 independent value mismatch '+h+'/'+s);
 console.log('PASS',h,s,value);
}