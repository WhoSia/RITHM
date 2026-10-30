require 'csv'
require_relative 'learning_models'
# Synthetic five-step route history, NOT an experimental replication.
trace=[{route_a:1,payoff:5.0,total_a:4},{route_a:1,payoff:4.0,total_a:4},{route_a:0,payoff:9.0,total_a:3},{route_a:0,payoff:8.0,total_a:3},{route_a:1,payoff:6.0,total_a:2}]
CSV.open(File.join(__dir__,'synthetic_model_comparison.csv'),'w') do |csv|
  csv<<%w[type period EWA_P_A SSM5_P_A_MC]
  [true,false].each do |informed|
    ewa=RithmLearningModels::EWA.new(informed:informed,lambda:1.0)
    5.times do |idx|
      ss=RithmLearningModels::SmallSample.new(informed:informed,rng:Random.new(101))
      trace.first(idx).each { |x| ss.observe(**(informed ? x : x.reject { |k,_| k==:total_a })) }
      p_ssm=2000.times.sum { ss.choose==1 ? 1.0 : 0.0 } / 2000
      csv<<[(informed ? 'informed' : 'uninformed'),idx+1,format('%.6f',ewa.probability_a),format('%.6f',p_ssm)]
      x=trace[idx]; ewa.update(**(informed ? x : x.reject { |k,_| k==:total_a }))
    end
  end
end
