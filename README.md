# NHL Goal Scorer Predictor

Samouczący się system typowania strzelców bramek NHL.

## Co robi system

- Przewiduje najbardziej prawdopodobnych strzelców na dany dzień
- Uwzględnia formę (Hot Hand), rolę w PP, jakość linii, matchup, residual xG, zmęczenie i kontekst meczu
- Wykrywa **Second Line Edge** (gdy druga linia ma większą szansę niż pierwsza)
- Uczy się na błędach i aktualizuje wagi

## Aktualne wagi

- form: 0.13
- role_pp: 0.24
- matchup: 0.16
- line_quality: 0.17
- residual: 0.08
- hidden_edge: 0.07
- context: 0.15

## Struktura

- `src/scoring/` – silnik scoringu + logika L2
- `src/ranking/` – generator rankingu
- `config/weights.yaml` – aktualne wagi
- `scripts/` – skrypty uruchomieniowe

## Status

W budowie – core scoring engine działa.
