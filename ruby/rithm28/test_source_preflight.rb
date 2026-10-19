# frozen_string_literal: true
require 'minitest/autorun'
require 'tmpdir'
require 'fileutils'
require_relative 'source_preflight'

class TestSourcePreflight < Minitest::Test
  def test_normal_header
    Dir.mktmpdir do |dir|
      path = File.join(dir, 'example.csv')
      File.binwrite(path, "session,section,trt,Period,ID,Group,RouteA,RouteB\nS1,2,1,1,pseudonym,g,1,0\n")
      result = RithmSourcePreflight.inspect(path)
      assert_equal 'SCHEMA_HEADER_PRESENT', result.fetch('status')
      assert_equal false, result.fetch('zero_only_prefix')
      assert_equal Digest::SHA256.file(path).hexdigest, result.fetch('sha256')
    end
  end
  def test_null_payload_rejected
    Dir.mktmpdir do |dir|
      path = File.join(dir, 'damaged.csv')
      File.binwrite(path, "\0" * 10_000)
      result = RithmSourcePreflight.inspect(path)
      assert_equal 'HOLD', result.fetch('status')
      assert_equal 'NUL_ONLY_PREFIX', result.fetch('reason')
    end
  end
  def test_missing_fields_gated
    Dir.mktmpdir do |dir|
      path = File.join(dir, 'unknown.csv')
      File.binwrite(path, "a,b,c\n1,2,3\n")
      assert_equal 'HEADER_REVIEW', RithmSourcePreflight.inspect(path).fetch('status')
    end
  end
end
