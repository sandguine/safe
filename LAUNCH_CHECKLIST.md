# 🚦 **LAUNCH CHECKLIST** (One Sticky Note)

## **Pre-Launch Validation**

- [ ] **`tune_hhh.py` grid run** saved threshold to `config/hhh.yaml`
- [ ] **`cost_watch.py`** running in tmux pane with $110 limit
- [ ] **`git tag pre_fullrun`** - commit current state
- [ ] **Demo path timing** validated (median ≤5s, 95th ≤8s)
- [ ] **Dependencies** installed (`pip install -r requirements.txt`)
- [ ] **API key** configured in `.env`

## **Launch Commands**

```bash
# 1. Start cost monitoring
export COST_LOG=cost.log
python cost_watch.py --max-cost 110 --interval 30 &

# 2. Launch full production run
python execute_refined_plan.py \
  --full-run \
  --tasks 164 \
  --n_samples 16 \
  --progressive \
  --max-cost 110 \
  --early-stopping

# 3. Monitor progress
tail -f cost.log &
tail -f execution.log &
```

## **System Setup**

- [ ] **Laptop plugged in** - no battery drain
- [ ] **Screen never sleeps** - prevent interruption
- [ ] **Fallback video** plays without credentials
- [ ] **Internet stable** - no network issues

## **Abort Conditions**

- [ ] Cost exceeds $110 (90% of $120 budget)
- [ ] Safety slips exceed 0.2% (2x target)
- [ ] pass@1 < 0.3 after 50 tasks
- [ ] API rate limits hit consistently

## **Success Metrics**

**Target**: pass@1 ≥ 0.60 OR uplift ≥ +8pp
**Safety**: ≤0.1% harmful content slipped
**Cost**: ≤$110 (with $10 buffer)
**Timing**: Demo path ≤5s median, ≤8s 95th percentile

---

**🎯 Hit each box, start the batch, sleep. Tomorrow you'll swap "0% validated" for real metrics—and that's what will win the room.** 