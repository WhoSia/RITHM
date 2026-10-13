// RITHM-2.7 P28. Exact bounded replays over original 2017 human route profiles.
// No actual new advice was administered; not an identified treatment effect.
package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"math/big"
	"math/bits"
	"os"
	"strconv"
	"strings"
)

type Panel struct {
	Session            string
	Group, Stage, Info int
	Routes             [20][12]int
	Incident           [20]int
}
type Bounds struct{ Lower, Upper int }

func cost(n1, n2, z int) int { return 264 - 24*n1 - 9*n2 + 2*n1*n1 + 2*n1*n2 + n2*n2 + 19*z*n2 }
func readPanels(path string) ([]Panel, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	cr := csv.NewReader(f)
	rr, err := cr.ReadAll()
	if err != nil {
		return nil, err
	}
	if len(rr) != 25 {
		return nil, fmt.Errorf("expected 24 rows, got %d", len(rr)-1)
	}
	wanted := []string{"session", "group", "stage", "info", "choices_base3_hex", "group_stage_total_cost", "incident_20_bits_hex"}
	for i, k := range wanted {
		if rr[0][i] != k {
			return nil, fmt.Errorf("header %d must be %s", i, k)
		}
	}
	out := make([]Panel, 0, 24)
	sessions := map[string]bool{}
	for _, row := range rr[1:] {
		var p Panel
		p.Session = row[0]
		p.Group, _ = strconv.Atoi(row[1])
		p.Stage, _ = strconv.Atoi(row[2])
		p.Info, _ = strconv.Atoi(row[3])
		sessions[p.Session] = true
		val := new(big.Int)
		if _, ok := val.SetString(row[4], 16); !ok {
			return nil, fmt.Errorf("bad hex panel")
		}
		three := big.NewInt(3)
		for t := 19; t >= 0; t-- {
			for j := 11; j >= 0; j-- {
				quot, rem := new(big.Int), new(big.Int)
				quot.QuoRem(val, three, rem)
				p.Routes[t][j] = int(rem.Int64()) + 1
				val = quot
			}
		}
		if val.Sign() != 0 {
			return nil, fmt.Errorf("overflow")
		}
		ib, err := strconv.ParseUint(row[6], 16, 32)
		if err != nil {
			return nil, err
		}
		if bits.OnesCount64(ib) != 4 {
			return nil, fmt.Errorf("incident quota !=4")
		}
		sum := 0
		for t := 0; t < 20; t++ {
			p.Incident[t] = int((ib >> uint(19-t)) & 1)
			n1, n2 := 0, 0
			for j := 0; j < 12; j++ {
				switch p.Routes[t][j] {
				case 1:
					n1++
				case 2:
					n2++
				}
			}
			sum += cost(n1, n2, p.Incident[t])
		}
		reported, _ := strconv.Atoi(row[5])
		_ = reported // published raw cost does not always match formula: preserve discrepancy, no silent repair
		out = append(out, p)
	}
	if len(sessions) != 6 {
		return nil, fmt.Errorf("expected six independent source sessions")
	}
	return out, nil
}
func admissible(route, z int, policy string) int { // 0=not eligible, +-1 is new change to n2
	switch policy {
	case "incident_avoid":
		if z == 1 && route == 2 {
			return -1
		}
	case "state_direction":
		if z == 1 && route == 2 {
			return -1
		}
		if z == 0 && route == 3 {
			return 1
		}
	case "unrestricted":
		if route == 2 {
			return -1
		}
		if route == 3 {
			return 1
		}
	default:
		panic("unknown policy")
	}
	return 0
}
func computePanel(p Panel, policy string) (map[int]Bounds, Bounds, int) {
	const masks = 1 << 12
	const inf = int(1 << 30)
	lo := make([]int, masks)
	hi := make([]int, masks)
	for i := range lo {
		lo[i] = inf
		hi[i] = -inf
	}
	lo[0] = 0
	hi[0] = 0
	local := Bounds{}
	opportunities := 0
	for t := 0; t < 20; t++ {
		nextLo := make([]int, masks)
		nextHi := make([]int, masks)
		for i := range nextLo {
			nextLo[i] = inf
			nextHi[i] = -inf
		}
		n1, n2 := 0, 0
		for _, v := range p.Routes[t] {
			if v == 1 {
				n1++
			}
			if v == 2 {
				n2++
			}
		}
		z := p.Incident[t]
		base := cost(n1, n2, z)
		roundLo, roundHi := 0, 0
		for j, route := range p.Routes[t] {
			dir := admissible(route, z, policy)
			if dir == 0 {
				continue
			}
			opportunities++
			gain := base - cost(n1, n2+dir, z)
			if gain < roundLo {
				roundLo = gain
			}
			if gain > roundHi {
				roundHi = gain
			}
			b := 1 << j
			for m := 0; m < masks; m++ {
				if m&b != 0 || lo[m] == inf {
					continue
				}
				newmask := m | b
				if x := lo[m] + gain; x < nextLo[newmask] {
					nextLo[newmask] = x
				}
				if x := hi[m] + gain; x > nextHi[newmask] {
					nextHi[newmask] = x
				}
			}
		}
		local.Lower += roundLo
		local.Upper += roundHi // per-round P27 rectangular bound
		for m := 0; m < masks; m++ {
			if lo[m] < nextLo[m] {
				nextLo[m] = lo[m]
			}
			if hi[m] > nextHi[m] {
				nextHi[m] = hi[m]
			}
		}
		lo, hi = nextLo, nextHi
	}
	budgets := []int{0, 1, 2, 4, 8, 12}
	out := map[int]Bounds{}
	for _, b := range budgets {
		best := Bounds{Lower: 0, Upper: 0}
		for m := 0; m < masks; m++ {
			if bits.OnesCount(uint(m)) > b || lo[m] == inf {
				continue
			}
			if lo[m] < best.Lower {
				best.Lower = lo[m]
			}
			if hi[m] > best.Upper {
				best.Upper = hi[m]
			}
		}
		out[b] = best
	}
	return out, local, opportunities
}
func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "usage: go run go/long_run.go <original_compact_routes.csv>")
		os.Exit(2)
	}
	panels, err := readPanels(os.Args[1])
	if err != nil {
		panic(err)
	}
	policies := []string{"incident_avoid", "state_direction", "unrestricted"}
	budgets := []int{0, 1, 2, 4, 8, 12}
	results := map[string]interface{}{}
	details := []map[string]interface{}{}
	for _, policy := range policies {
		totals := map[int]Bounds{}
		local := Bounds{}
		opp := 0
		for _, p := range panels {
			bb, loc, o := computePanel(p, policy)
			for _, b := range budgets {
				t := totals[b]
				t.Lower += bb[b].Lower
				t.Upper += bb[b].Upper
				totals[b] = t
			}
			local.Lower += loc.Lower
			local.Upper += loc.Upper
			opp += o
			details = append(details, map[string]interface{}{"session": p.Session, "group": p.Group, "stage": p.Stage, "info": p.Info, "policy": policy, "budgets": bb, "rectangular": loc})
		}
		summary := map[string]interface{}{}
		for _, b := range budgets {
			v := totals[b]
			summary[strconv.Itoa(b)] = map[string]interface{}{"lower_total": v.Lower, "upper_total": v.Upper, "lower_mean_group_round": float64(v.Lower) / 480, "upper_mean_group_round": float64(v.Upper) / 480}
		}
		results[policy] = map[string]interface{}{"per_person_lifetime_max_changes_per_20_rounds": 1, "per_round_max_changes": 1, "opportunity_events": opp, "source_rectangular": map[string]interface{}{"lower_total": local.Lower, "upper_total": local.Upper, "lower_mean": float64(local.Lower) / 480, "upper_mean": float64(local.Upper) / 480}, "panels_budget_B": summary}
	}
	output := map[string]interface{}{"experiment": "Wijayaratna et al 2017 actual historical human route profiles (not advice uptake)", "identity": "stable subject slot within EACH original group-treatment panel; switch slot <=1 per treatment; reset at treatment boundary", "design": "FROZEN historical future trajectories; max one hypothetical C-branch reversal per round and person per treatment; total per-panel B constrained; counterfactual group feedback and re-optimization suppressed by assumption", "n_sessions": 6, "n_treatment_panels": len(panels), "n_group_rounds": 480, "result": results, "panels": details, "status": "STRICTLY CONDITIONAL RESPONSE SET, NOT EMPIRICAL CAUSAL WELFARE"}
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	if err := enc.Encode(output); err != nil {
		panic(strings.TrimSpace(err.Error()))
	}
}
