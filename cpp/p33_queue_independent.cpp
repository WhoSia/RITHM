#include <iostream>
#include <vector>
#include <map>
#include <tuple>
#include <functional>
#include <cmath>
#include <stdexcept>
using namespace std;
// Independently enumerated simple-cycle means; not the Go/Karp algorithm.
// z, delayed-z, capped queue, rolling disturbance mask, parity controller.
using State=tuple<int,int,int,int,int>;
struct Edge{int to,cost;};
struct Answer{int states;double worst;bool safe;};
Answer check(int K,int B){
 vector<State> states;map<State,int> id;vector<vector<Edge>> arcs;
 auto put=[&](State s)->int{auto it=id.find(s);if(it!=id.end())return it->second;int n=(int)states.size();id[s]=n;states.push_back(s);arcs.push_back({});return n;};
 put({0,0,0,0,0});put({1,1,0,0,1});bool safe=true;
 for(size_t i=0;i<states.size();i++){
  auto [z,prev,q,h,m]=states[i];
  int d=m^z,cost=192+2*d+2*q;if(cost>192)safe=false;
  for(int w=0;w<=1;w++){
   if(__builtin_popcount((unsigned)h)+w>B)continue;
   int nh=K>1?(((h<<1)|w)&((1<<(K-1))-1)):0;
   int nq=max(0,min(3,q+2*d-1)),nz=z^1^w;
   int j=put({nz,z,nq,nh,m^1});arcs[i].push_back({j,cost});
  }
 }
 double best=-1.;vector<bool>seen(states.size());
 function<void(int,int,int,int)> dfs=[&](int root,int cur,int len,int sum){
  for(auto e:arcs[cur]){
   if(e.to==root)best=max(best,double(sum+e.cost)/double(len+1));
   else if(!seen[e.to]){seen[e.to]=true;dfs(root,e.to,len+1,sum+e.cost);seen[e.to]=false;}
  }
 };
 for(int i=0;i<(int)states.size();i++){seen[i]=true;dfs(i,i,0,0);seen[i]=false;}
 return {(int)states.size(),best,safe};
}
int main(){
 for(auto [k,b]:vector<pair<int,int>>{{3,0},{3,1},{5,1}}){
  Answer a=check(k,b);cout<<"K="<<k<<",B="<<b<<",states="<<a.states<<",worst="<<a.worst<<",safe="<<a.safe<<"\n";
 }
 if(fabs(check(3,1).worst-200.)>1e-9)throw runtime_error("independent-queue FAIL");
}
