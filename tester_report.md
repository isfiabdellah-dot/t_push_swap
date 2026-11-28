<pre><b>== 2. INVALID INPUT  (must print exactly &apos;Error\n&apos; on stderr, nothing on stdout, non-zero exit) ==</b>
  [<font color="#26A269">PASS</font>] 50/50 invalid-input cases rejected correctly
  [<font color="#26A269">PASS</font>] no argument -&gt; no output, exit 0, prompt back
  [<font color="#2AA1B3">INFO</font>] tab inside argument &apos;1\t2&apos; - rejected with Error (subject does not define tabs)
  [<font color="#2AA1B3">INFO</font>] tab inside argument &apos;3 2\t1&apos; - rejected with Error (subject does not define tabs)

<b>== 3. VALID INPUT PARSING  (must be accepted and sorted) ==</b>
  [<font color="#26A269">PASS</font>] single number
  [<font color="#26A269">PASS</font>] single 0
  [<font color="#26A269">PASS</font>] single INT_MIN
  [<font color="#26A269">PASS</font>] single INT_MAX
  [<font color="#26A269">PASS</font>] INT_MIN INT_MAX 0
  [<font color="#26A269">PASS</font>] INT_MAX INT_MIN
  [<font color="#26A269">PASS</font>] negatives
  [<font color="#26A269">PASS</font>] INT_MIN+1..
  [<font color="#26A269">PASS</font>] two numbers
  [<font color="#26A269">PASS</font>] 0 and -1
  [<font color="#26A269">PASS</font>] explicit plus sign (+3 2 1)
  [<font color="#26A269">PASS</font>] leading zeros (007 3 -01)
  [<font color="#26A269">PASS</font>] all numbers in ONE quoted argument
  [<font color="#26A269">PASS</font>] several numbers per argument
  [<font color="#26A269">PASS</font>] extra spaces in a quoted argument
  [<font color="#26A269">PASS</font>] -0 as a number
  [<font color="#26A269">PASS</font>] INT_MIN as string
  [<font color="#26A269">PASS</font>] INT_MAX with +
  [<font color="#26A269">PASS</font>] many leading zeros

<b>== 4. EXHAUSTIVE: every permutation of 1..7 in every mode ==</b>
  [<font color="#26A269">PASS</font>] default: all 5913 permutations of n&lt;=7 sorted (worst 33 ops)
  [<font color="#26A269">PASS</font>] simple: all 5913 permutations of n&lt;=7 sorted (worst 26 ops)
  [<font color="#26A269">PASS</font>] medium: all 5913 permutations of n&lt;=7 sorted (worst 25 ops)
  [<font color="#26A269">PASS</font>] complex: all 5913 permutations of n&lt;=7 sorted (worst 33 ops)
  [<font color="#26A269">PASS</font>] adaptive: all 5913 permutations of n&lt;=7 sorted (worst 33 ops)
  [<font color="#A2734C">WARN</font>] default tiny-input efficiency: worst n=2 -&gt; 3 op(s) (optimum 1), n=3 -&gt; 10 (optimum 2), n=5 -&gt; 25 (good &lt;= 12) - subject: &apos;smallest list of operations possible&apos;; hard-code n&lt;=5 for a cheap win
  [<font color="#A2734C">WARN</font>] adaptive tiny-input efficiency: worst n=2 -&gt; 3 op(s) (optimum 1), n=3 -&gt; 10 (optimum 2), n=5 -&gt; 25 (good &lt;= 12) - subject: &apos;smallest list of operations possible&apos;; hard-code n&lt;=5 for a cheap win

<b>== 5. RANDOM INPUTS: correctness for many sizes in every mode ==</b>
1 5 7 9 44 6 0
  [<font color="#C01C28"><b>FAIL</b></font>] default: 2/90 random runs wrong (sizes [2]) - TIMEOUT (timeout)
         repro: ./push_swap -423222 -486425
  [<font color="#26A269">PASS</font>] simple: 90/90 random runs sorted correctly
  [<font color="#26A269">PASS</font>] medium: 90/90 random runs sorted correctly
  [<font color="#C01C28"><b>FAIL</b></font>] complex: 1/90 random runs wrong (sizes [2]) - TIMEOUT (timeout)
         repro: ./push_swap --complex -128391 -234770
  [<font color="#C01C28"><b>FAIL</b></font>] adaptive: 1/90 random runs wrong (sizes [3]) - TIMEOUT (timeout)
         repro: ./push_swap --adaptive -261862 -867521

<b>== 6. SPECIAL SHAPES (sorted, reversed, rotated, nearly sorted, extremes ...)  - sorted input must print NOTHING ==</b>
  [<font color="#C01C28"><b>FAIL</b></font>] complex: TIMEOUT in 5 shape case(s) - e.g. n=3 all-negative, n=5 all-negative, n=10 all-negative, n=100 all-negative, n=500 all-negative
         repro: ./push_swap --complex -460089 -919152
  [<font color="#C01C28"><b>FAIL</b></font>] default: TIMEOUT in 1 shape case(s) - e.g. n=5 all-negative
         repro: ./push_swap -209261 -277142
  [<font color="#C01C28"><b>FAIL</b></font>] adaptive: TIMEOUT in 1 shape case(s) - e.g. n=5 all-negative
         repro: ./push_swap --adaptive -209261 -277142
  [<font color="#2AA1B3">INFO</font>] 328 of 335 shape/mode combinations fine

<b>== 7. OUTPUT HYGIENE &amp; WASTE (analysis of the instruction streams) ==</b>
  [<font color="#C01C28"><b>FAIL</b></font>] output format (one op per line, &apos;\n&apos; only, valid names) - complex: TIMEOUT (timeout)
  [<font color="#26A269">PASS</font>] no no-op instructions printed (pa on empty b, ra on 1 element ...)
  [<font color="#A2734C">WARN</font>] no cancelling pairs (ra rra, pa pb ...) - wasted pairs: default=65 (0.2%), simple=24 (0.0%), medium=7 (0.0%), complex=155 (0.5%), adaptive=65 (0.2%) -&gt; add a peephole pass that deletes them
  [<font color="#A2734C">WARN</font>] combined instructions ss/rr/rrr are used - never emitted in: default, simple, medium, complex, adaptive (adjacent ra+rb / rra+rrb pairs found: default=0, simple=0, medium=0, complex=0, adaptive=0); restructure so both stacks rotate together and emit rr/rrr
  [<font color="#26A269">PASS</font>] stdout carries only operations (n=500), stderr empty

<b>== 8. FLAGS  (--simple --medium --complex --adaptive, position &amp; combinations) ==</b>
  [<font color="#26A269">PASS</font>] --simple accepted and sorts the subject example
  [<font color="#26A269">PASS</font>] --medium accepted and sorts the subject example
  [<font color="#26A269">PASS</font>] --complex accepted and sorts the subject example
  [<font color="#26A269">PASS</font>] --adaptive accepted and sorts the subject example
  [<font color="#26A269">PASS</font>] subject example `./push_swap 2 1 3 6 5 8` sorts (subject shows 15 ops, here 16)
  [<font color="#26A269">PASS</font>] subject example `--adaptive 4 67 3 87 23 | wc -l` (subject: 13) -&gt; 13 ops
  [<font color="#2AA1B3">INFO</font>] flag AFTER the numbers (`1 2 3 --simple`) - rejected with Error
  [<font color="#2AA1B3">INFO</font>] two strategy flags (`--simple --medium ...`) - rejected
  [<font color="#C01C28"><b>FAIL</b></font>] `--bench --adaptive N...` (the subject&apos;s own example) accepted - rc=1 stderr=&apos;Error\n&apos;
         repro: ./push_swap --bench --adaptive 4 67 3 87 23
  [<font color="#C01C28"><b>FAIL</b></font>] `--adaptive --bench N...` accepted - rc=1 stderr=&apos;Error\n&apos;
  [<font color="#C01C28"><b>FAIL</b></font>] `--bench N...` alone accepted (default strategy) - rc=1 stderr=&apos;Error\n&apos;
  [<font color="#26A269">PASS</font>] --simple works for tiny/sorted inputs (&apos;any selector flag must work regardless of size or disorder&apos;)
  [<font color="#26A269">PASS</font>] --medium works for tiny/sorted inputs (&apos;any selector flag must work regardless of size or disorder&apos;)
  [<font color="#26A269">PASS</font>] --complex works for tiny/sorted inputs (&apos;any selector flag must work regardless of size or disorder&apos;)
  [<font color="#26A269">PASS</font>] --adaptive works for tiny/sorted inputs (&apos;any selector flag must work regardless of size or disorder&apos;)

<b>== 9. --bench MODE  (report on stderr only: disorder %, strategy/complexity, total, per-op counts) ==</b>
  [<font color="#C01C28"><b>FAIL</b></font>] --bench implemented - rc=1, stderr=&apos;Error\n&apos; - benchmark mode is mandatory in v1.2 (see subject VI.5)
         repro: ./push_swap --bench 3 2 1
  [<font color="#2AA1B3">INFO</font>] remaining --bench checks - skipped

<b>== 10. PERFORMANCE vs the subject&apos;s thresholds (100 numbers: &lt;2000 pass, &lt;1500 good, &lt;700 excellent; 500: &lt;12000 / &lt;8000 / &lt;5500) ==</b>
  [<font color="#26A269">PASS</font>] default n=100  min 723  avg 945  max 1084 | worst-case grade: good, average grade: good
  [<font color="#A2734C">WARN</font>] default n=500  min 6784  avg 7518  max 8241 | worst-case grade: pass, average grade: good - evaluator will run several random lists: aim for worst-case &lt;8000
  [<font color="#2AA1B3">INFO</font>] simple n=100  min 1233  avg 1444  max 1601 | worst-case grade: pass, average grade: good
  [<font color="#A2734C">WARN</font>] simple n=500  min 29126  avg 32147  max 33643 | worst-case grade: FAIL, average grade: FAIL - this forced strategy alone exceeds the &apos;pass&apos; limit (acceptable only if the default/adaptive mode does not use it here)
  [<font color="#2AA1B3">INFO</font>] medium n=100  min 711  avg 767  max 833 | worst-case grade: good, average grade: good
  [<font color="#2AA1B3">INFO</font>] medium n=500  min 7881  avg 8100  max 8337 | worst-case grade: pass, average grade: pass
  [<font color="#2AA1B3">INFO</font>] complex n=100  min 1084  avg 1084  max 1084 | worst-case grade: good, average grade: good
  [<font color="#2AA1B3">INFO</font>] complex n=500  min 6784  avg 6784  max 6784 | worst-case grade: good, average grade: good
  [<font color="#26A269">PASS</font>] adaptive n=100  min 731  avg 970  max 1084 | worst-case grade: good, average grade: good
  [<font color="#A2734C">WARN</font>] adaptive n=500  min 6784  avg 7625  max 8235 | worst-case grade: pass, average grade: good - evaluator will run several random lists: aim for worst-case &lt;8000

<b>== 11. COMPLEXITY CHECK (empirical exponent of #ops ~ n^k on random input, n = 200..2000) ==</b>
  [<font color="#26A269">PASS</font>] simple: measured exponent 1.98 (O(n^2) expected k~2)  [200:5245, 400:20906, 800:80521, 1600:324424]
  [<font color="#26A269">PASS</font>] medium: measured exponent 1.47 (O(n*sqrt n) expected k~1.5)  [200:2110, 400:5698, 800:16121, 1600:43923, 3200:123503]
  [<font color="#26A269">PASS</font>] complex: measured exponent 1.14 (O(n log n) expected k~1.1)  [200:2468, 400:5536, 800:12272, 1600:26944, 3200:58688]
  [<font color="#26A269">PASS</font>] at n=1000 complex (15068) should not be slower than medium (21923)

<b>== 12. ADAPTIVE MODE: does it pick well for each disorder band?  (&lt;0.2 / 0.2-0.5 / &gt;=0.5) ==</b>
  [<font color="#26A269">PASS</font>] low  [0.00,0.20) n=100: adaptive 425 vs simple 425 / medium 407 / complex 852
  [<font color="#A2734C">WARN</font>] low  [0.00,0.20) n=300: adaptive 3665 vs simple 3665 / medium 2594 / complex 4220 - adaptive uses 41% more ops than the best available strategy for this regime: the dispatch/threshold is not helping
  [<font color="#26A269">PASS</font>] mid  [0.20,0.50) n=100: adaptive 710 vs simple 1169 / medium 710 / complex 1084
  [<font color="#26A269">PASS</font>] mid  [0.20,0.50) n=300: adaptive 3640 vs simple 9811 / medium 3640 / complex 4220
  [<font color="#A2734C">WARN</font>] high [0.50,1.00] n=100: adaptive 1084 vs simple 1458 / medium 775 / complex 1084 - adaptive uses 40% more ops than the best available strategy for this regime: the dispatch/threshold is not helping
  [<font color="#26A269">PASS</font>] high [0.50,1.00] n=300: adaptive 4220 vs simple 12024 / medium 3830 / complex 4220

<b>== 13. MEMORY: valgrind leak check on valid inputs AND on every error path ==</b>
  [<font color="#26A269">PASS</font>] 58/58 runs free all memory with no invalid access

<b>== 14. ROBUSTNESS &amp; SPEED ==</b>
  [<font color="#26A269">PASS</font>] n=1000 default   15068 ops in 0.02s
  [<font color="#26A269">PASS</font>] n=1000 medium    22147 ops in 0.03s
  [<font color="#26A269">PASS</font>] n=1000 complex   15068 ops in 0.02s
  [<font color="#26A269">PASS</font>] n=5000 default  100196 ops in 0.49s
  [<font color="#26A269">PASS</font>] n=5000 medium   239695 ops in 1.11s
  [<font color="#26A269">PASS</font>] n=5000 complex  100196 ops in 0.46s
  [<font color="#26A269">PASS</font>] n=10000 default  215392 ops in 1.86s
  [<font color="#A2734C">WARN</font>] n=10000 medium   674024 ops in 5.71s - slow: &gt;3 s (is ranking/ft_index O(n) per lookup? each write() a syscall?)
  [<font color="#26A269">PASS</font>] n=10000 complex  215392 ops in 1.85s
  [<font color="#26A269">PASS</font>] 500 numbers in ONE quoted argument
  [<font color="#26A269">PASS</font>] duplicate of the LAST element in 501 args detected
  [<font color="#26A269">PASS</font>] duplicate in the middle of 500 numbers detected
  [<font color="#26A269">PASS</font>] deterministic output (same input twice)
  [<font color="#26A269">PASS</font>] INT_MAX / INT_MIN mixed with small values (n=100)
  [<font color="#26A269">PASS</font>] works with an empty environment
  [<font color="#26A269">PASS</font>] does not read stdin / does not need a particular cwd
  [<font color="#26A269">PASS</font>] write failure (stdout=/dev/full) does not crash

<b>==============================================================================</b>
<b>SUMMARY</b>
  section      PASS   FAIL   WARN   INFO
  parse           2      0      0      2
  valid          19      0      0      0
  perms           5      0 <font color="#A2734C">2</font>      0
  random          2 <font color="#C01C28"><b>3</b></font>      0      0
  shapes          0 <font color="#C01C28"><b>3</b></font>      0      1
  hygiene         2 <font color="#C01C28"><b>1</b></font> <font color="#A2734C">2</font>      0
  flags          10 <font color="#C01C28"><b>3</b></font>      0      2
  bench           0 <font color="#C01C28"><b>1</b></font>      0      1
  perf            2      0 <font color="#A2734C">3</font>      5
  scale           4      0      0      0
  adaptive        4      0 <font color="#A2734C">2</font>      0
  memory          1      0      0      0
  robust         16      0 <font color="#A2734C">1</font>      0

<b>WEAKNESSES TO FIX FIRST (FAIL = breaks the subject)</b>
   1. [random] default: 2/90 random runs wrong (sizes [2])
        TIMEOUT (timeout)
        repro: ./push_swap -423222 -486425
   2. [random] complex: 1/90 random runs wrong (sizes [2])
        TIMEOUT (timeout)
        repro: ./push_swap --complex -128391 -234770
   3. [random] adaptive: 1/90 random runs wrong (sizes [3])
        TIMEOUT (timeout)
        repro: ./push_swap --adaptive -261862 -867521
   4. [shapes] complex: TIMEOUT in 5 shape case(s)
        e.g. n=3 all-negative, n=5 all-negative, n=10 all-negative, n=100 all-negative, n=500 all-negative
        repro: ./push_swap --complex -460089 -919152
   5. [shapes] default: TIMEOUT in 1 shape case(s)
        e.g. n=5 all-negative
        repro: ./push_swap -209261 -277142
   6. [shapes] adaptive: TIMEOUT in 1 shape case(s)
        e.g. n=5 all-negative
        repro: ./push_swap --adaptive -209261 -277142
   7. [hygiene] output format (one op per line, &apos;\n&apos; only, valid names)
        complex: TIMEOUT (timeout)
   8. [flags] `--bench --adaptive N...` (the subject&apos;s own example) accepted
        rc=1 stderr=&apos;Error\n&apos;
        repro: ./push_swap --bench --adaptive 4 67 3 87 23
   9. [flags] `--adaptive --bench N...` accepted
        rc=1 stderr=&apos;Error\n&apos;
  10. [flags] `--bench N...` alone accepted (default strategy)
        rc=1 stderr=&apos;Error\n&apos;
  11. [bench] --bench implemented
        rc=1, stderr=&apos;Error\n&apos; - benchmark mode is mandatory in v1.2 (see subject VI.5)
        repro: ./push_swap --bench 3 2 1

<b>WEAKNESSES TO IMPROVE (WARN)</b>
   1. [perms] default tiny-input efficiency: worst n=2 -&gt; 3 op(s) (optimum 1), n=3 -&gt; 10 (optimum 2), n=5 -&gt; 25 (good &lt;= 12)
        subject: &apos;smallest list of operations possible&apos;; hard-code n&lt;=5 for a cheap win
   2. [perms] adaptive tiny-input efficiency: worst n=2 -&gt; 3 op(s) (optimum 1), n=3 -&gt; 10 (optimum 2), n=5 -&gt; 25 (good &lt;= 12)
        subject: &apos;smallest list of operations possible&apos;; hard-code n&lt;=5 for a cheap win
   3. [hygiene] no cancelling pairs (ra rra, pa pb ...)
        wasted pairs: default=65 (0.2%), simple=24 (0.0%), medium=7 (0.0%), complex=155 (0.5%), adaptive=65 (0.2%) -&gt; add a peephole pass that deletes them
   4. [hygiene] combined instructions ss/rr/rrr are used
        never emitted in: default, simple, medium, complex, adaptive (adjacent ra+rb / rra+rrb pairs found: default=0, simple=0, medium=0, complex=0, adaptive=0); restructure so both stacks rotate together and emit rr/rrr
   5. [perf] default n=500  min 6784  avg 7518  max 8241 | worst-case grade: pass, average grade: good
        evaluator will run several random lists: aim for worst-case &lt;8000
   6. [perf] simple n=500  min 29126  avg 32147  max 33643 | worst-case grade: FAIL, average grade: FAIL
        this forced strategy alone exceeds the &apos;pass&apos; limit (acceptable only if the default/adaptive mode does not use it here)
   7. [perf] adaptive n=500  min 6784  avg 7625  max 8235 | worst-case grade: pass, average grade: good
        evaluator will run several random lists: aim for worst-case &lt;8000
   8. [adaptive] low  [0.00,0.20) n=300: adaptive 3665 vs simple 3665 / medium 2594 / complex 4220
        adaptive uses 41% more ops than the best available strategy for this regime: the dispatch/threshold is not helping
   9. [adaptive] high [0.50,1.00] n=100: adaptive 1084 vs simple 1458 / medium 775 / complex 1084
        adaptive uses 40% more ops than the best available strategy for this regime: the dispatch/threshold is not helping
  10. [robust] n=10000 medium   674024 ops in 5.71s
        slow: &gt;3 s (is ranking/ft_index O(n) per lookup? each write() a syscall?)

<font color="#C01C28"><b>NOT READY</b></font>  (11 FAIL, 10 WARN, 99 tests)
elapsed 478.6s</pre>