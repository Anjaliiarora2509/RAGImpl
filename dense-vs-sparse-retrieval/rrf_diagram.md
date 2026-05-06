# Reciprocal Rank Fusion — Visual Walkthrough

## The Full Picture

```
                        USER QUERY
                "What is the refund policy?"
                            │
               ┌────────────┴────────────┐
               │                         │
               ▼                         ▼
     ┌──────────────────┐     ┌──────────────────────┐
     │  DENSE RETRIEVAL │     │   SPARSE RETRIEVAL   │
     │  (all-MiniLM)    │     │       (BM25)         │
     │                  │     │                      │
     │ Embeds query into│     │ Tokenizes query into │
     │ 384 numbers and  │     │ words and finds exact│
     │ finds closest    │     │ word matches in docs │
     │ vectors          │     │                      │
     └────────┬─────────┘     └──────────┬───────────┘
              │                          │
              ▼                          ▼
     ┌──────────────────┐     ┌──────────────────────┐
     │   DENSE RANKED   │     │    BM25 RANKED LIST  │
     │      LIST        │     │                      │
     │                  │     │  1. Chunk C  (exact  │
     │  1. Chunk A      │     │     "refund" found)  │
     │  2. Chunk B      │     │  2. Chunk A          │
     │  3. Chunk C      │     │  3. Chunk D          │
     │  4. Chunk D      │     │  4. Chunk B          │
     └────────┬─────────┘     └──────────┬───────────┘
              │                          │
              └────────────┬─────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   RRF SCORE FORMULA    │
              │                        │
              │  score = 1 / (60 + rank)│
              │                        │
              │  Add score from BOTH   │
              │  lists for each chunk  │
              └────────────┬───────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                    RRF CALCULATION                        │
│                                                          │
│  Chunk A → dense rank 1,  bm25 rank 2                   │
│          = 1/(60+1)     + 1/(60+2)                       │
│          = 0.0164       + 0.0161      = 0.0325  ✓ best   │
│                                                          │
│  Chunk C → dense rank 3,  bm25 rank 1                   │
│          = 1/(60+3)     + 1/(60+1)                       │
│          = 0.0159       + 0.0164      = 0.0323           │
│                                                          │
│  Chunk B → dense rank 2,  bm25 rank 4                   │
│          = 1/(60+2)     + 1/(60+4)                       │
│          = 0.0161       + 0.0156      = 0.0317           │
│                                                          │
│  Chunk D → dense rank 4,  bm25 rank 3                   │
│          = 1/(60+4)     + 1/(60+3)                       │
│          = 0.0156       + 0.0159      = 0.0315           │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │    FINAL MERGED LIST   │
              │                        │
              │  1. Chunk A  (0.0325)  │ ← high in BOTH
              │  2. Chunk C  (0.0323)  │ ← #1 in BM25
              │  3. Chunk B  (0.0317)  │
              │  4. Chunk D  (0.0315)  │
              └────────────┬───────────┘
                           │
                           ▼
                    TOP-K CHUNKS
                  passed to LLM as
                      context
```

---

## Why Chunk A Wins

```
              Dense only          BM25 only         Hybrid (RRF)
              ──────────          ─────────          ────────────
  Rank 1 →   Chunk A  ✓          Chunk C            Chunk A  ✓
  Rank 2 →   Chunk B             Chunk A            Chunk C
  Rank 3 →   Chunk C             Chunk D            Chunk B
  Rank 4 →   Chunk D             Chunk B            Chunk D
```

Chunk A was not #1 in either list alone — but it was near the top in **both**. RRF rewards this consistency.

---

## The rrf_k = 60 Sensitivity Dial

```
          Score curve for rank positions

  0.10 ┤
       │  k=10 ──────╮
  0.08 ┤              ╲
       │               ╲
  0.06 ┤                ╲
       │                 ╲___________
  0.04 ┤                              ╲____
       │   k=60 ────────────────────────────╲____
  0.02 ┤
       │
  0.00 └──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──
          1  2  3  4  5  6  7  8  9  10
                      rank

  k=10 → steep curve  → rank #1 dominates heavily
  k=60 → flat curve   → all ranks contribute fairly
```

---

## Real Query on Your Emirates Ticket

```
Query: "What is ticket number 176 2206583771?"

Dense retrieval                    BM25 retrieval
───────────────                    ──────────────
1. Chunk about "ticket receipt"    1. Chunk with "176 2206583771" ← exact match
2. Chunk about "booking ref"       2. Chunk about "ticket number"
3. Chunk about "fare information"  3. Chunk about "scan barcode"
4. Chunk about "baggage"           4. Chunk about "booking ref"

                    RRF merges both
                          ↓
           1. Chunk with "176 2206583771"  ← wins
              (BM25 rank 1 + decent dense rank)
```

Dense alone might return the wrong chunk. BM25 finds the exact number. RRF puts the right chunk at the top.
