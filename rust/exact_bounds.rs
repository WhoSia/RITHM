//! Rust P27 core: exact integer welfare envelopes of originally observed group states.
//! Requires only rustc (no crates). Runtime verification requires a machine with Rust installed.
//! Not a real policy or individual-attention experiment.
use std::env;
use std::fs;
#[derive(Copy,Clone)]
struct State { n1:i32, n2:i32, n3:i32, z:i32 }
fn cost(n1:i32,n2:i32,z:i32)->i32 {264-24*n1-9*n2+2*n1*n1+2*n1*n2+n2*n2+19*z*n2}
fn bounds(s:State,k:i32,policy:usize)->(i32,i32){
    let q=s.n2+s.n3;
    let (mut left,mut right)=(s.n2,s.n2);
    match policy {
        0=>{left=(s.n2-k).max(0);right=(s.n2+k).min(q);},
        1=>{if s.z==1 {left=(s.n2-k).max(0);}},
        2=>{if s.z==1 {left=(s.n2-k).max(0);} else {right=(s.n2+k).min(q);}},
        _=>panic!("unsupported policy"),
    }
    let (mut lo,mut hi)=(0,0);
    let base=cost(s.n1,s.n2,s.z);
    for x in left..=right {
        let improvement=base-cost(s.n1,x,s.z);
        lo=lo.min(improvement);hi=hi.max(improvement);
    }
    (lo,hi)
}
fn source(path:&str)->Vec<State>{
    let bytes=fs::read_to_string(path).expect("group states source file");
    let mut lines=bytes.lines();
    assert_eq!(lines.next().expect("header"),"session,group,stage,info,round,n1,n2,n3,incident,theoretical_group_cost");
    let mut states=Vec::new();
    for line in lines {
        let c:Vec<&str>=line.split(',').collect();assert_eq!(c.len(),10);
        let num=|i:usize|c[i].parse::<i32>().expect("integer field");
        let s=State{n1:num(5),n2:num(6),n3:num(7),z:num(8)};
        assert!(s.n1+s.n2+s.n3==12&&s.z>=0&&s.z<=1);
        assert_eq!(cost(s.n1,s.n2,s.z),num(9));
        states.push(s);
    }
    assert_eq!(states.len(),480);
    states
}
fn main(){
    let args:Vec<String>=env::args().collect();assert_eq!(args.len(),2,"rust bounds.rs derived_states.csv");
    let data=source(&args[1]);
    println!("scheme,k,N,both,benefit,harm,mean_lower,mean_upper");
    for (policy, name) in ["unrestricted","incident_avoid","state_direction"].iter().enumerate() {
        for k in 0..=2 {
            let (mut lo,mut hi,mut both,mut pos,mut neg)=(0_i64,0_i64,0,0,0);
            for &s in &data {
                let (a,b)=bounds(s,k,policy);
                lo+=a as i64;hi+=b as i64;
                if a<0&&b>0 {both+=1;}
                if b>0{pos+=1;}
                if a<0{neg+=1;}
            }
            println!("{},{},{},{},{},{},{:.14},{:.14}",name,k,data.len(),both,pos,neg,lo as f64/data.len() as f64,hi as f64/data.len() as f64);
        }
    }
}
#[cfg(test)]
mod tests {
  use super::*;
  #[test] fn incident_avoid_has_no_harm_in_12_driver_network(){
    for n1 in 0..=12 {for n2 in 0..=12-n1{
      let s=State{n1,n2,n3:12-n1-n2,z:1};
      for k in 0..=2 {let (a,_)=bounds(s,k,1);assert_eq!(a,0);}
    }}
  }
  #[test] fn baseline_and_one_switch_exact(){
    let s=State{n1:4,n2:4,n3:4,z:0};
    assert_eq!(cost(s.n1,s.n2,s.z),212);
    assert_eq!(bounds(s,1,0),(-8,6));
  }
}
