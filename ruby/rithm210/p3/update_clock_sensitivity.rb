# frozen_string_literal: true
# RITHM P3-R17D: exact finite-grid sensitivity, no continuum theorem claimed.
require_relative 'update_clock_signal_factorial'
module Rithm210UpdateClockSensitivity
  module_function
  M=Rithm210UpdateClockSignalFactorial
  GRID=[0.to_r,Rational(1,100),Rational(1,20),Rational(1,10),
        Rational(1,5),Rational(3,10),Rational(2,5),Rational(1,2)].freeze
  def run(grid:GRID)
    raise ArgumentError,'nonempty epsilon grid required' if grid.empty?
    rows=grid.flat_map do |epsilon|
      (0..6).map do |n|
        result=M.factorial(initial_mask:(1<<n)-1,tremble:epsilon)
        {initial:n,tremble:epsilon,interaction:result[:difference_in_differences]}
      end
    end
    {grid_points:rows.length,
     positive:rows.count{|r|r[:interaction]>0},
     zero:rows.count{|r|r[:interaction]==0},
     negative:rows.count{|r|r[:interaction]<0},
     min:rows.min_by{|r|r[:interaction]},
     max:rows.max_by{|r|r[:interaction]},
     initial4:rows.select{|r|r[:initial]==4},
     warning:'Only a prelisted finite rational grid under one behavioral rule; no claim for all parameters/learning mechanisms or empirical effect.'}
  end
end
if __FILE__==$PROGRAM_NAME
  require 'json'
  a=Rithm210UpdateClockSensitivity.run
  puts JSON.pretty_generate(a.transform_values{|v|
    if v.is_a?(Hash)
      v.transform_values{|x|x.is_a?(Rational) ? x.to_f : x}
    elsif v.is_a?(Array)
      v.map{|row|row.transform_values{|x|x.is_a?(Rational) ? x.to_f : x}}
    else
      v
    end})
end
