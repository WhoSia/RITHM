# frozen_string_literal: true
require_relative 'paid_agency'
require 'json'
a=Rithm29PaidAgency.audit
rows=a.fetch(:rows).map{|r|{'policies'=>r.fetch(:policies).map(&:to_s),
'individual_quarters'=>r.fetch(:individual).map{|v|Integer(v*4)},
'social_quarters'=>Integer(r.fetch(:social)*4),
'pure_nash'=>r.fetch(:pure_nash)}}
puts JSON.generate(rows)
