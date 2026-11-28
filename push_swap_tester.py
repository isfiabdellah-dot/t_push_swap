#!/usr/bin/env python3
"""
push_swap_tester.py - stress tester / weakness detector for a 42 push_swap (v1.2: --simple/--medium/
--complex/--adaptive/--bench).  Python 3.8+, standard library only.  Does NOT need a Makefile and
does NOT need the school's checker (a built-in checker replays every operation list).

USAGE
    python3 push_swap_tester.py [SRC_DIR]            # compile every .c under SRC_DIR (default ".") and test
    python3 push_swap_tester.py --bin ./push_swap    # test an already-built binary
    options:  --quick | --full   (default: normal)     --seed N      --jobs N
              --no-valgrind  --no-asan  --no-norm      --only SECTION[,SECTION]   --report FILE
    sections: build parse valid perms random shapes hygiene flags bench perf scale adaptive memory robust

WHAT IT REPORTS
    FAIL  violates the subject (wrong result, crash, wrong error text, missing flag ...)
    WARN  weakness (leak, poor operation count, wasted instructions, slow, unclear behaviour)
    INFO  observation
Every failing sorting test is shrunk to a minimal reproducing input and printed as a command line.
Exit code: 0 if no FAIL, 1 otherwise.
"""
import argparse, collections, itertools, math, os, random, re, shutil, statistics
import subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor

INT_MIN, INT_MAX = -2**31, 2**31 - 1
OPS = ["sa", "sb", "ss", "pa", "pb", "ra", "rb", "rr", "rra", "rrb", "rrr"]
MODES = collections.OrderedDict([
    ("default", []), ("simple", ["--simple"]), ("medium", ["--medium"]),
    ("complex", ["--complex"]), ("adaptive", ["--adaptive"])])
ALL_SECTIONS = ["build", "parse", "valid", "perms", "random", "shapes", "hygiene", "flags",
                "bench", "perf", "scale", "adaptive", "memory", "robust"]

# ----------------------------------------------------------------------------- output helpers
USE_COLOR = sys.stdout.isatty()
def c(code, s): return "\033[%sm%s\033[0m" % (code, s) if USE_COLOR else s
COL = {"PASS": "32", "FAIL": "31;1", "WARN": "33", "INFO": "36"}

class Result:
    def __init__(s, cat, name, status, detail="", repro=None):
        s.cat, s.name, s.status, s.detail, s.repro = cat, name, status, detail, repro
RESULTS = []
def rec(cat, name, status, detail="", repro=None):
    RESULTS.append(Result(cat, name, status, detail, repro))
    tag = c(COL[status], "%-4s" % status)
    if status != "PASS" or ARGS.verbose:
        print("  [%s] %s%s" % (tag, name, (" - " + detail.split("\n")[0]) if detail else ""))
        for extra in detail.split("\n")[1:]:
            print("         " + extra)
        if repro:
            print("         repro: " + repro)
    else:
        print("  [%s] %s" % (tag, name))
def section(title): print("\n" + c("1", "== %s ==" % title))
def shq(a):
    a = str(a)
    return a if re.fullmatch(r"[A-Za-z0-9_./=+-]+", a) else "'" + a.replace("'", "'\\''") + "'"
def cmdline(args): return "./push_swap " + " ".join(shq(a) for a in args)

# ----------------------------------------------------------------------------- process helpers
class Run:
    def __init__(s, rc, out, err, dt): s.rc, s.out, s.err, s.dt = rc, out, err, dt
    @property
    def crashed(s): return s.rc is None or s.rc < 0
    def why_crash(s):
        if s.rc is None: return "timeout"
        return "killed by signal %d" % -s.rc
def run(args, timeout=20, binp=None, env=None):
    t = time.time()
    try:
        p = subprocess.run([binp or BIN] + [str(a) for a in args], capture_output=True,
                           timeout=timeout, env=env)
        return Run(p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace"), time.time() - t)
    except subprocess.TimeoutExpired:
        return Run(None, "", "TIMEOUT", timeout)
def pmap(fn, items):
    with ThreadPoolExecutor(max_workers=ARGS.jobs) as ex:
        return list(ex.map(fn, items))

# ----------------------------------------------------------------------------- the checker
def parse_ops(out):
    """-> (ops, problem or None)"""
    if out == "": return [], None
    if not out.endswith("\n"): return [], "output does not end with a newline"
    lines = out[:-1].split("\n")
    for i, l in enumerate(lines):
        if l not in OPS:
            return [], "line %d is %r (not a valid operation; spaces/CR/empty lines are forbidden)" % (i + 1, l)
    return lines, None

def simulate(vals, ops):
    """replay ops. returns dict(sorted, noops, inverse, mergeable, hist)"""
    a, b = collections.deque(vals), collections.deque()
    noop = 0
    for o in ops:
        if o == "sa":
            if len(a) < 2: noop += 1
            else: a[0], a[1] = a[1], a[0]
        elif o == "sb":
            if len(b) < 2: noop += 1
            else: b[0], b[1] = b[1], b[0]
        elif o == "ss":
            if len(a) < 2 and len(b) < 2: noop += 1
            if len(a) >= 2: a[0], a[1] = a[1], a[0]
            if len(b) >= 2: b[0], b[1] = b[1], b[0]
        elif o == "pa":
            if not b: noop += 1
            else: a.appendleft(b.popleft())
        elif o == "pb":
            if not a: noop += 1
            else: b.appendleft(a.popleft())
        elif o == "ra":
            if len(a) < 2: noop += 1
            else: a.rotate(-1)
        elif o == "rb":
            if len(b) < 2: noop += 1
            else: b.rotate(-1)
        elif o == "rr":
            if len(a) < 2 and len(b) < 2: noop += 1
            a.rotate(-1) if len(a) >= 2 else None
            b.rotate(-1) if len(b) >= 2 else None
        elif o == "rra":
            if len(a) < 2: noop += 1
            else: a.rotate(1)
        elif o == "rrb":
            if len(b) < 2: noop += 1
            else: b.rotate(1)
        elif o == "rrr":
            if len(a) < 2 and len(b) < 2: noop += 1
            a.rotate(1) if len(a) >= 2 else None
            b.rotate(1) if len(b) >= 2 else None
    inv_pairs = {("ra", "rra"), ("rra", "ra"), ("rb", "rrb"), ("rrb", "rb"), ("pa", "pb"),
                 ("pb", "pa"), ("sa", "sa"), ("sb", "sb"), ("ss", "ss"), ("rr", "rrr"), ("rrr", "rr")}
    merge_pairs = {("ra", "rb"), ("rb", "ra"), ("rra", "rrb"), ("rrb", "rra"), ("sa", "sb"), ("sb", "sa")}
    inverse = sum(1 for x, y in zip(ops, ops[1:]) if (x, y) in inv_pairs)
    merge = sum(1 for x, y in zip(ops, ops[1:]) if (x, y) in merge_pairs)
    return dict(sorted=(list(a) == sorted(vals) and not b), noops=noop, inverse=inverse,
                mergeable=merge, hist=collections.Counter(ops), a_left=len(a), b_left=len(b))

def disorder_of(v):
    n = len(v)
    if n < 2: return 0.0
    m = sum(1 for i in range(n) for j in range(i + 1, n) if v[i] > v[j])
    return m / (n * (n - 1) / 2)

def solve(vals, mode="default", extra_args=()):
    """run the program and fully validate. -> (problem or None, ops, sim, Run)"""
    args = list(MODES[mode]) + list(extra_args) + [str(v) for v in vals]
    r = run(args, timeout=ARGS.timeout)
    if r.crashed: return "%s (%s)" % ("CRASH" if r.rc is not None else "TIMEOUT", r.why_crash()), [], None, r
    if r.rc != 0: return "exit code %d (stderr=%r)" % (r.rc, r.err[:40]), [], None, r
    if r.err and "--bench" not in extra_args:
        return "unexpected output on stderr: %r" % r.err[:60], [], None, r
    ops, prob = parse_ops(r.out)
    if prob: return prob, [], None, r
    sim = simulate(vals, ops)
    if not sim["sorted"]:
        return "NOT SORTED (ends with a=%d b=%d elements)" % (sim["a_left"], sim["b_left"]), ops, sim, r
    return None, ops, sim, r

def shrink(vals, mode, extra_args=(), budget=250):
    """delta-debugging: smallest sub-list that still fails"""
    fails = lambda v: bool(v) and solve(v, mode, extra_args)[0] is not None
    cur, tries = list(vals), 0
    size = max(1, len(cur) // 2)
    while size >= 1 and tries < budget:
        i, removed = 0, False
        while i < len(cur) and tries < budget:
            cand = cur[:i] + cur[i + size:]
            tries += 1
            if cand and fails(cand): cur, removed = cand, True
            else: i += size
        if not removed or size == 1: size //= 2
    return cur

# ----------------------------------------------------------------------------- generators
def rnd_list(rng, n, lo=-10**6, hi=10**6): return rng.sample(range(lo, hi), n)
def ext_list(rng, n):
    v = set([INT_MIN, INT_MAX, 0, -1, 1])
    while len(v) < n: v.add(rng.randint(INT_MIN, INT_MAX))
    v = list(v)[:n]; rng.shuffle(v); return v
def shapes(rng, n):
    s = sorted(rnd_list(rng, n))
    near = s[:]
    for _ in range(max(1, n // 20)):
        i = rng.randrange(n - 1); near[i], near[i + 1] = near[i + 1], near[i]
    k = rng.randrange(1, n) if n > 1 else 0
    pipe = s[0::2] + s[1::2][::-1]
    saw = [x for r in range(4) for x in s[r::4]]
    return collections.OrderedDict([
        ("sorted", s), ("reversed", s[::-1]), ("rotated", s[k:] + s[:k]),
        ("rotated-reversed", (s[::-1][k:] + s[::-1][:k])), ("nearly-sorted", near),
        ("organ-pipe", pipe), ("sawtooth", saw), ("all-negative", sorted([-abs(x) - 1 for x in s], key=lambda _: rng.random())),
        ("extremes", ext_list(rng, n)),
        ("swap-first-two", [s[1], s[0]] + s[2:]), ("swap-last-two", s[:-2] + [s[-1], s[-2]]),
        ("one-misplaced-min", s[1:] + s[:1]), ("one-misplaced-max", s[-1:] + s[:-1])])
def with_disorder(rng, n, lo, hi):
    base = list(range(n))
    for _ in range(3000):
        p = rng.random(); idx = [i for i in range(n) if rng.random() < p]
        vals = [base[i] for i in idx]; rng.shuffle(vals)
        v = base[:]
        for i, x in zip(idx, vals): v[i] = x
        if lo <= disorder_of(v) < hi: return v
    return None

# ----------------------------------------------------------------------------- build
def find_sources(src):
    out = []
    for r, ds, fs in os.walk(src):
        ds[:] = [d for d in ds if not d.startswith(".") and d.lower() not in ("tests", "test", "bonus", "checker", "tester", "libft_tests")]
        for f in fs:
            if f.endswith(".c") and not f.startswith(("checker", "test", "tester")) and "bonus" not in f:
                out.append(os.path.join(r, f))
    return sorted(out)

def build(src, tmp):
    global BIN
    section("1. BUILD  (Makefile ignored: every .c file under %s is compiled)" % src)
    files = find_sources(src)
    if not files:
        rec("build", "find source files", "FAIL", "no .c file found under %r" % src); return False
    rec("build", "found %d .c files" % len(files), "INFO", ", ".join(os.path.relpath(f, src) for f in files)[:300])
    mains = [f for f in files if re.search(r"\bmain\s*\(", open(f, errors="ignore").read())]
    if len(mains) != 1:
        rec("build", "exactly one main()", "FAIL", "found main() in: %s" % [os.path.relpath(m, src) for m in mains])
    strict = os.path.join(tmp, "push_swap_strict")
    p = subprocess.run(["cc", "-Wall", "-Wextra", "-Werror", "-o", strict] + files, capture_output=True, text=True, cwd=src)
    if p.returncode == 0:
        rec("build", "compiles with -Wall -Wextra -Werror", "PASS"); BIN = strict
    else:
        rec("build", "compiles with -Wall -Wextra -Werror", "FAIL", "\n".join(l.replace(src + "/", "") for l in p.stderr.strip().split("\n")[:8]))
        lax = os.path.join(tmp, "push_swap_lax")
        q = subprocess.run(["cc", "-w", "-o", lax] + files, capture_output=True, text=True, cwd=src)
        if q.returncode != 0:
            rec("build", "compiles at all", "FAIL", q.stderr[:400]); return False
        BIN = lax
        rec("build", "using a build without -Werror for the remaining tests", "INFO")
    if not ARGS.no_asan:
        asan = os.path.join(tmp, "push_swap_asan")
        q = subprocess.run(["cc", "-g", "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-w", "-o", asan] + files,
                           capture_output=True, text=True, cwd=src)
        globals()["ASAN_BIN"] = asan if q.returncode == 0 else None
        if q.returncode != 0: rec("build", "ASan/UBSan build", "INFO", "could not build: " + q.stderr[:200])
    if not ARGS.no_norm and shutil.which("norminette"):
        q = subprocess.run(["norminette", src], capture_output=True, text=True)
        errs = [l for l in q.stdout.split("\n") if l.startswith("Error")]
        files_bad = [l for l in q.stdout.split("\n") if l.endswith("Error!")]
        rec("build", "norminette", "PASS" if not errs else "WARN",
            "" if not errs else "%d error(s) in: %s" % (len(errs), ", ".join(l.split(":")[0] for l in files_bad)))
    elif not ARGS.no_norm:
        rec("build", "norminette", "INFO", "not installed (pip install norminette) - norm not checked")
    return True

# ----------------------------------------------------------------------------- sections
def expect_error(cat, label, args):
    r = run(args)
    prob = []
    if r.crashed: prob.append(r.why_crash().upper())
    else:
        if r.rc == 0: prob.append("exit code 0")
        if r.err != "Error\n": prob.append("stderr=%r (must be exactly 'Error\\n')" % r.err[:30])
        if r.out != "": prob.append("wrote %d bytes on stdout" % len(r.out))
    return (label, args, prob)

def sec_parse():
    section("2. INVALID INPUT  (must print exactly 'Error\\n' on stderr, nothing on stdout, non-zero exit)")
    big = "9" * 30
    cases = [
        ("letters", ["abc"]), ("letters among numbers", ["1", "two", "3"]), ("digit+letter", ["12a"]),
        ("letter+digit", ["a12"]), ("float", ["1.5"]), ("hex", ["0x10"]), ("only sign +", ["+"]),
        ("only sign -", ["-"]), ("double sign --5", ["--5"]), ("sign mix +-1", ["+-1"]), ("sign mix -+1", ["-+1"]),
        ("trailing sign 1-", ["1-"]), ("sign inside 1-2", ["1-2"]), ("1+2", ["1+2"]),
        ("INT_MAX+1", [str(INT_MAX + 1)]), ("INT_MIN-1", [str(INT_MIN - 1)]), ("huge", [big]), ("-huge", ["-" + big]),
        ("INT_MAX+1 in the middle", ["1", str(INT_MAX + 1), "2"]), ("4294967296", ["4294967296"]),
        ("4294967297 (wraps to 1)", ["4294967297", "5"]), ("-4294967295 (wraps to 1)", ["-4294967295", "5"]),
        ("2147483650", ["2147483650"]), ("-2147483650", ["-2147483650"]),
        ("duplicate", ["1", "1"]), ("duplicate far apart", ["3", "2", "5", "4", "1", "3"]),
        ("duplicate 0 and -0", ["0", "-0"]), ("duplicate 1 and +1", ["1", "+1"]), ("duplicate 1 and 01", ["1", "01"]),
        ("duplicate INT_MAX", [str(INT_MAX), "5", "+%d" % INT_MAX]), ("duplicate INT_MIN", [str(INT_MIN), "0", str(INT_MIN)]),
        ("duplicate inside one quoted arg", ["1 2 3 2"]), ("duplicate across quoted args", ["1 2", "3 1"]),
        ("empty string alone", [""]), ("empty string among numbers", ["1", "", "2"]), ("spaces only", [" "]),
        ("empty string with flag", ["--simple", ""]),
        ("flag with only text", ["--medium", "foo"]), ("unknown flag --foo", ["--foo", "1", "2"]),
        ("flag with bad number", ["--adaptive", "0", "one", "2", "3"]), ("flag with duplicates", ["--simple", "3", "2", "3"]),
        ("flag without numbers", ["--simple"]), ("flag only (complex)", ["--complex"]),
        ("1 2 abc quoted", ["1 2 abc"]), ("comma separated", ["1,2,3"]), ("a lone dash among numbers", ["1", "-", "2"]),
        ("non-ascii digit", ["٣"]), ("very long garbage", ["x" * 5000]),
        ("'-' then space then number", ["- 5"]), ("'+' then space then number", ["+ 5"]),
    ]
    res = pmap(lambda cs: expect_error("parse", cs[0], cs[1]), cases)
    bad = [(l, a, p) for l, a, p in res if p]
    groups = collections.OrderedDict()
    for l, a, pr in bad: groups.setdefault("; ".join(pr), []).append((l, a))
    for sig, items in groups.items():
        rec("parse", "%d/%d invalid inputs mishandled: %s" % (len(items), len(res), sig),
            "FAIL", "e.g. " + ", ".join(l for l, _ in items[:6]) + (" ..." if len(items) > 6 else ""), cmdline(items[0][1]))
    rec("parse", "%d/%d invalid-input cases rejected correctly" % (len(res) - len(bad), len(res)), "PASS" if not bad else "INFO")
    r = run([]);
    rec("parse", "no argument -> no output, exit 0, prompt back", "PASS" if (r.rc == 0 and r.out == "" and r.err == "") else "FAIL",
        "rc=%s out=%r err=%r" % (r.rc, r.out[:20], r.err[:20]), "./push_swap")
    for t in ("1\t2", "3 2\t1"):
        r = run([t]);
        rec("parse", "tab inside argument %r" % t, "INFO", "accepted" if r.rc == 0 else "rejected with Error (subject does not define tabs)")

def sec_valid():
    section("3. VALID INPUT PARSING  (must be accepted and sorted)")
    cases = [
        ("single number", [5]), ("single 0", [0]), ("single INT_MIN", [INT_MIN]), ("single INT_MAX", [INT_MAX]),
        ("INT_MIN INT_MAX 0", [INT_MIN, INT_MAX, 0]), ("INT_MAX INT_MIN", [INT_MAX, INT_MIN]),
        ("negatives", [-3, -1, -2]), ("INT_MIN+1..", [INT_MIN + 1, INT_MIN, INT_MAX - 1, INT_MAX]),
        ("two numbers", [2, 1]), ("0 and -1", [0, -1]),
    ]
    for label, v in cases:
        p, ops, sim, r = solve(v)
        rec("valid", label, "PASS" if not p else "FAIL", p or "", cmdline(v) if p else None)
    strs = [
        ("explicit plus sign (+3 2 1)", ["+3", "2", "1"], [3, 2, 1]),
        ("leading zeros (007 3 -01)", ["007", "3", "-01"], [7, 3, -1]),
        ("all numbers in ONE quoted argument", ["5 4 3 2 1"], [5, 4, 3, 2, 1]),
        ("several numbers per argument", ["5 4", "3 2", "1"], [5, 4, 3, 2, 1]),
        ("extra spaces in a quoted argument", ["  5   4  3 "], [5, 4, 3]),
        ("-0 as a number", ["-0", "5", "-5"], [0, 5, -5]),
        ("INT_MIN as string", [str(INT_MIN), "0"], [INT_MIN, 0]),
        ("INT_MAX with +", ["+%d" % INT_MAX, "0"], [INT_MAX, 0]),
        ("many leading zeros", ["0000000000000000000000000005", "3"], [5, 3]),
    ]
    for label, args, vals in strs:
        r = run(args); ops, prob = parse_ops(r.out)
        ok = (r.rc == 0 and r.err == "" and not prob and simulate(vals, ops)["sorted"])
        rec("valid", label, "PASS" if ok else "FAIL", "" if ok else "rc=%s err=%r %s" % (r.rc, r.err[:30], prob or ""), cmdline(args) if not ok else None)

def sec_perms():
    mx = 6 if ARGS.quick else 7
    section("4. EXHAUSTIVE: every permutation of 1..%d in every mode" % mx)
    for mode in MODES:
        bad_n, good_n, first, worst_all = [], 0, None, 0
        for n in range(1, mx + 1):
            perms = list(itertools.permutations(range(n)))
            res = pmap(lambda p: (p, solve(list(p), mode)), perms)
            bad = [(p, r[0]) for p, r in res if r[0]]
            if bad:
                bad_n.append("n=%d: %d/%d" % (n, len(bad), len(perms)))
                if first is None: first = (bad[0][0], bad[0][1])
            else:
                good_n += len(perms); worst_all = max([worst_all] + [len(r[1]) for p, r in res])
        if bad_n:
            small = shrink(list(first[0]), mode)
            rec("perms", "%s: permutations wrong -> %s" % (mode, ", ".join(bad_n)), "FAIL", first[1], cmdline(MODES[mode] + small))
        else:
            rec("perms", "%s: all %d permutations of n<=%d sorted (worst %d ops)" % (mode, good_n, mx, worst_all), "PASS")
    for mode in ("default", "adaptive"):
        w3 = max((len(solve(list(p), mode)[1]) for p in itertools.permutations(range(3))), default=0)
        w2 = max((len(solve(list(p), mode)[1]) for p in itertools.permutations(range(2))), default=0)
        w5 = max((len(solve(list(p), mode)[1]) for p in itertools.permutations(range(5))), default=0)
        rec("perms", "%s tiny-input efficiency: worst n=2 -> %d op(s) (optimum 1), n=3 -> %d (optimum 2), n=5 -> %d (good <= 12)" % (mode, w2, w3, w5),
            "PASS" if (w2 <= 1 and w3 <= 3 and w5 <= 12) else "WARN",
            "" if (w2 <= 1 and w3 <= 3 and w5 <= 12) else "subject: 'smallest list of operations possible'; hard-code n<=5 for a cheap win")

def sec_random():
    section("5. RANDOM INPUTS: correctness for many sizes in every mode")
    rng = random.Random(ARGS.seed)
    sizes = [2, 3, 4, 5, 6, 8, 10, 13, 20, 32, 50, 64, 100, 128, 200, 333, 500, 1000]
    reps = 3 if ARGS.quick else (8 if ARGS.full else 5)
    jobs = []
    for mode in MODES:
        for n in sizes:
            for k in range(reps):
                v = ext_list(rng, n) if (k == 0 and n >= 5) else rnd_list(rng, n, -50 * n, 50 * n) if k == 1 else rnd_list(rng, n)
                jobs.append((mode, v))
    res = pmap(lambda j: (j, solve(j[1], j[0])), jobs)
    per_mode = collections.defaultdict(list)
    for (mode, v), s in res:
        if s[0]: per_mode[mode].append((v, s[0]))
    for mode in MODES:
        tot = sum(1 for (m, v), s in res if m == mode)
        bad = per_mode.get(mode, [])
        if bad:
            v0, msg = min(bad, key=lambda t: len(t[0]))
            small = shrink(v0, mode)
            sizes_bad = sorted(set(len(v) for v, _ in bad))
            rec("random", "%s: %d/%d random runs wrong (sizes %s)" % (mode, len(bad), tot, sizes_bad[:8]), "FAIL", msg, cmdline(MODES[mode] + small))
        else:
            rec("random", "%s: %d/%d random runs sorted correctly" % (mode, tot, tot), "PASS")

def sec_shapes():
    section("6. SPECIAL SHAPES (sorted, reversed, rotated, nearly sorted, extremes ...)  - sorted input must print NOTHING")
    rng = random.Random(ARGS.seed + 1)
    groups = collections.OrderedDict()
    total = 0
    for n in (2, 3, 5, 10, 100, 500):
        tbl = shapes(rng, n) if n >= 3 else {"sorted": [1, 2], "reversed": [2, 1]}
        for name, v in tbl.items():
            for mode in MODES:
                total += 1
                p, ops, sim, r = solve(v, mode)
                if p:
                    key = (mode, p.split(" (")[0]); ex = (n, name, v)
                elif name == "sorted" and ops:
                    key = (mode, "ALREADY-SORTED input produces operations (expected none)"); ex = (n, name, v)
                else: continue
                groups.setdefault(key, []).append(ex)
    for (mode, why), items in groups.items():
        n, name, v = items[0]
        small = shrink(v, mode) if (n <= 100 and "ALREADY" not in why) else v
        shown = "e.g. " + ", ".join("n=%d %s" % (i[0], i[1]) for i in items[:5]) + (" ..." if len(items) > 5 else "")
        rec("shapes", "%s: %s in %d shape case(s)" % (mode, why, len(items)), "FAIL", shown,
            cmdline(MODES[mode] + small) if len(small) <= 40 else "(%s n=%d, generator seed %d)" % (name, n, ARGS.seed + 1))
    if not groups: rec("shapes", "all %d shape/mode combinations OK (sorted input prints nothing)" % total, "PASS")
    else: rec("shapes", "%d of %d shape/mode combinations fine" % (total - sum(len(i) for i in groups.values()), total), "INFO")

def sec_hygiene():
    section("7. OUTPUT HYGIENE & WASTE (analysis of the instruction streams)")
    rng = random.Random(ARGS.seed + 2)
    agg = {m: dict(noops=0, inverse=0, merge=0, total=0, used=collections.Counter()) for m in MODES}
    bad_fmt = []
    for mode in MODES:
        for n in (5, 20, 100, 300):
            for _ in range(3 if ARGS.quick else 6):
                v = rnd_list(rng, n); p, ops, sim, r = solve(v, mode)
                if p and "NOT SORTED" not in p: bad_fmt.append((mode, p)); continue
                if not sim: continue
                a = agg[mode]; a["noops"] += sim["noops"]; a["inverse"] += sim["inverse"]; a["merge"] += sim["mergeable"]
                a["total"] += len(ops); a["used"].update(sim["hist"])
    rec("hygiene", "output format (one op per line, '\\n' only, valid names)", "PASS" if not bad_fmt else "FAIL", "; ".join("%s: %s" % x for x in bad_fmt[:3]))
    live = {m: a for m, a in agg.items() if a["total"]}
    pct = lambda a, k: 100.0 * a[k] / a["total"]
    nz = {m: a["noops"] for m, a in live.items() if a["noops"]}
    rec("hygiene", "no no-op instructions printed (pa on empty b, ra on 1 element ...)", "PASS" if not nz else "FAIL",
        "" if not nz else "no-ops found: " + ", ".join("%s=%d" % kv for kv in nz.items()))
    cp = {m: a for m, a in live.items() if a["inverse"]}
    rec("hygiene", "no cancelling pairs (ra rra, pa pb ...)", "PASS" if not cp else "WARN",
        "" if not cp else "wasted pairs: " + ", ".join("%s=%d (%.1f%%)" % (m, a["inverse"], pct(a, "inverse")) for m, a in cp.items()) + " -> add a peephole pass that deletes them")
    unused = {m: [o for o in ("ss", "rr", "rrr") if a["used"][o] == 0] for m, a in live.items()}
    unused = {m: u for m, u in unused.items() if u}
    rec("hygiene", "combined instructions ss/rr/rrr are used", "PASS" if not unused else "WARN",
        "" if not unused else "never emitted in: " + ", ".join(unused) + " (adjacent ra+rb / rra+rrb pairs found: " +
        ", ".join("%s=%d" % (m, a["merge"]) for m, a in live.items()) + "); restructure so both stacks rotate together and emit rr/rrr")
    # trailing garbage / stream flush on large output
    v = rnd_list(rng, 500); r = run([str(x) for x in v])
    rec("hygiene", "stdout carries only operations (n=500), stderr empty", "PASS" if (r.err == "" and not parse_ops(r.out)[1]) else "FAIL", r.err[:40])

def sec_flags():
    section("8. FLAGS  (--simple --medium --complex --adaptive, position & combinations)")
    v = [4, 67, 3, 87, 23]
    for f in ("--simple", "--medium", "--complex", "--adaptive"):
        p, ops, sim, r = solve(v, f[2:])
        rec("flags", "%s accepted and sorts the subject example" % f, "PASS" if not p else "FAIL", p or "", cmdline([f] + v) if p else None)
    p, ops, sim, r = solve([2, 1, 3, 6, 5, 8])
    rec("flags", "subject example `./push_swap 2 1 3 6 5 8` sorts (subject shows 15 ops, here %d)" % len(ops), "PASS" if not p else "FAIL", p or "")
    r = run(["--adaptive"] + [str(x) for x in v]); n = len(parse_ops(r.out)[0])
    rec("flags", "subject example `--adaptive 4 67 3 87 23 | wc -l` (subject: 13) -> %d ops" % n, "PASS" if n <= 13 else "WARN",
        "" if n <= 13 else "more operations than the subject's own example")
    # position / combos
    r = run([str(x) for x in v] + ["--simple"])
    rec("flags", "flag AFTER the numbers (`1 2 3 --simple`)", "INFO", "rejected with Error" if r.rc else "accepted (rc 0)")
    r = run(["--simple", "--medium"] + [str(x) for x in v])
    rec("flags", "two strategy flags (`--simple --medium ...`)", "INFO", "rejected" if r.rc else "accepted")
    r = run(["--bench", "--adaptive"] + [str(x) for x in v]); ok = r.rc == 0 and r.out
    rec("flags", "`--bench --adaptive N...` (the subject's own example) accepted", "PASS" if ok else "FAIL",
        "" if ok else "rc=%s stderr=%r" % (r.rc, r.err[:30]), "./push_swap --bench --adaptive 4 67 3 87 23")
    r = run(["--adaptive", "--bench"] + [str(x) for x in v]); ok = r.rc == 0 and r.out
    rec("flags", "`--adaptive --bench N...` accepted", "PASS" if ok else "FAIL", "" if ok else "rc=%s stderr=%r" % (r.rc, r.err[:30]))
    r = run(["--bench"] + [str(x) for x in v]); ok = r.rc == 0 and r.out
    rec("flags", "`--bench N...` alone accepted (default strategy)", "PASS" if ok else "FAIL", "" if ok else "rc=%s stderr=%r" % (r.rc, r.err[:30]))
    # every strategy flag must work for ALL valid inputs: tiny + sorted
    for f in ("simple", "medium", "complex", "adaptive"):
        probs = []
        for vv in ([1], [1, 2], [2, 1], [3, 2, 1], list(range(1, 9)), [INT_MAX, INT_MIN]):
            pr, ops, sim, rr = solve(vv, f)
            if pr: probs.append("%s -> %s" % (vv, pr))
            elif vv == sorted(vv) and ops: probs.append("%s already sorted but %d ops printed" % (vv, len(ops)))
        rec("flags", "--%s works for tiny/sorted inputs ('any selector flag must work regardless of size or disorder')" % f,
            "PASS" if not probs else "FAIL", "; ".join(probs[:3]))

BENCH_FIELDS = None
def parse_bench(err):
    d = {"lines": err.strip().split("\n"), "ops": {}}
    m = re.search(r"disorder:\s*([0-9]+(?:[.,][0-9]+)?)\s*%", err); d["disorder"] = float(m.group(1).replace(",", ".")) if m else None
    m = re.search(r"strategy:\s*(.+)", err); d["strategy"] = m.group(1).strip() if m else None
    m = re.search(r"total[_ ]ops:\s*(\d+)", err); d["total"] = int(m.group(1)) if m else None
    for o, n in re.findall(r"\b(sa|sb|ss|pa|pb|ra|rb|rr|rra|rrb|rrr):\s*(\d+)", err): d["ops"][o] = int(n)
    return d

def sec_bench():
    section("9. --bench MODE  (report on stderr only: disorder %, strategy/complexity, total, per-op counts)")
    rng = random.Random(ARGS.seed + 3)
    v = rnd_list(rng, 60)
    r = run(["--bench"] + [str(x) for x in v])
    if r.rc != 0 or r.err.strip() == "":
        rec("bench", "--bench implemented", "FAIL", "rc=%s, stderr=%r - benchmark mode is mandatory in v1.2 (see subject VI.5)" % (r.rc, r.err[:40]),
            "./push_swap --bench 3 2 1")
        rec("bench", "remaining --bench checks", "INFO", "skipped"); return
    rec("bench", "--bench implemented", "PASS")
    ref = run([str(x) for x in v])
    rec("bench", "stdout identical with and without --bench", "PASS" if ref.out == r.out else "FAIL")
    rec("bench", "nothing on stderr WITHOUT --bench", "PASS" if ref.err == "" else "FAIL", ref.err[:40])
    d = parse_bench(r.err); ops, _ = parse_ops(r.out)
    miss = [k for k in ("disorder", "strategy", "total") if d[k] is None] + [o for o in OPS if o not in d["ops"]]
    rec("bench", "report contains disorder, strategy, total_ops and all 11 counters", "PASS" if not miss else "FAIL", "missing: %s\nstderr was:\n%s" % (miss, r.err[:300]) if miss else "")
    if not miss:
        rec("bench", "total_ops equals the number of lines on stdout (%d)" % len(ops), "PASS" if d["total"] == len(ops) else "FAIL", "reported %s" % d["total"])
        hist = collections.Counter(ops)
        wrong = [o for o in OPS if d["ops"][o] != hist[o]]
        rec("bench", "per-operation counters are exact", "PASS" if not wrong else "FAIL", "mismatch: %s" % [(o, d["ops"][o], hist[o]) for o in wrong])
        exp = disorder_of(v) * 100
        rec("bench", "disorder %% matches (expected %.2f, reported %.2f)" % (exp, d["disorder"]), "PASS" if abs(exp - d["disorder"]) <= 0.011 else "FAIL",
            "" if "%.2f" % d["disorder"] == "%.2f" % exp or abs(exp - d["disorder"]) <= 0.011 else "must be a percentage with two decimals")
        rec("bench", "disorder printed with exactly two decimals", "PASS" if re.search(r"disorder:\s*\d+\.\d\d%", r.err) else "FAIL", r.err.split("\n")[0])
    for f, key in (("--simple", "²"), ("--medium", "√"), ("--complex", "log"), ("--adaptive", "")):
        rr = run(["--bench", f] + [str(x) for x in v]); dd = parse_bench(rr.err); s = (dd["strategy"] or "")
        ok = bool(s) and (not key or key in s or {"²": "^2", "√": "sqrt"}.get(key, "\0") in s)
        rec("bench", "%s -> strategy line names the strategy and its complexity" % f, "PASS" if ok else "FAIL", "strategy line: %r" % s)
    e = run(["--bench"] + [str(x) for x in range(1, 6)])
    rec("bench", "sorted input + --bench: stdout empty, report says 0 ops", "PASS" if (e.out == "" and parse_bench(e.err)["total"] == 0) else "FAIL", "stdout=%r total=%s" % (e.out[:20], parse_bench(e.err)["total"]))
    e = run(["--bench", "1", "1"])
    rec("bench", "error + --bench: exactly 'Error\\n' on stderr (no report)", "PASS" if (e.err == "Error\n" and e.rc != 0 and e.out == "") else "FAIL", repr(e.err[:50]))

def grade(x, th):
    return "excellent" if x < th[2] else "good" if x < th[1] else "pass" if x < th[0] else "FAIL"
def sec_perf():
    section("10. PERFORMANCE vs the subject's thresholds (100 numbers: <2000 pass, <1500 good, <700 excellent; 500: <12000 / <8000 / <5500)")
    rng = random.Random(ARGS.seed + 4)
    runs = 15 if ARGS.quick else (100 if ARGS.full else 40)
    TH = {100: (2000, 1500, 700), 500: (12000, 8000, 5500)}
    for mode in MODES:
        for n in (100, 500):
            lists = [rnd_list(rng, n, -10**4, 10**4) for _ in range(runs)]
            res = pmap(lambda v: solve(v, mode), lists)
            bad = [(v, s[0]) for v, s in zip(lists, res) if s[0]]
            cnt = [len(s[1]) for s in res if not s[0]]
            if bad:
                rec("perf", "%s n=%d: %d/%d runs not sorted" % (mode, n, len(bad), runs), "FAIL", bad[0][1], cmdline(MODES[mode] + shrink(bad[0][0], mode) if n <= 100 else MODES[mode] + bad[0][0][:8]))
            if not cnt: continue
            mn, av, mx = min(cnt), statistics.mean(cnt), max(cnt)
            gw, ga = grade(mx, TH[n]), grade(av, TH[n])
            msg = "min %d  avg %.0f  max %d | worst-case grade: %s, average grade: %s" % (mn, av, mx, gw, ga)
            if mode in ("default", "adaptive"):
                st = "FAIL" if gw == "FAIL" else ("PASS" if gw in ("good", "excellent") else "WARN")
                rec("perf", "%s n=%d  %s" % (mode, n, msg), st, "" if st == "PASS" else "evaluator will run several random lists: aim for worst-case <%d" % TH[n][1])
            else:
                rec("perf", "%s n=%d  %s" % (mode, n, msg), "INFO" if gw != "FAIL" else "WARN",
                    "" if gw != "FAIL" else "this forced strategy alone exceeds the 'pass' limit (acceptable only if the default/adaptive mode does not use it here)")

def fit_exponent(xs, ys):
    lx, ly = [math.log(x) for x in xs], [math.log(y) for y in ys]
    mx, my = statistics.mean(lx), statistics.mean(ly)
    return sum((a - mx) * (b - my) for a, b in zip(lx, ly)) / sum((a - mx) ** 2 for a in lx)
def sec_scale():
    section("11. COMPLEXITY CHECK (empirical exponent of #ops ~ n^k on random input, n = 200..2000)")
    rng = random.Random(ARGS.seed + 5)
    sizes = [200, 400, 800, 1600] if ARGS.quick else [200, 400, 800, 1600, 3200]
    limits = {"simple": (1.8, 2.3), "medium": (1.25, 1.65), "complex": (0.95, 1.35)}
    names = {"simple": "O(n^2) expected k~2", "medium": "O(n*sqrt n) expected k~1.5", "complex": "O(n log n) expected k~1.1"}
    for mode in ("simple", "medium", "complex"):
        pts = []
        for n in sizes:
            if mode == "simple" and n > 1600: continue
            s = solve(rnd_list(rng, n), mode)
            if s[0]: pts = None; rec("scale", "%s n=%d" % (mode, n), "FAIL", s[0]); break
            pts.append((n, len(s[1])))
        if not pts or len(pts) < 3: continue
        k = fit_exponent([p[0] for p in pts], [p[1] for p in pts]); lo, hi = limits[mode]
        tbl = ", ".join("%d:%d" % p for p in pts)
        ok = lo <= k <= hi
        rec("scale", "%s: measured exponent %.2f (%s)  [%s]" % (mode, k, names[mode], tbl), "PASS" if ok else "WARN",
            "" if ok else "outside the expected band [%.2f, %.2f]: the complexity you claim in the README may be wrong" % (lo, hi))
    # ratio between strategies must respect the hierarchy at n=2000
    s = {m: len(solve(rnd_list(random.Random(1), 1000), m)[1]) for m in ("medium", "complex")}
    rec("scale", "at n=1000 complex (%d) should not be slower than medium (%d)" % (s["complex"], s["medium"]), "PASS" if s["complex"] <= s["medium"] * 1.05 else "WARN")

def sec_adaptive():
    section("12. ADAPTIVE MODE: does it pick well for each disorder band?  (<0.2 / 0.2-0.5 / >=0.5)")
    rng = random.Random(ARGS.seed + 6)
    reps = 6 if ARGS.quick else 14
    for band, (lo, hi) in (("low  [0.00,0.20)", (0, 0.2)), ("mid  [0.20,0.50)", (0.2, 0.5)), ("high [0.50,1.00]", (0.5, 1.01))):
        for n in (100, 300):
            lists = [x for x in (with_disorder(rng, n, lo, hi) for _ in range(reps)) if x]
            if not lists: rec("adaptive", "%s n=%d: could not generate inputs" % (band, n), "INFO"); continue
            table = {m: pmap(lambda v: solve(v, m), lists) for m in ("adaptive", "simple", "medium", "complex")}
            bad = {m: sum(1 for s in table[m] if s[0]) for m in table}
            if bad["adaptive"]:
                i = next(i for i, s in enumerate(table["adaptive"]) if s[0])
                small = shrink(lists[i], "adaptive") if n <= 100 else lists[i][:10]
                rec("adaptive", "%s n=%d: adaptive WRONG on %d/%d inputs" % (band, n, bad["adaptive"], len(lists)), "FAIL", table["adaptive"][i][0], cmdline(small))
                continue
            avg = {m: statistics.mean(len(s[1]) for s in table[m] if not s[0]) if bad[m] < len(lists) else float("inf") for m in table}
            best = min(avg["simple"], avg["medium"], avg["complex"])
            ratio = avg["adaptive"] / best if best else 1
            line = "adaptive %.0f vs simple %.0f / medium %.0f / complex %.0f%s" % (
                avg["adaptive"], avg["simple"], avg["medium"], avg["complex"], "" if not any(bad[m] for m in ("simple", "medium", "complex")) else "  (some forced strategies produced wrong results)")
            rec("adaptive", "%s n=%d: %s" % (band, n, line), "PASS" if ratio <= 1.25 else "WARN",
                "" if ratio <= 1.25 else "adaptive uses %.0f%% more ops than the best available strategy for this regime: the dispatch/threshold is not helping" % ((ratio - 1) * 100))
    # does --bench tell which strategy was used?  (only if implemented)
    v = with_disorder(rng, 100, 0, 0.2)
    r = run(["--bench"] + [str(x) for x in v]) if v else None
    if r and r.rc == 0 and r.err:
        s = (parse_bench(r.err)["strategy"] or "").lower()
        rec("adaptive", "low-disorder input reports an O(n^2) strategy in --bench", "PASS" if ("²" in s or "^2" in s) else "WARN", s)

LEAK_PAT = re.compile(r"definitely lost|indirectly lost|possibly lost|Invalid (read|write|free)|uninitialised|Conditional jump|Mismatched free")
def sec_memory():
    section("13. MEMORY: valgrind leak check on valid inputs AND on every error path" + ("  (skipped)" if ARGS.no_valgrind else ""))
    rng = random.Random(ARGS.seed + 7)
    cases = [("1 elem", ["1"]), ("2 sorted", ["1", "2"]), ("2 rev", ["2", "1"]), ("3 rev", ["3", "2", "1"]),
             ("rotated sorted n=10", [str(x) for x in list(range(5, 10)) + list(range(5))]),
             ("5 random", [str(x) for x in rnd_list(rng, 5)]), ("40 random", [str(x) for x in rnd_list(rng, 40)]),
             ("100 random", [str(x) for x in rnd_list(rng, 100)]), ("all in one quoted arg", ["5 4 3 2 1"]),
             ("sorted 20", [str(x) for x in range(20)])]
    cases = [(l + " [%s]" % m, MODES[m] + a) for l, a in cases for m in MODES if (m in ("default", "medium", "complex", "simple") or len(a) > 3)]
    errs = [("dup", ["1", "2", "1"]), ("dup at end n=50", [str(x) for x in range(50)] + ["0"]), ("letters", ["a"]), ("letters late", ["1", "2", "3", "x"]),
            ("overflow", ["99999999999"]), ("overflow late", ["1", "2", "3", "99999999999"]), ("empty arg", [""]),
            ("flag no number", ["--simple"]), ("flag + dup", ["--medium", "1", "1"]), ("sign only", ["-"]), ("dup in quoted", ["1 2 3 3"]),
            ("bad number in 2nd quoted arg", ["1 2", "3 x"]), ("INT_MAX+1 late", ["1", "2", str(INT_MAX + 1)])]
    cases += [("ERROR PATH: " + l, a) for l, a in errs]
    def vg(case):
        label, args = case
        if shutil.which("valgrind"):
            p = subprocess.run(["valgrind", "-q", "--leak-check=full", "--show-leak-kinds=definite,indirect,possible",
                                "--errors-for-leak-kinds=definite,indirect,possible", "--error-exitcode=99", BIN] + args,
                               capture_output=True, text=True)
            return label, args, p.returncode == 99 or bool(LEAK_PAT.search(p.stderr)), p.stderr
        a = globals().get("ASAN_BIN")
        if a:
            env = dict(os.environ, ASAN_OPTIONS="detect_leaks=1:exitcode=99")
            p = subprocess.run([a] + args, capture_output=True, text=True, env=env)
            return label, args, ("AddressSanitizer" in p.stderr or "runtime error" in p.stderr or "LeakSanitizer" in p.stderr), p.stderr
        return label, args, None, ""
    if ARGS.no_valgrind and not globals().get("ASAN_BIN"): rec("memory", "no leak checker available", "INFO"); return
    res = pmap(vg, cases) if not ARGS.no_valgrind else []
    if not shutil.which("valgrind") and not ARGS.no_valgrind: rec("memory", "valgrind not installed, using ASan/LeakSanitizer instead", "INFO")
    bad = [r for r in res if r[2]]
    for label, args, _, errtxt in bad:
        first = [l for l in errtxt.split("\n") if re.search(r"lost|Invalid|uninit|Conditional|Sanitizer|runtime error", l)][:2]
        rec("memory", label, "FAIL", " | ".join(x.strip("= ") for x in first), cmdline(args))
    if res: rec("memory", "%d/%d runs free all memory with no invalid access" % (len(res) - len(bad), len(res)), "PASS" if not bad else "INFO")
    a = globals().get("ASAN_BIN")
    if a:
        rng2 = random.Random(ARGS.seed + 8); badA = 0; first = None
        for m in MODES:
            for n in (1, 2, 3, 7, 50, 200, 500):
                v = rnd_list(rng2, n) if n < 100 else ext_list(rng2, n)
                p = subprocess.run([a] + MODES[m] + [str(x) for x in v], capture_output=True, text=True,
                                   env=dict(os.environ, ASAN_OPTIONS="detect_leaks=0"))
                if "AddressSanitizer" in p.stderr or "runtime error" in p.stderr:
                    badA += 1; first = first or (m, v[:6], p.stderr.split("\n")[1][:120] if "\n" in p.stderr else p.stderr[:120])
        rec("memory", "ASan/UBSan on random inputs (all modes, n=1..500)", "PASS" if not badA else "FAIL", "" if not badA else "%d runs: %s" % (badA, first))
        # int overflow / sanitizer on edge parsing
        edge = [[str(INT_MIN), str(INT_MAX)], ["-2147483648"], ["2147483647"], ["+0"], ["-0", "1"], ["0000000000"], ["1 2 3 4 5 6 7 8 9"]]
        badE = []
        for ea in edge:
            p = subprocess.run([a] + ea, capture_output=True, text=True, env=dict(os.environ, ASAN_OPTIONS="detect_leaks=0"))
            if "AddressSanitizer" in p.stderr or "runtime error" in p.stderr: badE.append(ea)
        rec("memory", "UBSan/ASan on INT_MIN/INT_MAX parsing edge cases", "PASS" if not badE else "FAIL", str(badE[:2]))

def sec_robust():
    section("14. ROBUSTNESS & SPEED")
    rng = random.Random(ARGS.seed + 9)
    for n in ([1000, 3000] if ARGS.quick else [1000, 5000, 10000]):
        for mode in ("default", "medium", "complex"):
            v = rnd_list(rng, n, -10**7, 10**7)
            p, ops, sim, r = solve(v, mode)
            st = "FAIL" if p else ("PASS" if r.dt < 3 else "WARN")
            rec("robust", "n=%d %-8s %6d ops in %.2fs" % (n, mode, len(ops), r.dt), st, p or ("slow: >3 s (is ranking/ft_index O(n) per lookup? each write() a syscall?)" if st == "WARN" else ""),
                cmdline(MODES[mode] + v[:6]) if p else None)
    v = rnd_list(rng, 500); r = run([" ".join(map(str, v))]); ops, pr = parse_ops(r.out)
    rec("robust", "500 numbers in ONE quoted argument", "PASS" if (r.rc == 0 and not pr and simulate(v, ops)["sorted"]) else "FAIL", "rc=%s" % r.rc)
    v = rnd_list(rng, 500); r = run([str(x) for x in v] + [str(v[-1])])
    rec("robust", "duplicate of the LAST element in 501 args detected", "PASS" if (r.rc != 0 and r.err == "Error\n") else "FAIL", "rc=%s err=%r" % (r.rc, r.err[:20]))
    v = rnd_list(rng, 500); v2 = v[:]; v2[250] = v2[10]; r = run(v2)
    rec("robust", "duplicate in the middle of 500 numbers detected", "PASS" if (r.rc != 0 and r.err == "Error\n") else "FAIL", "rc=%s" % r.rc)
    r1, r2 = run(v), run(v)
    rec("robust", "deterministic output (same input twice)", "PASS" if r1.out == r2.out else "WARN")
    r = run([str(INT_MAX), str(INT_MIN)] + [str(x) for x in rnd_list(rng, 98, -1000, 1000)])
    ok = r.rc == 0 and simulate([INT_MAX, INT_MIN] + [], [])["sorted"] is not None
    p, ops, sim, rr = solve([INT_MAX, INT_MIN] + rnd_list(rng, 98, -1000, 1000))
    rec("robust", "INT_MAX / INT_MIN mixed with small values (n=100)", "PASS" if not p else "FAIL", p or "")
    r = run(["1", "2", "3"], binp=BIN, env={"PATH": ""})
    rec("robust", "works with an empty environment", "PASS" if r.rc == 0 else "FAIL", "rc=%s" % r.rc)
    d = tempfile.mkdtemp()
    try:
        r = subprocess.run([BIN, "3", "2", "1"], capture_output=True, cwd=d, stdin=subprocess.DEVNULL, timeout=10)
        rec("robust", "does not read stdin / does not need a particular cwd", "PASS" if r.returncode == 0 else "FAIL")
    finally: shutil.rmtree(d, ignore_errors=True)
    r = subprocess.run("%s 3 2 1 >/dev/full" % shq(BIN), shell=True, capture_output=True)
    rec("robust", "write failure (stdout=/dev/full) does not crash", "PASS" if (r.returncode is not None and r.returncode >= 0 and r.returncode < 128) else "WARN", "rc=%s" % r.returncode)

# ----------------------------------------------------------------------------- main
SECTION_FUNCS = [("parse", sec_parse), ("valid", sec_valid), ("perms", sec_perms), ("random", sec_random),
                 ("shapes", sec_shapes), ("hygiene", sec_hygiene), ("flags", sec_flags), ("bench", sec_bench),
                 ("perf", sec_perf), ("scale", sec_scale), ("adaptive", sec_adaptive), ("memory", sec_memory), ("robust", sec_robust)]

def final_report():
    print("\n" + c("1", "=" * 78) + "\n" + c("1", "SUMMARY"))
    cats = collections.OrderedDict()
    for r in RESULTS: cats.setdefault(r.cat, collections.Counter())[r.status] += 1
    print("  %-10s %6s %6s %6s %6s" % ("section", "PASS", "FAIL", "WARN", "INFO"))
    for k, cn in cats.items():
        print("  %-10s %6d %6s %6s %6d" % (k, cn["PASS"], c("31;1", "%d" % cn["FAIL"]) if cn["FAIL"] else "0",
                                       c("33", "%d" % cn["WARN"]) if cn["WARN"] else "0", cn["INFO"]))
    fails = [r for r in RESULTS if r.status == "FAIL"]; warns = [r for r in RESULTS if r.status == "WARN"]
    print("\n" + c("1", "WEAKNESSES TO FIX FIRST (FAIL = breaks the subject)"))
    if not fails: print("  none - no mandatory requirement violated by these tests")
    for i, r in enumerate(fails, 1):
        print("  %2d. [%s] %s" % (i, r.cat, r.name));
        if r.detail: print("        " + r.detail.split("\n")[0])
        if r.repro: print("        repro: " + r.repro)
    print("\n" + c("1", "WEAKNESSES TO IMPROVE (WARN)"))
    if not warns: print("  none")
    for i, r in enumerate(warns, 1):
        print("  %2d. [%s] %s" % (i, r.cat, r.name))
        if r.detail: print("        " + r.detail.split("\n")[0])
    if ARGS.report:
        with open(ARGS.report, "w") as f:
            f.write("# push_swap tester report\n\nseed=%d binary=%s\n\n" % (ARGS.seed, BIN))
            for r in RESULTS:
                f.write("- **%s** [%s] %s%s%s\n" % (r.status, r.cat, r.name, (" - " + r.detail.replace("\n", " ")) if r.detail else "",
                                                   ("  \n  `%s`" % r.repro) if r.repro else ""))
        print("\nreport written to %s" % ARGS.report)
    total_fail = len(fails)
    print("\n%s  (%d FAIL, %d WARN, %d tests)" % (c("31;1", "NOT READY") if total_fail else c("32;1", "ALL MANDATORY CHECKS PASSED"), total_fail, len(warns), len(RESULTS)))
    return 1 if total_fail else 0

def main():
    global ARGS, BIN
    ap = argparse.ArgumentParser(description="push_swap tester / weakness detector")
    ap.add_argument("src", nargs="?", default=".", help="project directory (compiled without the Makefile)")
    ap.add_argument("--bin", help="test this binary instead of compiling")
    ap.add_argument("--quick", action="store_true"); ap.add_argument("--full", action="store_true")
    ap.add_argument("--seed", type=int, default=42); ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--no-valgrind", action="store_true"); ap.add_argument("--no-asan", action="store_true"); ap.add_argument("--no-norm", action="store_true")
    ap.add_argument("--only", help="comma separated sections"); ap.add_argument("--report", help="write a markdown report")
    ap.add_argument("-v", "--verbose", action="store_true", help="print details for passing tests too")
    ARGS = ap.parse_args()
    only = set(ARGS.only.split(",")) if ARGS.only else set(ALL_SECTIONS)
    tmp = tempfile.mkdtemp(prefix="ps_tester_")
    t0 = time.time()
    try:
        globals()["ASAN_BIN"] = None
        if ARGS.bin:
            BIN = os.path.abspath(ARGS.bin)
            if not os.access(BIN, os.X_OK): print("not executable: %s" % BIN); return 2
        else:
            ok = build(os.path.abspath(ARGS.src), tmp) if "build" in only or True else True
            if not ok: final_report(); return 1
        for name, fn in SECTION_FUNCS:
            if name in only: fn()
        rc = final_report(); print("elapsed %.1fs" % (time.time() - t0)); return rc
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    sys.exit(main())
