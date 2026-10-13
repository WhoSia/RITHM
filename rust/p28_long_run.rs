//! P28 std-only Rust exact finite-horizon counterfactual response envelopes.
//! Input: same verified 24-row original S2-derived compact routes, read-only.
//! This is AUTHORED, but not compiled/tested in the current container (rustc absent).
//! Alternative independent future executable; no claim of causal advice effects.
use std::{collections::BTreeMap,env,fs};
const M:usize=1<<12;
const INF:i32=1000000000;
#[derive(Clone)]
struct Panel{routes:[[i32;12];20],z:[i32;20]}
fn cost(n1:i32,n2:i32,z:i32)->i32{264-24*n1-9*n2+2*n1*n1+2*n1*n2+n2*n2+19*z*n2}
fn hex_to_240_trits(s:&str)->Result<[i32;240],String>{
 let mut hex:Vec<u32>=s.chars().map(|c|c.to_digit(16).ok_or(format!("not hex: {c}"))).collect::<Result<_,_>>()?;
 let mut seq=[0i32;240];
 for i in (0..240).rev(){let mut rem=0u32;for d in &mut hex{let v=rem*16+*d;*d=v/3;rem=v%3;}seq[i]=rem as i32+1;}
 if hex.iter().any(|&v|v!=0){return Err("base3 source overflow".into());}Ok(seq)
}
fn load(path:&str)->Result<Vec<Panel>,String>{
 let text=fs::read_to_string(path).map_err(|e|e.to_string())?;let mut lines=text.lines();
 let header=lines.next().ok_or("empty source")?;
 if header!="session,group,stage,info,choices_base3_hex,group_stage_total_cost,incident_20_bits_hex"{return Err("wrong source schema".into());}
 let mut all=Vec::new();
 for line in lines{let c:Vec<&str>=line.split(',').collect();if c.len()!=7{return Err("bad source row".into());}
  let seq=hex_to_240_trits(c[4])?;
  let mut routes=[[0i32;12];20];for t in 0..20{for j in 0..12{routes[t][j]=seq[t*12+j];}}
  let bits=u32::from_str_radix(c[6],16).map_err(|e|e.to_string())?;
  if bits.count_ones()!=4{return Err("wrong 4/20 original incidence quota".into());}
  let mut z=[0;20];for t in 0..20{z[t]=((bits>>(19-t))&1) as i32;}
  all.push(Panel{routes,z});
 }
 if all.len()!=24{return Err("need 24 original panels".into());}Ok(all)
}
fn direction(old:i32,z:i32,policy:&str)->i32{match policy{
 "incident_avoid"=>if z==1&&old==2{-1}else{0},
 "state_direction"=>if z==1&&old==2{-1}else if z==0&&old==3{1}else{0},
 "unrestricted"=>if old==2{-1}else if old==3{1}else{0},_=>panic!("unknown policy")}}
fn solve(p:&Panel,policy:&str)->(BTreeMap<u32,(i32,i32)>,(i32,i32),i32){
 let mut low=vec![INF;M];let mut high=vec![-INF;M];low[0]=0;high[0]=0;
 let(mut rectlow,mut recthigh,mut opportunities)=(0,0,0);
 for t in 0..20{
  let n1=p.routes[t].iter().filter(|&&x|x==1).count() as i32;
  let n2=p.routes[t].iter().filter(|&&x|x==2).count() as i32;
  let z=p.z[t];let base=cost(n1,n2,z);
  let mut nextlo=low.clone();let mut nexthi=high.clone();let mut rowlow=0;let mut rowhigh=0;
  for j in 0..12{
   let dir=direction(p.routes[t][j],z,policy);if dir==0{continue;}opportunities+=1;
   let gain=base-cost(n1,n2+dir,z);rowlow=rowlow.min(gain);rowhigh=rowhigh.max(gain);let bit=1usize<<j;
   for mask in 0..M{if mask&bit!=0||low[mask]==INF{continue;}
      let nx=mask|bit;nextlo[nx]=nextlo[nx].min(low[mask]+gain);nexthi[nx]=nexthi[nx].max(high[mask]+gain);
   }
  }
  rectlow+=rowlow;recthigh+=rowhigh;low=nextlo;high=nexthi;
 }
 let mut vals=BTreeMap::new();for b in [0,1,2,4,8,12]{let(mut mn,mut mx)=(0,0);for mask in 0..M{
  if mask.count_ones()>b||low[mask]==INF{continue;}mn=mn.min(low[mask]);mx=mx.max(high[mask]);}
  vals.insert(b,(mn,mx));}
 (vals,(rectlow,recthigh),opportunities)
}
fn main()->Result<(),String>{
 let a:Vec<String>=env::args().collect();if a.len()!=2{return Err("usage: p28_rust <24-row original compact routes CSV>".into());}
 let panels=load(&a[1])?;println!("policy,B,lower_total,upper_total,independent_lower,independent_upper,eligible_events");
 for policy in ["incident_avoid","state_direction","unrestricted"]{
  let mut sum:BTreeMap<u32,(i32,i32)>=BTreeMap::new();let(mut rl,mut ru,mut opp)=(0,0,0);
  for p in &panels{let(vals,(l,u),e)=solve(p,policy);rl+=l;ru+=u;opp+=e;
   for (b,(l,u)) in vals{let entry=sum.entry(b).or_insert((0,0));entry.0+=l;entry.1+=u;}}
  for (b,(l,u)) in sum{println!("{policy},{b},{l},{u},{rl},{ru},{opp}");}
 }
 Ok(())
}
#[cfg(test)]mod tests{use super::*;
 #[test]fn incident_single_switch_beneficial(){for n1 in 0..=12{for n2 in 1..=(12-n1){assert!(cost(n1,n2,1)>cost(n1,n2-1,1));}}}
 #[test]fn known_base3(){let x=hex_to_240_trits("0").unwrap();assert!(x.iter().all(|&v|v==1));}
 #[test]fn subject_budget_blocks_repeat(){let mut p=Panel{routes:[[1;12];20],z:[0;20]};p.routes[0][0]=2;p.routes[1][0]=2;p.z[0]=1;p.z[1]=1;let(b,rect,_) = solve(&p,"incident_avoid");assert_eq!(b[&12],(0,33));assert_eq!(rect,(0,66));}
}
