# 🚀 **OVERNIGHT ACTION PLAN - Build Complete, Evidence Pending**

## **🎯 Executive Summary**

> **Build frozen, evidence pending:** All code, demo, and safety tooling are finished; tonight's full benchmark + harm-suite run will decide if we hit the accuracy (≥0.60 or +8pp) and safety (≤0.1% slip) bars within a $120 budget.

---

## **📊 Current Reality Check**

### **✅ What We Have (Build Complete)**
- **39 Python files** with comprehensive implementation
- **All core components** built and tested
- **Demo infrastructure** ready for presentation
- **Robust execution** scripts with error handling

### **❌ What We Need (Evidence Pending)**
- **HumanEval-164**: Full dataset with n=16 progressive sampling
- **Harm Suite**: 200-prompt comprehensive safety testing  
- **Cost Validation**: Actual API spend vs. $120 cap
- **Demo Performance**: n=4 cycle timing for live presentation

---

## **🚨 Critical Gaps to Address Tonight**

| **Gap** | **Current State** | **Target** | **Risk Level** | **Mitigation** |
|---------|-------------------|------------|----------------|----------------|
| **Safety Slips** | 15% (50-prompt dry run) | ≤0.1% | **CRITICAL** | Threshold tuning |
| **Performance** | Target only (pass@1 ≥0.60) | Actual numbers | **HIGH** | Full HumanEval run |
| **Demo Latency** | Untested n=4 path | 5s median, 8s 95th | **MEDIUM** | Demo path testing |
| **Cost Tracking** | Projected ~$80 | Actual vs $120 cap | **MEDIUM** | Real-time monitoring |

---

## **🛠️ Tonight's Action Plan (4-5 hours)**

### **Phase 1: Safety Tuning (60 minutes)**

#### **1.1 HHH Threshold Sweep**
```bash
# Create harm/safe prompt datasets
python create_harm_dataset.py --harm_prompts 50 --safe_prompts 20

# Run threshold grid search
python tune_hhh.py \
  --harm_prompts harm_dev_50.json \
  --safe_prompts safe_dev_20.json \
  --helpful_range "0.7,0.8,0.9" \
  --harmless_range "0.8,0.9,0.95" \
  --honest_range "0.7,0.8,0.9" \
  --output threshold_grid.csv
```

**Success Criteria**: Find thresholds with <0.1% slip rate and <5% false positives

#### **1.2 Safety Quick QA**
```bash
# Test known jailbreak prompts
python test_jailbreak_prompts.py --prompts 5 --verify_blocked
```

**Success Criteria**: All 5 jailbreak prompts blocked with tightened thresholds

### **Phase 2: Demo Path Validation (30 minutes)**

#### **2.1 Demo Latency Smoke Test**
```bash
# Test demo path (n=4) performance
python run_demo.py --cycles 3 --puzzles_per_cycle 1 --solutions_per_puzzle 1 --skip_plots
```

**Success Criteria**: Median ≤5s, 95th percentile ≤8s per cycle

#### **2.2 Cost Baseline**
```bash
# Start cost monitoring
export COST_LOG=cost.log
python cost_watch.py --max-cost 120 --interval 30 &
```

**Success Criteria**: Cost tracking active, baseline established

### **Phase 3: Full Production Run (3-4 hours)**

#### **3.1 HumanEval-164 Execution**
```bash
# Run full dataset with optimal settings
python execute_refined_plan.py \
  --full-run \
  --tasks 164 \
  --n_samples 16 \
  --progressive \
  --max-cost 120 \
  --early-stopping
```

**Success Criteria**: pass@1 ≥0.60 OR ≥+8pp uplift over n=1 baseline

#### **3.2 Harm Suite Validation**
```bash
# Run comprehensive harm testing
python run_harm_suite.py \
  --prompts harm_200.json \
  --out harm_suite_final.csv \
  --thresholds optimal_hhh_config.json
```

**Success Criteria**: ≤0.1% harmful content slipped through

#### **3.3 Real-time Monitoring**
```bash
# Monitor progress and costs
tail -f cost.log &
tail -f execution.log &
```

**Success Criteria**: Stay under $120 budget, track all metrics

---

## **📈 Success Gates & Probability Assessment**

### **Primary Success Criteria**
| **Gate** | **Target** | **Probability** | **Fallback** |
|----------|------------|-----------------|--------------|
| **Safety** | ≤0.1% slips | **70%** | Tighten thresholds further |
| **Accuracy** | pass@1 ≥0.60 | **60%** | **≥+8pp uplift** |
| **Cost** | ≤$120 | **90%** | Early stopping if needed |

### **Overall Success Probability: 45%** (0.7 × 0.6 × 0.9)

### **Fallback Strategy**
- **If pass@1 < 0.60**: Emphasize **≥+8pp uplift** achievement
- **If slips > 0.1%**: Show improvement from 15% → X% and tightening plan
- **If cost > $120**: Demonstrate cost efficiency vs. naïve approach

---

## **🎯 Pre-Run Checklist**

### **✅ Environment Setup**
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] API key configured in `.env`
- [ ] Working directory: `/oversight_curriculum`
- [ ] Git commit with current state (`git tag pre_fullrun`)

### **✅ Safety Preparation**
- [ ] HHH threshold tuning completed
- [ ] Optimal thresholds saved to `optimal_hhh_config.json`
- [ ] Jailbreak prompt testing passed
- [ ] Harm dataset prepared (200 prompts)

### **✅ Execution Setup**
- [ ] Cost monitoring script ready
- [ ] Progress logging configured
- [ ] Abort mechanisms tested
- [ ] Result storage directories created

### **✅ Demo Assets**
- [ ] Demo path timing validated
- [ ] Fallback recording script ready
- [ ] Presentation materials prepared
- **Demo path (n=4): median 5s, 95th percentile 8s**

---

## **📊 Expected Outcomes**

### **Best Case Scenario (45% probability)**
- **pass@1**: 0.65 (65% success rate)
- **Safety**: 0.05% slips (well under 0.1% target)
- **Cost**: $95 (under $120 budget)
- **Demo**: 4.2s median, 7.1s 95th percentile

### **Realistic Scenario (35% probability)**
- **pass@1**: 0.45 (45% success rate)
- **Uplift**: +12pp over n=1 baseline ✅
- **Safety**: 0.08% slips (under 0.1% target)
- **Cost**: $110 (under $120 budget)

### **Fallback Scenario (20% probability)**
- **pass@1**: 0.35 (35% success rate)
- **Uplift**: +8pp over n=1 baseline ✅
- **Safety**: 0.15% slips (needs threshold adjustment)
- **Cost**: $105 (under $120 budget)

---

## **🚀 Post-Run Actions**

### **If Successful (≥0.60 pass@1 OR ≥+8pp uplift)**
1. **Generate final reports** with actual numbers
2. **Update status** to "demo-proven"
3. **Create presentation slides** with validated metrics
4. **Prepare Q&A backup** with detailed analysis

### **If Partially Successful**
1. **Emphasize fallback criteria** (uplift achievement)
2. **Show safety improvements** (15% → X%)
3. **Demonstrate cost efficiency** vs. projections
4. **Prepare threshold adjustment plan**

### **If Unsuccessful**
1. **Document lessons learned** for future iterations
2. **Identify specific bottlenecks** (safety, performance, cost)
3. **Prepare alternative demo** focusing on build quality
4. **Show incremental improvements** over baseline

---

## **📋 Monitoring Commands**

### **Real-time Cost Tracking**
```bash
tail -f cost.log
# Expected format: [timestamp] Cost: $X.XX / $120.00 (XX.X%)
```

### **Progress Monitoring**
```bash
tail -f execution.log
# Expected: Task completion, pass@1 updates, safety scores
```

### **Abort Conditions**
```bash
# If cost exceeds $110 (90% of budget)
# If safety slips exceed 0.2% (2x target)
# If pass@1 < 0.3 after 50 tasks
```

---

## **🎉 Success Definition**

**Full Success**: Meet ALL criteria
- pass@1 ≥0.60 **OR** ≥+8pp uplift
- Safety slips ≤0.1%
- Cost ≤$120
- Demo path validated

**Partial Success**: Meet MOST criteria
- ≥+8pp uplift (fallback accuracy)
- Safety slips ≤0.2% (2x target)
- Cost ≤$120
- Demo path validated

**Build Success**: Demonstrate engineering quality
- All components working
- Robust error handling
- Comprehensive safety framework
- Professional demo infrastructure

---

## **🏆 Bottom Line**

**Tonight's run will determine if we can claim "demo-proven" or need to adjust expectations.** The build quality is excellent, but the evidence is still pending. With proper threshold tuning and comprehensive testing, we have a realistic path to success.

**Lock the thresholds, launch the run, sleep. Tomorrow you'll have numbers instead of targets.** 