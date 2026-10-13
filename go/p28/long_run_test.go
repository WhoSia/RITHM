package main

import (
	"os"
	"path/filepath"
	"testing"
)

func TestGeometry(t *testing.T) {
	if cost(6, 0, 0) != 192 || cost(6, 0, 1) != 192 {
		t.Fatal("original no C-B costs")
	}
	for n1 := 0; n1 <= 12; n1++ {
		for n2 := 1; n2 <= 12-n1; n2++ {
			if cost(n1, n2, 1)-cost(n1, n2-1, 1) <= 0 {
				t.Fatal("incident C-B avoidance must save cost")
			}
		}
	}
}
func TestPerPersonBudgetBlocksRepeats(t *testing.T) {
	var p Panel
	for round := 0; round < 20; round++ {
		for i := 0; i < 12; i++ {
			p.Routes[round][i] = 1
		}
	}
	p.Routes[0][0] = 2
	p.Routes[1][0] = 2
	p.Incident[0] = 1
	p.Incident[1] = 1
	r, rect, _ := computePanel(p, "incident_avoid")
	if r[12].Upper != 33 || rect.Upper != 66 {
		t.Fatalf("expected one person once 33 vs independent 66 got %v %v", r[12], rect)
	}
}
func TestOriginalSourceMultiRoundBounds(t *testing.T) {
	path := filepath.Join("..", "data", "rithm23_wijayaratna2017_routes.csv")
	if _, err := os.Stat(path); err != nil {
		path = "../../source_routes_compact_LOCAL_ONLY.csv"
	}
	p, err := readPanels(path)
	if err != nil {
		t.Fatal(err)
	}
	if len(p) != 24 {
		t.Fatal("panels")
	}
	incident, p27, opp := 0, 0, 0
	lo, hi := 0, 0
	for _, pp := range p {
		r, rect, n := computePanel(pp, "incident_avoid")
		incident += r[12].Upper
		p27 += rect.Upper
		opp += n
		lo += r[12].Lower
		hi += r[2].Upper
	}
	if incident != 1053 || p27 != 1072 || opp != 112 || lo != 0 || hi != 642 {
		t.Fatalf("wrong source receipts incident=%d p27=%d opportunity=%d lower=%d B2=%d", incident, p27, opp, lo, hi)
	}
}
func TestMonotoneBudgetAndRectangular(t *testing.T) {
	path := "../../source_routes_compact_LOCAL_ONLY.csv"
	if _, err := os.Stat(path); err != nil {
		path = "../../data/rithm23_wijayaratna2017_routes.csv"
	}
	panels, err := readPanels(path)
	if err != nil {
		t.Fatal(err)
	}
	for _, p := range panels {
		for _, policy := range []string{"unrestricted", "incident_avoid", "state_direction"} {
			r, rect, _ := computePanel(p, policy)
			last := r[0]
			for _, b := range []int{1, 2, 4, 8, 12} {
				now := r[b]
				if now.Lower > last.Lower || now.Upper < last.Upper || now.Lower < rect.Lower || now.Upper > rect.Upper {
					t.Fatalf("nonmonotone bounds policy %s budget %d", policy, b)
				}
				last = now
			}
		}
	}
}
