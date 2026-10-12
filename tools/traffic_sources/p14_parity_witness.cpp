// RITHM-2.6 P14: original-source five-minute volume parity/negative-control witness.
// c++ -O3 -std=c++17 p14_parity_witness.cpp -o parity
// ./parity 20250418 /path/to/2025*__part_*.csv
// Counts are sensor readings, NOT causal traffic-intervention or human welfare.
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;
static void csvcells(const string& s,vector<string>& o){
 o.clear();string x;bool quote=false;
 for(size_t i=0;i<s.size();++i){char c=s[i];
  if(c=='"'){if(quote && i+1<s.size() && s[i+1]=='"'){x+='"';++i;}else quote=!quote;}
  else if(c==','&&!quote){o.push_back(move(x));x.clear();}
  else if(c!='\r')x+=c;
 }
 o.push_back(move(x));if(quote)throw runtime_error("bad CSV quotation");
}
struct Link{
 vector<double> q,speed,occ;vector<bool> present;
 Link():q(288,numeric_limits<double>::quiet_NaN()),
 speed(288,numeric_limits<double>::quiet_NaN()),
 occ(288,numeric_limits<double>::quiet_NaN()),present(288,false){}
};
static double parse(const string& s){
 if(s.empty())return numeric_limits<double>::quiet_NaN();
 char* end=nullptr;double v=strtod(s.c_str(),&end);
 return (end==s.c_str()||*end!='\0'||!isfinite(v))?numeric_limits<double>::quiet_NaN():v;
}
static pair<double,double> source_lag_errors(const vector<Link>& links,int field){
 double sum5=0,sum10=0;size_t n=0;
 for(const auto& l:links){
  const vector<double>& a=field==0?l.q:(field==1?l.speed:l.occ);
  for(size_t t=2;t<288;t++)if(isfinite(a[t])&&isfinite(a[t-1])&&isfinite(a[t-2])){
   sum5+=fabs(a[t]-a[t-1]);sum10+=fabs(a[t]-a[t-2]);++n;
  }
 }
 if(!n)throw runtime_error("no matched source triples");
 return {sum5/n,sum10/n};
}
int main(int argc,char**argv){
 try{
  if(argc<3)throw runtime_error("usage: p14_parity_witness YYYYMMDD source_parts...");
  string day=argv[1];if(day.size()!=8)throw runtime_error("date expected YYYYMMDD");
  const string hdr="DATE_CD,ROUTE_ID,ROUTE_NAME,LINK_ID,ROAD_NAME,HH5M_CD,VOL,SPD,OCC";
  vector<Link> links;unordered_map<string,size_t> ids;vector<string> fields;string line;size_t rows=0;
  for(int a=2;a<argc;a++){
   ifstream f(argv[a]);if(!f)throw runtime_error(string("source not readable: ")+argv[a]);
   if(!getline(f,line))throw runtime_error("empty source");
   if(line.size()>=3&&(unsigned char)line[0]==0xEF&&
     (unsigned char)line[1]==0xBB&&(unsigned char)line[2]==0xBF)line.erase(0,3);
   if(!line.empty()&&line.back()=='\r')line.pop_back();
   if(line!=hdr)throw runtime_error(string("native source-header contract failure in ")+argv[a]);
   while(getline(f,line)){
    if(line.size()<8||line.compare(0,8,day)!=0)continue;
    csvcells(line,fields);if(fields.size()!=9)throw runtime_error("bad source row field count");
    const string& t=fields[5];if(t.size()!=4)throw runtime_error("bad five-minute bin");
    int hour=stoi(t.substr(0,2)),minute=stoi(t.substr(2,2));
    if(hour>23||minute>=60||minute%5)throw runtime_error("invalid clock");
    int bin=hour*12+minute/5;
    string id=fields[1]+"|"+fields[3];auto it=ids.find(id);size_t j;
    if(it==ids.end()){j=links.size();ids[id]=j;links.emplace_back();}else j=it->second;
    auto& l=links[j];if(l.present[bin])throw runtime_error("duplicated link/date/five-minute bin");
    l.present[bin]=true;
    l.q[bin]=parse(fields[6]);l.speed[bin]=parse(fields[7]);l.occ[bin]=parse(fields[8]);++rows;
   }
  }
  if(!rows)throw runtime_error("source date has no observations");
  int odd_greater=0,even_greater=0,lag10_links=0;size_t eligible=0;
  for(const auto& l:links){
   double even=0,odd=0,sum5=0,sum10=0;int ne=0,no=0,nt=0;
   for(int t=0;t<288;t++)if(isfinite(l.q[t])){
    if(t%2){odd+=l.q[t];no++;}else{even+=l.q[t];ne++;}
   }
   if(ne&&no){even/=ne;odd/=no;
    if(odd>even)odd_greater++;else if(even>odd)even_greater++;
   }
   for(int t=2;t<288;t++)if(isfinite(l.q[t])&&isfinite(l.q[t-1])&&isfinite(l.q[t-2])){
    sum5+=fabs(l.q[t]-l.q[t-1]);sum10+=fabs(l.q[t]-l.q[t-2]);nt++;
   }
   if(nt>=250){eligible++;if(sum10<sum5)lag10_links++;}
  }
  auto q=source_lag_errors(links,0),s=source_lag_errors(links,1),o=source_lag_errors(links,2);
  cout<<setprecision(9)<<"date="<<day<<" links="<<links.size()<<" rows="<<rows
      <<" odd_greater="<<odd_greater<<" even_greater="<<even_greater
      <<" lag10_better_links="<<lag10_links<<"/"<<eligible
      <<" q_5="<<q.first<<" q_10="<<q.second<<" q_ratio="<<q.first/q.second
      <<" speed_ratio="<<s.first/s.second<<" occupancy_ratio="<<o.first/o.second<<"\n";
 }catch(const exception&e){cerr<<"P14_SOURCE_FAILURE: "<<e.what()<<"\n";return 2;}
}
