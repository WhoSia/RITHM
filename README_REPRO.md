# RITHM-2.3 exact network-welfare replication

Status: exploratory, six already-inspected lab sessions. No causal claims.

Data: compact derivative of Wijayaratna et al. (2017), DOI 10.1371/journal.pone.0184191.s002, licensed CC BY 4.0. Original author workbook remains the source of record. Two source-derived 2017 route/cost CSVs are in `data/`. The 2023 Ashraf individual author CSV is not distributed here.

Commands:

```
python rithm23_welfare_bridge.py
PYTHONPATH=. python -m unittest discover -s tests -p 'test_*.py' -v
```

2017 source: 5,760 individual observations; 47 cost disagreements with the network formula across six group-rounds; 480 structural social costs reconstruct the PLOS published TSTC means (NoInfo 210.629, Info 219.163 rounded three decimals).

The exact mean-cost identity:
`E[C] = C(E[n1],E[n2],E[z]) + Var(n1) + Var(n3) + 19 Cov(z,n2)`.

Notice: the code runs with Python numpy/pandas and stdlib. Five core tests run offline without the 2023 author CSV. The optional sixth test uses the user's separately supplied original 2023 author CSV when present.

No GitHub Actions execution required or performed for this work. RITHM-2.4 name is only a proposal in the scientific report.
