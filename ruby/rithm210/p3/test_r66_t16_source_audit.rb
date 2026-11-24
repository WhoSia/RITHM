# frozen_string_literal: true
require 'minitest/autorun'
require 'tempfile'
require_relative 'r66_t16_source_audit'
class T16AuditTest < Minitest::Test
  A=RithmT16::SourceAudit
  def test_ambiguous_state_and_sign
    x=A.classify(:a,9);assert_equal (0..5).to_a,x[:support];refute x[:sign_known]
  end
  def test_ambiguous_state_but_known_sign
    x=A.classify(:a,14);assert_equal [0,1],x[:support];assert x[:sign_known]
  end
  def test_sha_gate
    Tempfile.create('invalid') { |f| f.write('invalid'); f.flush; assert_raises(ArgumentError){A.audit(f.path)} }
  end
end
