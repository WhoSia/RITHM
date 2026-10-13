// Independent C++17 reconstruction of P28 person's finite one-change-over-20-rounds DP.
// Scientific limit: counterfactual response is hypothetical on frozen observed route histories.
#include <algorithm>
#include <array>
#include <bitset>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <map>
#include <boost/multiprecision/cpp_int.hpp>
using namespace std;
using boost::multiprecision::cpp_int;
struct Panel {string session;int group,stage,info;array<array<int,12>,20> r;array<int,20> z;};
struct Edge {int low=0,high=0;};
int network(int n1,int n2,int z){return 264-24*n1-9*n2+2*n1*n1+2*n1*n2+n2*n2+19*z*n2;}
vector<string> split(const string&s,char delim=','){istringstream ss(s);string tok;vector<string>parts;while(getline(ss,tok,delim))parts.push_back(tok);return parts;}
vector<Panel> read(const string& file) {
 ifstream fin(file);if(!fin)throw runtime_error("cannot open source");string line;getline(fin,line);auto h=split(line);if(h.size()!=7 || h[0]!="session" || h[4]!="choices_base3_hex")throw runtime_error("incorrect source schema");
 vector<Panel>out;while(getline(fin,line)){
  auto cols=split(line);if(cols.size()!=7)throw runtime_error("malformed panel");Panel p{};p.session=cols[0];p.group=stoi(cols[1]);p.stage=stoi(cols[2]);p.info=stoi(cols[3]);
  cpp_int number=0;for(char c:cols[4]){int d=(c>='0'&&c<='9')?c-'0':(c>='a'&&c<='f')?c-'a'+10:-1;if(d<0)throw runtime_error("bad hex");number*=16;number+=d;}
  for(int t=19;t>=0;--t)for(int person=11;person>=0;--person){cpp_int rem=number%3;number/=3;p.r[t][person]=int(rem)+1;}
  if(number!=0)throw runtime_error("overflow");
  unsigned long bits=stoul(cols[6],nullptr,16);
  if(__builtin_popcountl(bits)!=4)throw runtime_error("bad accident quota");
  for(int t=0;t<20;t++)p.z[t]=(bits>>(19-t))&1;
  out.push_back(p);
 }
 if(out.size()!=24)throw runtime_error("not 24 source panels");
 return out;
}
int direction(int original,int shock,const string&policy){if(policy=="incident_avoid")return shock==1&&original==2?-1:0;if(policy=="state_direction")return shock==1&&original==2?-1:(shock==0&&original==3?1:0);if(policy=="unrestricted")return original==2?-1:original==3?1:0;throw runtime_error("bad policy");}
struct Result {map<int,Edge> clipped;Edge independent;int eligible=0;};
Result solve(const Panel&p,const string&policy){constexpr int M=1<<12,INF=1000000000;vector<int>mini(M,INF),maxi(M,-INF);mini[0]=maxi[0]=0;Edge rect{};int elig=0;
 for(int t=0;t<20;t++){
  int n1=0,n2=0;for(int r:p.r[t]){n1+=r==1;n2+=r==2;}int base=network(n1,n2,p.z[t]);
  vector<pair<int,int>> actions;int minstep=0,maxstep=0;
  for(int person=0;person<12;person++){int d=direction(p.r[t][person],p.z[t],policy);if(!d)continue;elig++;int gain=base-network(n1,n2+d,p.z[t]);actions.emplace_back(person,gain);minstep=min(minstep,gain);maxstep=max(maxstep,gain);}
  rect.low+=minstep;rect.high+=maxstep;
  vector<int>newmin=mini,newmax=maxi; // explicit no response
  for(auto [person,gain]:actions){int bit=1<<person;
    for(int mask=0;mask<M;mask++){if((mask&bit)||mini[mask]==INF)continue;int nxt=mask|bit;newmin[nxt]=min(newmin[nxt],mini[mask]+gain);newmax[nxt]=max(newmax[nxt],maxi[mask]+gain);}
  }
  mini.swap(newmin);maxi.swap(newmax);
 }
 Result output;output.independent=rect;output.eligible=elig;for(int B: {0,1,2,4,8,12}){
  Edge q{};for(int mask=0;mask<M;mask++)if(__builtin_popcount(unsigned(mask))<=B&&mini[mask]!=INF){q.low=min(q.low,mini[mask]);q.high=max(q.high,maxi[mask]);}output.clipped[B]=q;}
 return output;
}
int main(int argc,char**argv){try{if(argc!=2)throw runtime_error("usage: p28_cpp original_compact.csv");auto panels=read(argv[1]);cout<<"policy,B,lower_total,upper_total,independent_lower,independent_upper,eligible_events\n";
 for(const string policy: {"incident_avoid","state_direction","unrestricted"}){map<int,Edge> totals;Edge rect{};int count=0;
   for(auto&p:panels){auto r=solve(p,policy);count+=r.eligible;rect.low+=r.independent.low;rect.high+=r.independent.high;for(auto [B,e]:r.clipped){totals[B].low+=e.low;totals[B].high+=e.high;}}
   for(auto [B,e]:totals)cout<<policy<<","<<B<<","<<e.low<<","<<e.high<<","<<rect.low<<","<<rect.high<<","<<count<<"\n";
 }
 }catch(const exception&e){cerr<<e.what()<<"\n";return 1;}}
