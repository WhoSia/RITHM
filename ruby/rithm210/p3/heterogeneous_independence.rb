# frozen_string_literal: true
# A six-person strictly independent yet heterogeneous Bernoulli negative control.
# Previous players 0..3 on A, players 4..5 on B, conditioned on n_t=4.
module Rithm210HeterogeneousIndependence
  module_function

  def validate(ps)
    raise ArgumentError,'six actor probabilities required' unless ps.is_a?(Array)&&
      ps.length==6&&ps.all?{|x|x.is_a?(Numeric)&&x.finite?&&x.between?(0,1)}
  end

  def convolve(ps)
    a=[1.0]
    ps.each do |p|
      b=Array.new(a.length+1,0.0)
      a.each_with_index do |v,i|
        b[i]+=v*(1-p)
        b[i+1]+=v*p
      end
      a=b
    end
    a
  end

  def analyze(probabilities)
    validate(probabilities)
    a=probabilities.first(4)
    b=probabilities.last(2)
    p_down=convolve(a)
    p_up=convolve(b)
    joint={}
    p_up.each_with_index do |pu,u|
      p_down.each_with_index do |pd,d|
        joint[[u,d]]=pu*pd
      end
    end
    raise 'not normalized' unless (joint.values.sum-1).abs<1e-10
    gross=probabilities.sum.to_f
    signed_mean=b.sum-a.sum
    variance=probabilities.sum{|p|p*(1-p)}
    loss=3*(variance+signed_mean*signed_mean)
    exact_loss=joint.sum{|(u,d),prob|3*(u-d)**2*prob}
    raise 'heterogeneous independence identity failed' unless (exact_loss-loss).abs<1e-9
    {gross:gross,zero:joint.fetch([0,0]),cancellation:joint.sum{|(u,d),p|u>0&&u==d ? p : 0},
      signed_mean:signed_mean,net_variance:variance,next_excess:loss}
  end
end
