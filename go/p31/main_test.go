package main
import "testing"
func TestP31Baseline(t *testing.T){a:=solve("clock_only","toggle1bit");if a.MaxMean!=192||!a.Safe{t.Fatalf("%+v",a)};b:=solve("clock_only","constant0");if b.MaxMean!=194||b.Safe{t.Fatalf("%+v",b)}}
func TestP31Feedback(t *testing.T){a:=solve("feedback_only","toggle1bit");if a.MaxMean!=192||!a.Safe{t.Fatalf("%+v",a)}}
func TestP31AdversarialShock(t *testing.T){for _,m:=range []string{"shock_only","shock_feedback"}{for _,p:=range []string{"constant0","toggle1bit","delay1"}{a:=solve(m,p);if a.MaxMean!=196||a.Safe{t.Fatalf("%+v",a)}}}}
func TestP31Oracle(t *testing.T){for _,m:=range []string{"clock_only","feedback_only","shock_only","shock_feedback"}{a:=solve(m,"oracle");if a.MaxMean!=192||!a.Safe{t.Fatalf("%+v",a)}}}
func TestP31ShockFeedbackEquivalence(t *testing.T){for _,p:=range []string{"constant0","toggle1bit","delay1","oracle"}{a:=solve("shock_only",p);b:=solve("shock_feedback",p);if a.MaxMean!=b.MaxMean||a.Safe!=b.Safe{t.Fatal(p,a,b)}}}
func TestP31FiniteCycleMeans(t *testing.T){for _,m:=range []string{"clock_only","feedback_only","shock_only","shock_feedback"}{for _,p:=range []string{"constant0","toggle1bit","delay1","oracle"}{a:=solve(m,p);if a.MaxMean<192||a.MaxMean>196||a.States==0{t.Fatal(a)}}}}
