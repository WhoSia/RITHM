// C++17 independent reproduction of P27 full-state finite welfare boundaries.
// C++ implementation is deliberately independent of Go and Ruby kernels.
#include <algorithm>
#include <array>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
struct State {int n1,n2,n3,z;};
int cost(int n1,int n2,int z){return 264-24*n1-9*n2+2*n1*n1+2*n1*n2+n2*n2+19*z*n2;}
std::vector<State> load(std::string path){
 std::ifstream f(path);if(!f)throw std::runtime_error("source missing");
 std::string line;std::getline(f,line);std::vector<State> states;
 while(std::getline(f,line)){
  std::istringstream ss(line);std::string cell;std::vector<std::string> fields;
  while(std::getline(ss,cell,','))fields.push_back(cell);
  if(fields.size()!=10)throw std::runtime_error("bad csv column count");
  State x{std::stoi(fields[5]),std::stoi(fields[6]),std::stoi(fields[7]),std::stoi(fields[8])};
  if(x.n1+x.n2+x.n3!=12 || x.z<0 || x.z>1 || cost(x.n1,x.n2,x.z)!=std::stoi(fields[9])) throw std::runtime_error("mismatched cost geometry");
  states.push_back(x);
 }
 if(states.size()!=480)throw std::runtime_error("expected 480 real historical group-round states");
 return states;
}
std::pair<int,int> bounds(State s,int k,int policy){
 int q=s.n2+s.n3,left=s.n2,right=s.n2;
 if(policy==0) {left=std::max(0,s.n2-k);right=std::min(q,s.n2+k);}
 else if(policy==1 && s.z==1){left=std::max(0,s.n2-k);}
 else if(policy==2){if(s.z==1)left=std::max(0,s.n2-k);else right=std::min(q,s.n2+k);}
 int bottom=0,top=0,base=cost(s.n1,s.n2,s.z);
 for(int n2=left;n2<=right;n2++) {int gain=base-cost(s.n1,n2,s.z);bottom=std::min(bottom,gain);top=std::max(top,gain);}
 return {bottom,top};
}
int main(int argc,char **argv){
 if(argc!=2){std::cerr<<"usage: exact_bounds derived_group_states.csv\n";return 2;}
 try{
  auto data=load(argv[1]);const std::array<std::string,3> names={"unrestricted","incident_avoid","state_direction"};
  std::cout<<"scheme,k,N,both,benefit,harm,mean_lower,mean_upper\n";
  for(int policy=0;policy<3;policy++)for(int k=0;k<=2;k++){
   long long L=0,U=0;int both=0,pos=0,neg=0;
   for(auto s:data){auto [a,b]=bounds(s,k,policy);L+=a;U+=b;both+=(a<0&&b>0);pos+=(b>0);neg+=(a<0);}
   std::cout<<names[policy]<<","<<k<<","<<data.size()<<","<<both<<","<<pos<<","<<neg<<","
    <<std::setprecision(15)<<(double)L/data.size()<<","<<(double)U/data.size()<<"\n";
  }
 }catch(std::exception const &e){std::cerr<<e.what()<<"\n";return 1;}
}
