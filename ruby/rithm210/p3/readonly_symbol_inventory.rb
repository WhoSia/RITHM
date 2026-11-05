# frozen_string_literal: true
# RITHM-2.10 public synthetic-only symbol inventory baseline.
# Standard-library AST walk: comments and strings never count as method definitions.
require 'ripper'

module Rithm210ReadOnlySymbols
  module_function

  # Input: UTF-8 Ruby source string. Output: deterministic method symbol metadata.
  # This does not execute the source or inspect external/private project files.
  def definitions(source)
    raise ArgumentError, 'source must be a String' unless source.is_a?(String)
    raise ArgumentError, 'source exceeds 64 KiB' if source.bytesize > 65_536
    tree = Ripper.sexp(source)
    raise ArgumentError, 'Ruby parse failed' if tree.nil?

    found = []
    walk = lambda do |node|
      next unless node.is_a?(Array)
      if node[0] == :def
        token = node[1]
        found << {name: token[1], line: token[2][0]} if token.is_a?(Array) && token[0].to_s.start_with?('@')
      elsif node[0] == :defs
        token = node[3]
        found << {name: token[1], line: token[2][0]} if token.is_a?(Array) && token[0].to_s.start_with?('@')
      end
      node.each { |child| walk.call(child) if child.is_a?(Array) }
    end
    walk.call(tree)
    found.sort_by { |item| [item[:line], item[:name]] }
  end
end
