# frozen_string_literal: true
# RITHM-2.10 P2-R5: online actor switching history (strictly prior periods).
# Original source CSV is held in Drive; DO NOT commit participant rows.
require 'csv'
require 'json'

module Rithm210OnlineIdentity
  module_function

  def source(path)
    groups = Hash.new { |h,k| h[k] = [] }
    CSV.foreach(path, headers: true) do |r|
      s = r.fetch('session').to_i
      t = r.fetch('trt').to_i
      p = r.fetch('Period').to_i
      next unless t.between?(1,3) && s != 2 && s != 101 && p.between?(1,39)
      groups[[s,r.fetch('section').to_i,r.fetch('Group').to_i,p]] << r
    end
    raise 'source group mismatch' unless groups.size == 5616 && groups.values.all? { |rs| rs.size == 6 }
    groups
  end

  def actor_key(r)
    [r['trt'].to_i,r['Informed'].to_i,r['RouteA'].to_i,r['Cost'].to_f]
  end

  def train(groups, heldout_sessions)
    counts = Hash.new { |h,k| h[k] = [0,0] }
    global = Hash.new { |h,k| h[k] = [0,0] }
    groups.each do |(session,*_),people|
      next if heldout_sessions.include?(session)
      people.each do |r|
        y = r['switchWill'].to_i
        raise 'invalid switch' unless y == 0 || y == 1
        a = counts[actor_key(r)]
        a[0] += y; a[1] += 1
        b = global[r['RouteA'].to_i]
        b[0] += y; b[1] += 1
      end
    end
    [counts,global]
  end

  def probability(model,r)
    counts,global = model
    q = counts.fetch(actor_key(r),[0,0])
    b = global.fetch(r['RouteA'].to_i,[0,0])
    prior = (b[0]+1.0)/(b[1]+2.0)
    (q[0]+20.0*prior)/(q[1]+20.0)
  end

  def online_probability(prior,history,strength)
    raise ArgumentError, 'strength must be positive' unless strength.positive?
    switch_count,n = history
    (strength*prior+switch_count)/(strength+n)
  end

  def convolve(ps)
    ps.reduce([1.0]) do |prev,p|
      out = Array.new(prev.size+1,0.0)
      prev.each_with_index { |v,i| out[i]+=v*(1-p);out[i+1]+=v*p }
      out
    end
  end

  def group_scores(people,probs)
    up=[];down=[];u=0;d=0
    people.each_with_index do |r,i|
      if r['RouteA'].to_i == 1
        down << probs[i]
        d += r['switchAtoBWill'].to_i
      else
        up << probs[i]
        u += r['switchBtoAWill'].to_i
      end
    end
    p_up=convolve(up)
    p_down=convolve(down)
    joint=p_up.fetch(u)*p_down.fetch(d)
    next_a=0.0
    p_up.each_with_index do |a,i|
      p_down.each_with_index { |b,j| next_a+=a*b if i-j==u-d }
    end
    raise 'zero likelihood' unless joint>0 && next_a>0
    [-Math.log(joint),-Math.log(next_a),(u-up.sum)*(d-down.sum)]
  end

  def run(path,strengths:[5.0,20.0,80.0])
    groups=source(path)
    sessions=groups.keys.map(&:first).uniq.sort
    raise 'session mismatch' unless sessions.size==24
    fold_map=sessions.each_with_index.to_h { |s,i| [s,i%6] }
    rows=[]
    6.times do |fold|
      held=sessions.select{|s|fold_map[s]==fold}
      fitted=train(groups,held)
      keys=groups.keys.select{|k|held.include?(k[0])}.sort_by{|s,section,g,period|[s,section,period,g]}
      all_hist=Hash.new { |h,k| h[k]=[0,0] }
      section_hist=Hash.new { |h,k| h[k]=[0,0] }
      keys.each do |session,section,group,period|
        people=groups.fetch([session,section,group,period])
        ids=people.map{|r|r['ID'].to_i}
        raise 'duplicate group actor' unless ids.uniq.length==6
        baseline=people.map{|r|probability(fitted,r)}
        candidates={baseline:baseline}
        strengths.each do |strength|
          {within_section:section_hist,cross_section:all_hist}.each do |mode,history|
            label="#{mode}_#{strength.to_i}".to_sym
            candidates[label]=people.each_with_index.map do |r,i|
              hkey=mode==:within_section ? [session,section,r['ID'].to_i] : [session,r['ID'].to_i]
              online_probability(baseline[i],history[hkey],strength)
            end
          end
        end
        candidates.each do |variant,p|
          joint,count,cross=group_scores(people,p)
          rows << {session:session,section:section,group:group,period:period,
            variant:variant,joint:joint,count:count,cross:cross}
        end
        # y_t enters histories only AFTER making period-t prediction.
        people.each do |r|
          y=r['switchWill'].to_i
          [[session,r['ID'].to_i],[session,section,r['ID'].to_i]].each_with_index do |hkey,j|
            hist=j==0 ? all_hist : section_hist
            hist[hkey][0]+=y
            hist[hkey][1]+=1
          end
        end
      end
    end
    raise 'number of predictions mismatch' unless rows.size==5616*(1+2*strengths.size)
    models=rows.group_by{|r|r[:variant]}
    {sessions:24,groups:5616,
      models:models.to_h{|name,rs|[name,[:joint,:count,:cross].to_h{|key|[key,rs.sum{|r|r[key]}/rs.size.to_f]}]},
      session_rows:models.transform_values do |rs|
        rs.group_by{|r|r[:session]}.map do |s,a|
          {session:s,n:a.size,**[:joint,:count,:cross].to_h{|key|[key,a.sum{|r|r[key]}/a.size.to_f]}}
        end
      end}
  end
end
puts JSON.pretty_generate(Rithm210OnlineIdentity.run(ARGV.fetch(0))) if __FILE__==$PROGRAM_NAME
