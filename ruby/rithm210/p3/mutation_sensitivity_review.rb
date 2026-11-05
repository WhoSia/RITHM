# frozen_string_literal: true
# Public, fixed P3 mutation sensitivity audit.
# Original scientific source/test files are READ ONLY; mutants run in disposable directories.
require 'tmpdir'
require 'open3'
require 'rbconfig'
require 'json'
source = File.read(File.join(__dir__, 'occupancy_churn_bounds.rb'), encoding: 'UTF-8')
test = File.read(File.join(__dir__, 'test_occupancy_churn_bounds.rb'), encoding: 'UTF-8')
mutants = {
  'finite_guard_removed' => ['k.is_a?(Numeric) && k.real? && k.finite? && k >= 0', 'k.is_a?(Numeric) && k >= 0'],
  'minimum_signed' => ['minimum:(b-a).abs', 'minimum:(b-a)'],
  'maximum_inverted' => ['maximum:[a+b, 2*n-a-b].min', 'maximum:[a+b, 2*n-a-b].max'],
  'max_cost_uses_min' => ['max_switch_cost:k*hi', 'max_switch_cost:k*lo']
}.freeze

def execute_case(source, test)
  Dir.mktmpdir('rithm-public-mutation-') do |root|
    File.write(File.join(root, 'occupancy_churn_bounds.rb'), source)
    File.write(File.join(root, 'test_occupancy_churn_bounds.rb'), test)
    out, err, status = Open3.capture3(RbConfig.ruby, 'test_occupancy_churn_bounds.rb', chdir: root)
    {passed: status.success?, code: status.exitstatus, text: (out + err)}
  end
end

baseline = execute_case(source, test)
abort 'BASELINE FAILED' unless baseline[:passed] && baseline[:text].include?('1148 assertions, 0 failures')
results = mutants.map do |name, (needle, replacement)|
  count = source.scan(needle).size
  abort "INVALID MUTANT ANCHOR #{name}: #{count}" unless count == 1
  result = execute_case(source.sub(needle, replacement), test)
  abort "SURVIVED MUTATION #{name}" if result[:passed]
  {name: name, killed: true, exit_code: result[:code]}
end
puts JSON.pretty_generate({baseline: {passed: true, assertions: 1148}, mutants: results,
  sensitivity: "#{results.count { |r| r[:killed] }}/#{results.length}",
  note: 'Four fixed deliberate perturbations; NOT a statistical robustness estimate'})
