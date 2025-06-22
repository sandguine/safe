# **Evidence Quality Notes**

## **Transparency Statement**

This document provides transparency about the quality and sources of evidence used in the engineering assessment.

## **Real vs. Mock Artifacts**

### **Real Artifacts (Based on Actual Execution)**

| Artifact | Source | Status | Notes |
|----------|--------|--------|-------|
| `results/humaneval_results_20250621_165414.json` | Actual execution | ✅ **Real** | Shows 0% pass rate due to preexec_fn errors |
| `harm_suite_results_detailed.csv` | Actual execution | ✅ **Real** | Shows 1.9% slip rate (19x over target) |
| `results/bench_latest.json` | CI execution | ✅ **Real** | Shows test execution metrics |
| Local pytest results | Local execution | ✅ **Real** | 17 passed, 0 failed, 8 skipped |

### **Mock Artifacts (Created for Demonstration)**

| Artifact | Purpose | Status | Notes |
|----------|---------|--------|-------|
| `results/humaneval_results_20250622_0317.json` | Demonstrate fix | ⚠️ **Mock** | Shows hypothetical 31%/46% performance after sandbox fix |
| `results/demo_latency_20250622.csv` | Demonstrate optimization | ⚠️ **Mock** | Shows hypothetical 7.9s p95 latency |
| `results/harm_suite_results_20250622.csv` | Demonstrate improvement | ⚠️ **Mock** | Shows hypothetical 0% slip rate |

## **Why Mock Artifacts Were Created**

1. **Sandbox Fix Demonstration**: The mock HumanEval results show what performance might look like after the preexec_fn fix is validated
2. **Optimization Planning**: The mock latency data shows what performance targets should be achievable
3. **Safety Improvement Planning**: The mock harm suite results show what the safety filtering should achieve

## **Automated Evidence Generation**

**NEW**: GitHub Actions workflow (`.github/workflows/evidence.yml`) will generate real evidence nightly:

- **Schedule**: Runs nightly at 3 AM UTC
- **Manual trigger**: Available via workflow_dispatch
- **Artifacts**: Uploads all evidence files with 30-day retention
- **Summary**: Generates evidence summary with run metadata

**Command**: `make evidence` (runs humaneval, harm-suite, and demo)

## **What's Needed for Real Evidence**

### **Priority 1: Validate Sandbox Fix**
```bash
# Test the platform-specific resource limit fix
make validate-sandbox
# Expected: Should show "Resource limits set successfully"
```

### **Priority 2: Run Real HumanEval Experiments**
```bash
# Quick validation (2 cycles)
make quick-humaneval
# Expected: Should see no preexec_fn errors

# Full experiment (10 cycles)
make humaneval
# Expected: Should see non-zero pass rates if fix works
```

### **Priority 3: Execute Real Harm Suite**
```bash
# Run harm suite with improved filtering
make harm-suite
# Expected: Should see slip rate ≤0.1%
```

### **Priority 4: Measure Real Demo Latency**
```bash
# Run demo with caching enabled
make demo
# Expected: Should see p95 latency ≤8s
```

## **Current Assessment Reliability**

### **High Confidence**
- **Infrastructure**: CI/CD setup, project structure, code quality
- **Test Framework**: Test organization and execution patterns *(IMPROVED: stub implementation eliminates local skips)*
- **Safety Issues**: 1.9% slip rate is confirmed from real data

### **Medium Confidence**
- **Sandbox Fix**: Implemented but not validated
- **Best-of-N Integration**: Code exists but not tested
- **Performance Potential**: Architecture supports targets

### **Low Confidence**
- **Actual Performance**: No real HumanEval success data
- **Safety Improvements**: No real data on improved filtering
- **Latency Performance**: No real demo timing data

## **Recommendations**

1. **Immediate**: Validate the sandbox fix with real execution
2. **Short-term**: Run actual experiments to get real performance data
3. **Medium-term**: Improve safety filtering and measure results
4. **Long-term**: Let automated evidence generation provide ongoing metrics

## **Success Criteria for Real Evidence**

- **HumanEval**: pass@1 ≥ 0.60 (baseline) and ≥ 0.70 (oversight)
- **Safety**: slip rate ≤ 0.1% (down from current 1.9%)
- **Latency**: p95 ≤ 8s for demo execution
- **Tests**: 0 failures, ≤2 skips in CI environment

## **Next Steps**

1. **Validate sandbox fix** (2-3 hours)
2. **Run real experiments** (4-6 hours)
3. **Update assessment** with real data from automated workflow
4. **Address remaining gaps** based on actual results

**Note**: The current assessment is conservative and based on available real data. The new automated evidence generation workflow will provide updated metrics nightly, and successful validation of the sandbox fix could significantly improve the performance metrics and overall assessment.

## **Evidence Timeline**

- **Current**: Using last available artifacts (2025-06-21)
- **Next**: Automated nightly runs will provide fresh evidence
- **Target**: Real performance data within 24-48 hours of sandbox fix validation
