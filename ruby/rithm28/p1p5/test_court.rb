require 'minitest/autorun'
require_relative 'court'
class P1P5Test < Minitest::Test
 def test_adaptive
  assert_equal 0,RithmP1P5::Court.new(boosts:0).solve
  assert_equal 1,RithmP1P5::Court.new(boosts:1).solve
  assert_equal 1,RithmP1P5::Court.new(horizon:6,boosts:0).solve
 end
 def test_open_loop
  x=RithmP1P5.open_loop(boosts:1)
  assert_equal 0,x[:guarantee];assert_equal 192,x[:plans];assert_equal 6,x[:scenarios]
  y=RithmP1P5.open_loop(boosts:2)
  assert_equal 1,y[:guarantee];assert_equal 512,y[:plans]
 end
 def test_distribution
  assert_equal 2,RithmP1P5::Court.new(boosts:1,objective: :count).solve
  assert_equal 1,RithmP1P5::Court.new(boosts:0,objective: :a).solve
  assert_equal 1,RithmP1P5::Court.new(boosts:0,objective: :b).solve
 end
end