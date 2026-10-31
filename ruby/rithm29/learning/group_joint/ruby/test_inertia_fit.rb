require 'minitest/autorun'
require_relative 'inertia_fit'
class InertiaFitTest < Minitest::Test
  def test_chooses_zero_without_inertia_signal
    rows=Array.new(100){{p:0.9,old:0,y:1}}+Array.new(100){{p:0.1,old:1,y:0}}
    assert_in_delta 0.0,RithmInertiaFit.fit(rows),1e-6
  end
  def test_positive_when_history_persists
    rows=Array.new(100){{p:0.5,old:1,y:1}}+Array.new(100){{p:0.5,old:0,y:0}}
    assert_operator RithmInertiaFit.fit(rows),:>,0.1
  end
  def test_empty
    assert_raises(ArgumentError){RithmInertiaFit.fit([])}
  end
end
