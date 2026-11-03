# frozen_string_literal: true
# Nested session-fold gamma selection; outer test sessions never enter gamma selection.
require_relative '../p1/latent_joint_cv'
require_relative 'residual_negative_control'
require 'json'
module Rithm210NestedGammaCV
  module_function
  GRID=[0.0,0.15,0.30,0.40,0.45,0.60].freeze
  def split(sessions,k)
    sessions.sort.each_with_index.to_h{|s,i|[s,i%k]}
  end
  def train_model(groups,sessions)
    allowed=sessions.to_h{|s|[s,true]}
    count=Hash.new{|h,k|h[k]=[0,0]}
    prior=Hash.new{|h,k|h[k]=[0,0]}
    groups.each do |key,people|
      next unless allowed[key[0]]
      people.each do |r|
        y=r['switchWill'].to_i
        k=Rithm210LatentCV.key(r)
        count[k][0]+=y;count[k][1]+=1
        a=prior[r['RouteA'].to_i];a[0]+=y;a[1]+=1
      end
    end
    [count,prior]
  end
  def probability(model,r)
    k=Rithm210LatentCV.key(r)
    local=model[0].fetch(k,[0,0]);z=model[1].fetch(r['RouteA'].to_i,[0,0])
    prior=(z[0]+1.0)/(z[1]+2.0)
    (local[0]+20.0*prior)/(local[1]+20.0)
  end
  def losses(groups,sessions,model,gamma)
    valid=sessions.to_h{|s|[s,true]}
    sum_joint=0.0;sum_count=0.0;n=0
    groups.each do |key,people|
      next unless valid[key[0]]
      pa=people.select{|r|r['RouteA'].to_i==1}.map{|r|probability(model,r)}
      pb=people.select{|r|r['RouteA'].to_i==0}.map{|r|probability(model,r)}
      up=people.sum{|r|r['switchBtoAWill'].to_i}
      down=people.sum{|r|r['switchAtoBWill'].to_i}
      j,c=Rithm210LatentCV.joint_and_count(pa,pb,up,down,gamma)
      sum_joint+=j;sum_count+=c;n+=1
    end
    {n:n,joint:sum_joint/n,count:sum_count/n}
  end
  def run(path,grid:GRID)
    raise ArgumentError,'grid must contain zero' unless grid.include?(0.0)
    groups=Rithm210ResidualNegativeControl.read_groups(path)
    sessions=groups.keys.map(&:first).uniq.sort
    raise 'sessions mismatch' unless sessions.size==24
    outer=split(sessions,6);folds=[]
    6.times do |ofold|
      holdout=sessions.select{|s|outer[s]==ofold}
      other=sessions.reject{|s|outer[s]==ofold}
      raise 'outer session leakage' unless holdout.size==4 && other.size==20 && (holdout & other).empty?
      inner=split(other,5)
      scores=grid.to_h{|g|[g,0.0]}
      inner_n=0
      5.times do |ifld|
        val=other.select{|s|inner[s]==ifld}
        train=other.reject{|s|inner[s]==ifld}
        raise 'inner session leakage' unless val.size==4 && train.size==16 && (train & holdout).empty?
        model=train_model(groups,train)
        grid.each do |gamma|
          r=losses(groups,val,model,gamma)
          scores[gamma]+=r[:joint]*r[:n]
        end
        inner_n+=groups.count{|k,_|val.include?(k[0])}
      end
      gamma=grid.min_by{|g|[scores[g]/inner_n,g]}
      model=train_model(groups,other)
      chosen=losses(groups,holdout,model,gamma)
      base=losses(groups,holdout,model,0.0)
      folds<<{fold:ofold,train_sessions:other.size,test_sessions:holdout,
        test_n:chosen[:n],gamma:gamma,inner_loss:scores.transform_values{|v|v/inner_n},
        joint:chosen[:joint],joint_baseline:base[:joint],
        count:chosen[:count],count_baseline:base[:count]}
    end
    n=folds.sum{|r|r[:test_n]}
    raise 'unexpected count' unless n==5616
    {n:n,sessions:24,grid:grid,folds:folds,
      gamma_counts:folds.group_by{|r|r[:gamma]}.transform_values(&:size),
      joint:folds.sum{|r|r[:joint]*r[:test_n]}/n,
      joint_baseline:folds.sum{|r|r[:joint_baseline]*r[:test_n]}/n,
      count:folds.sum{|r|r[:count]*r[:test_n]}/n,
      count_baseline:folds.sum{|r|r[:count_baseline]*r[:test_n]}/n}
  end
end
puts JSON.pretty_generate(Rithm210NestedGammaCV.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
