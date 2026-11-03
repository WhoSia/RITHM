# frozen_string_literal: true
# Descriptive linear projection of fixed-gamma score difference on treatment,
# section, and session FE. Randomized assignment is NOT assumed.
require_relative 'treatment_epoch_cv'
module Rithm210SectionAdjustedRegression
  module_function
  def session_panels(rows)
    values=rows.group_by{|r|[r[:session],r[:section]]}.map do |(s,sec),a|
      t=a.map{|r|r[:treatment]}.uniq
      raise 'section treatment not unique' unless t.size==1
      {session:s,section:sec,treatment:t.first,
        y:a.sum{|r|r[:joint1]-r[:joint0]}/a.size.to_f}
    end
    by=values.group_by{|r|r[:session]}
    raise 'session count' unless by.size==24
    by.values.each do |a|
      raise 'incomplete treatment sequence' unless a.size==3 && a.map{|r|r[:treatment]}.sort==[1,2,3]
      raise 'incomplete section order' unless a.map{|r|r[:section]}.sort==[2,3,4]
    end
    by.values
  end
  def solve(a,b)
    n=b.size
    matrix=a.each_with_index.map{|r,i|r.map(&:to_f)+[b[i].to_f]}
    n.times do |i|
      pivot=(i...n).max_by{|j|matrix[j][i].abs}
      raise 'singular design matrix' if matrix[pivot][i].abs<1e-10
      matrix[i],matrix[pivot]=matrix[pivot],matrix[i]
      z=matrix[i][i]
      (i..n).each{|j|matrix[i][j]/=z}
      n.times do |k|
        next if k==i
        c=matrix[k][i]
        (i..n).each{|j|matrix[k][j]-=c*matrix[i][j]}
      end
    end
    (0...n).map{|i|matrix[i][n]}
  end
  def coefficients(panels)
    xtx=Array.new(4){Array.new(4,0.0)}
    xty=Array.new(4,0.0)
    panels.each do |panel|
      x=panel.map{|r|[r[:treatment]==2 ? 1.0 : 0.0,r[:treatment]==3 ? 1.0 : 0.0,
        r[:section]==3 ? 1.0 : 0.0,r[:section]==4 ? 1.0 : 0.0]}
      means=(0..3).map{|j|x.sum{|r|r[j]}/panel.size.to_f}
      mean_y=panel.sum{|r|r[:y]}/panel.size.to_f
      panel.each_with_index do |r,k|
        v=x[k].each_with_index.map{|z,j|z-means[j]}
        z=r[:y]-mean_y
        4.times do |j|
          xty[j]+=v[j]*z
          4.times{|l|xtx[j][l]+=v[j]*v[l]}
        end
      end
    end
    solve(xtx,xty)
  end
  def interval(panels,draws:20_000,seed:20261103)
    point=coefficients(panels)
    rng=Random.new(seed)
    sample=Array.new(draws){coefficients(Array.new(panels.size){panels.fetch(rng.rand(panels.size))})}
    (0..3).map do |j|
      v=sample.map{|x|x[j]}.sort
      {point:point[j],lower:v[(draws*0.025).floor],upper:v[(draws*0.975).floor]}
    end
  end
  def run(path,draws:20_000)
    rows=Rithm210TreatmentEpochCV.predict(Rithm210ResidualNegativeControl.read_groups(path))
    panels=session_panels(rows)
    {sessions:panels.size,model:'session-FE demeaned OLS treatment + section',
      coefficient_names:%w[partial_vs_no full_vs_no section3_vs_section2 section4_vs_section2],
      coefficients:interval(panels,draws:draws)}
  end
end
puts JSON.pretty_generate(Rithm210SectionAdjustedRegression.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
