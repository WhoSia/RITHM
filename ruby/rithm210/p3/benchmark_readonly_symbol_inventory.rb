# frozen_string_literal: true
# Public synthetic 12-case Ruby method inventory benchmark. NOT a Serena MCP run.
require_relative 'readonly_symbol_inventory'
CASES = [
 ["def calculate; 1; end\n", %w[calculate]],
 ["# def imaginary\ndef real; end\n", %w[real]],
 ["x = \"def imaginary\"\ndef real; end\n", %w[real]],
 ["x = 'def imaginary'\ndef real; end\n", %w[real]],
 ["doc = <<~TEXT\n def imaginary\nTEXT\ndef real; end\n", %w[real]],
 ["class A\n def self.singleton; end\nend\n", %w[singleton]],
 ["def resource_bounds(n:, path:, k:); k; end\n", %w[resource_bounds]],
 ["def result = 42\n", %w[result]],
 ["def available?; true; end\n", ['available?']],
 ["def validate!; true; end\n", ['validate!']],
 ["define_method(:dynamic) { 1 }\n", []],
 ["module A\n module B\n  def check!; end\n end\nend\n", ['check!']]
].freeze
rows = CASES.map do |source, expected|
 ast = Rithm210ReadOnlySymbols.definitions(source).map { |x| x[:name] }
 raise 'AST did not match fixed gold names' unless ast == expected
 regex = source.scan(/\bdef\s+([A-Za-z_]\w*[!?=]?)/).flatten
 {truth: expected, regex: regex, ast: ast}
end
tp = rows.sum { |r| (r[:truth] & r[:regex]).length }
fp = rows.sum { |r| (r[:regex] - r[:truth]).length }
fn = rows.sum { |r| (r[:truth] - r[:regex]).length }
raise 'fixed benchmark changed' unless [rows.size, tp, fp, fn] == [12,10,5,1]
puts "cases=12 tp=#{tp} fp=#{fp} fn=#{fn} precision=#{Rational(tp,tp+fp)} recall=#{Rational(tp,tp+fn)}"
puts "AST detections=#{rows.sum { |r| r[:ast].length }} with 0 fixed-gold errors"
