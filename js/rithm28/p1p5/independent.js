'use strict';
// Independent implementation of P1-P5 controller/adversary timing contract.
function adaptive(H,B){
 const memo=new Map();
 function v(t,a,b,last,used,trained,spent){
  if(t===H)return Number(a===2&&b===2);
  const key=[t,a,b,last,used,trained,spent].join(',');
  if(memo.has(key))return memo.get(key);
  let best=0;
  for(let who=0;who<2;who++)for(let boost=0;boost<=(spent<B?1:0);boost++){
   let worst=1;
   for(let w=0;w<=(used===0?1:0);w++){
    const sw=last!==2&&last!==who;
    const cap=Math.max(0,1+boost-w-Number(sw&&trained===0));
    const x=who===0?Math.min(2,a+cap):a,y=who===1?Math.min(2,b+cap):b;
    worst=Math.min(worst,v(t+1,x,y,who,used|w,trained|Number(sw),spent+boost));
   }
   best=Math.max(best,worst);
  }
  memo.set(key,best);return best;
 }
 return {value:v(0,0,0,2,0,0,0),states:memo.size};
}
function openLoop(H,B){
 let plans=0,winners=0;
 const scenarios=[Array(H).fill(0),...Array.from({length:H},(_,i)=>Array.from({length:H},(_,j)=>Number(i===j)))];
 function visit(plan,spent){
  if(plan.length===H){
   plans++;
   const safe=scenarios.every(s=>{
    let a=0,b=0,last=2,trained=0;
    plan.forEach(([who,boost],t)=>{
     const sw=last!==2&&last!==who;
     const cap=Math.max(0,1+boost-s[t]-Number(sw&&trained===0));
     if(who===0)a=Math.min(2,a+cap);else b=Math.min(2,b+cap);
     trained|=Number(sw);last=who;
    });
    return a===2&&b===2;
   });
   if(safe)winners++;return;
  }
  for(let who=0;who<2;who++)for(let add=0;add<=(spent<B?1:0);add++)visit([...plan,[who,add]],spent+add);
 }
 visit([],0);return {value:Number(winners>0),plans,winners};
}
for(const H of [5,6])for(const B of [0,1,2]){
 const a=adaptive(H,B),o=openLoop(H,B);
 console.log(JSON.stringify({H,B,adaptive:a,open_loop:o}));
}
if(adaptive(5,1).value!==1||openLoop(5,1).value!==0||openLoop(5,2).value!==1)throw Error('replay failure');
