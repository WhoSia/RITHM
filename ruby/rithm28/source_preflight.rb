# frozen_string_literal: true
require 'csv'
require 'digest'
require 'json'
require 'pathname'

# Read-only and bounded inspection. Never prints participant rows.
module RithmSourcePreflight
  EXPECTED = %w[session section trt Period ID Group RouteA RouteB].freeze
  module_function

  def inspect(path)
    file = Pathname(path)
    raise ArgumentError, 'file missing' unless file.file?
    bytes = file.size
    first = File.open(path, 'rb') { |f| f.read(4096) || ''.b }
    zero_only_prefix = !first.empty? && first.bytes.all?(&:zero?)
    raise ArgumentError, 'empty input' if bytes.zero?
    digest = Digest::SHA256.file(path).hexdigest
    result = {
      'filename' => file.basename.to_s, 'bytes' => bytes, 'sha256' => digest,
      'zero_only_prefix' => zero_only_prefix,
      'expected_headers_present' => false, 'status' => 'HOLD'
    }
    return result.merge('reason' => 'NUL_ONLY_PREFIX') if zero_only_prefix
    begin
      first_line = File.open(path, 'rb') { |f| f.gets }
      raise ArgumentError, 'header line exceeds safe bound' if first_line.nil? || first_line.bytesize > 16_384
      headers = CSV.parse_line(first_line.force_encoding('UTF-8'), liberal_parsing: false)
      headers = (headers || []).map { |x| x.to_s.sub(/\A\uFEFF/, '').strip }
      matched = (EXPECTED - headers).empty?
      result.merge('expected_headers_present' => matched,
        'header_names' => headers.first(80), 'status' => matched ? 'SCHEMA_HEADER_PRESENT' : 'HEADER_REVIEW',
        'reason' => matched ? 'NO_ROW_VALIDATION_YET' : 'EXPECTED_COLUMNS_MISSING')
    rescue CSV::MalformedCSVError, Encoding::InvalidByteSequenceError, ArgumentError => e
      result.merge('status' => 'HEADER_REVIEW', 'reason' => e.class.to_s)
    end
  end
end

if __FILE__ == $PROGRAM_NAME
  abort('usage: ruby source_preflight.rb RAW_CSV_PATH [RAW_CSV_PATH...]') if ARGV.empty?
  puts JSON.pretty_generate(ARGV.map { |path| RithmSourcePreflight.inspect(path) })
end
