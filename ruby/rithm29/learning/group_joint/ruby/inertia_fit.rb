# frozen_string_literal: true
require 'csv'
require_relative 'inertia_calibration'
module RithmInertiaFit
  module_function
  def logloss(rows,kappa)
    rows.sum do |row|
      p=RithmInertiaCalibration.adjusted_probability(row.fetch(:p),row.fetch(:old),kappa)
      p=[[p,1e-14].max,1-1e-14].min
      row.fetch(:y)==1 ? -Math.log(p) : -Math.log(1.0-p)
    end
  end
  def fit(rows,min:0.0,max:8.0)
    raise ArgumentError,'nonempty training data required' if rows.empty?
    phi=(Math.sqrt(5.0)-1.0)/2
    a=min;b=max
    c=b-phi*(b-a);d=a+phi*(b-a)
    fc=logloss(rows,c);fd=logloss(rows,d)
    60.times do
      if fc<=fd
        b=d;d=c;fd=fc;c=b-phi*(b-a);fc=logloss(rows,c)
      else
        a=c;c=d;fc=fd;d=a+phi*(b-a);fd=logloss(rows,d)
      end
    end
    best=(a+b)/2.0
    logloss(rows,0.0)<=logloss(rows,best) ? 0.0 : best
  end
end
