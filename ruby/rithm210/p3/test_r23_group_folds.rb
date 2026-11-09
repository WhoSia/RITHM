require 'minitest/autorun'
require_relative 'r23_group_memory_cv'
class TestR23GroupFoldLeakage < Minitest::Test
  M=Rithm210R23GroupMemoryCV
  def fixture
    (1..24).flat_map do |s|
      (1..3).flat_map do |trt|
        ['frequency_decay_1.0','memory_1.0_markov_5.0_mix_0.25'].map do |model|
          # Competitor is attractive only in a subset of heldout sessions.
          loss=model.start_with?('frequency') ? 0.5 : (s%6==1 ? 8.0 : 0.3)
          {session:s,treatment:trt,model:model,groups:40,
           logloss:loss,brier:loss,cost_abs_error:loss}
        end
      end
    end
  end
  def test_fold_decisions_cannot_use_own_heldout_sessions
    original=M.cross_validate(fixture,draws:20,seed:7)
    assert_equal 18,original.fetch(:fold_choices).size
    original[:fold_choices].each do |choice|
      assert_equal 20,choice[:training_sessions]
      assert_equal 4,choice[:heldout_sessions]
    end
    # Destroy all test outcomes of fold 0. Fold 0's selected models MUST remain
    # unchanged. Selection on other folds can change and is not constrained.
    altered=fixture.map do |row|
      if (row[:session]-1)%6==0
        row.merge(logloss:row[:logloss]*1000.0)
      else
        row
      end
    end
    replay=M.cross_validate(altered,draws:20,seed:7)
    assert_equal original[:fold_choices].select{|r|r[:fold]==0},
      replay[:fold_choices].select{|r|r[:fold]==0}
  end
  def test_repeated_source_cannot_masquerade_as_more_independent_sessions
    rows=fixture
    assert_raises(RuntimeError) do
      M.cross_validate(rows.select{|r|r[:session]<24},draws:10)
    end
  end
end
