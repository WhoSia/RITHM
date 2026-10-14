#include <cassert>
#include <cstdint>
#include <iostream>
using namespace std;
// Independent C++17 replay; separate implementation from Go/Karp.
bool budget(uint64_t w,int k,int b){for(int t=0;t+k<=12;t++){auto m=(w>>t)&((1ULL<<k)-1);if(__builtin_popcountll(m)>b)return false;}return true;}
bool verify(int phase,bool fb,uint64_t w){int z=phase,old=z,mem=z,shockLast=0;for(int t=0;t<12;t++){int a=fb?mem:1-old;int d=a^z;if(t&&d!=shockLast)return false;int shock=(w>>t)&1;int newz=z^1^shock^(fb?d:0);old=z;z=newz;mem^=1;shockLast=shock;}return true;}
int main(){long total=0;for(int k:{3,5})for(int b=0;b<=k;b++)for(int phase=0;phase<2;phase++)for(int f=0;f<2;f++)for(uint64_t w=0;w<4096;w++){if(!budget(w,k,b))continue;assert(verify(phase,f,w));total++;}assert(total==63972);cout<<"PASS independent admissible histories "<<total<<"\n";}
