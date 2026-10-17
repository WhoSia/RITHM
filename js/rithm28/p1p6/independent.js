'use strict';
function minBudget(H,lag){
 const worlds=[Array(H).fill(0),...Array.from({length:H},(_,i)=>Array.from({length:H},(_,j)=>+(i===j)))];
 function feasible(B){
  const memo=new Map();
  function decide(t,records,last,trained,spent){
   if(t===H)return records.every(([_,a,b])=>a===2&&b===2);
   const k=JSON.stringify([t,records,last,trained,spent]);
   if(memo.has(k))return memo.get(k);
   for(let who=0;who<2;who++)for(let boost=0;boost<=+(spent<B);boost++){
    const sw=last!==2&&last!==who;
    const next=records.map(([i,a,b])=>{
     const cap=Math.max(0,1+boost-worlds[i][t]-+(sw&&trained===0));
     return who===0?[i,Math.min(2,a+cap),b]:[i,a,Math.min(2,b+cap)];
    });
    const groups=new Map(),index=t+1-lag;
    for(const rec of next){const obs=index>=0?worlds[rec[0]][index]:-1;
     if(!groups.has(obs))groups.set(obs,[]);groups.get(obs).push(rec);
    }
    if([...groups.values()].every(g=>decide(t+1,g,who,trained|+sw,spent+boost))){memo.set(k,true);return true;}
   }
   memo.set(k,false);return false;
  }
  return decide(0,worlds.map((_,i)=>[i,0,0]),2,0,0);
 }
 return [0,1,2].find(feasible);
}
for(const H of [5,6])for(const lag of [1,2,3,4,100]){
 const x=minBudget(H,lag);
 console.log(JSON.stringify({H,lag,min_budget:x}));
 const expected=H===5?(lag===100?2:1):(lag===100?1:0);
 if(x!==expected)throw Error('independent mismatch');
}
