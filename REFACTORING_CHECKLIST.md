# Refactoring Implementation Checklist

## Foundation (✅ DONE)

- [x] Created `utils/base_service.py` (85 lines)
- [x] Created `utils/base_gui.py` (75 lines)
- [x] Created `utils/data_models.py` (290 lines)
- [x] Created `utils/validators.py` (150 lines)
- [x] Created `REFACTORING_GUIDE.md`
- [x] Created `REFACTORING_EXAMPLE.md`
- [x] Created `REFACTORING_ROADMAP.md`
- [x] Created `REFACTORING_SUMMARY.md`
- [x] Committed all files to git

## Phase 1: Easy Services (Target: 2 hours)

### Service: portfolio_manager.py (213 → 160 lines)
- [ ] Add imports: BaseService, data_models, validators
- [ ] Change class to extend BaseService
- [ ] Update __init__ to call super().__init__()
- [ ] Replace logger with self.logger
- [ ] Remove Holding dataclass (use Position from data_models)
- [ ] Replace try/except error handling with self.logger
- [ ] Use self._cache_get/set instead of dict
- [ ] Test: `python -c "from services.portfolio_manager import Portfolio"`
- [ ] Commit with message: "Refactor portfolio_manager to use BaseService"

### Service: alert_service.py (265 → 200 lines)
- [ ] Add imports: BaseService, data_models, validators
- [ ] Change class to extend BaseService
- [ ] Update __init__
- [ ] Replace logger with self.logger
- [ ] Remove duplicate dataclasses (use from data_models)
- [ ] Replace logging boilerplate
- [ ] Use validators for symbol validation
- [ ] Test: `python -c "from services.alert_service import AlertService"`
- [ ] Commit

### Service: technical_analysis.py (473 → 380 lines)
- [ ] Add imports: BaseService, validators
- [ ] Extend BaseService
- [ ] Update __init__
- [ ] Replace logger with self.logger
- [ ] Use validators
- [ ] Test
- [ ] Commit

## Phase 2: Medium Services (Target: 3 hours)

### Service: chatbot_service.py (477 lines)
- [ ] Refactor following Phase 1 pattern
- [ ] Test
- [ ] Commit

### Service: ml_personalization.py (507 lines)
- [ ] Refactor following Phase 1 pattern
- [ ] Test
- [ ] Commit

### Service: stock_screener.py (507 lines)
- [ ] Refactor following Phase 1 pattern
- [ ] Test
- [ ] Commit

### Service: dividend_tracker.py (531 lines)
- [ ] Refactor following Phase 1 pattern
- [ ] Test
- [ ] Commit

## Phase 3: Large Services (Target: 4 hours)

### Service: options_analyzer.py (536 lines)
- [ ] Refactor following Phase 1 pattern
- [ ] Test
- [ ] Commit

### Service: international_markets.py (557 lines)
- [ ] Refactor following Phase 1 pattern
- [ ] Test
- [ ] Commit

### Service: backtester.py (567 → 440 lines) - LARGE
- [ ] Add imports: BaseService, data_models, validators
- [ ] Extend BaseService
- [ ] Update __init__
- [ ] Remove Trade, BacktestResults, etc. (use from data_models)
- [ ] Replace logger with self.logger
- [ ] Use caching from parent
- [ ] Test: `python -c "from services.backtester import Backtester"`
- [ ] Commit

### Service: broker_integration.py (591 lines)
- [ ] Refactor following Phase 1 pattern
- [ ] Test
- [ ] Commit

### Service: custom_alert_engine.py (647 → 420 lines) - VERY LARGE
- [ ] Add imports: BaseService, data_models, validators
- [ ] Extend BaseService
- [ ] Update __init__
- [ ] Remove ALL alert dataclasses (already in data_models!)
- [ ] Replace logger with self.logger
- [ ] Replace threading patterns (move to GUI)
- [ ] Test: `python -c "from services.custom_alert_engine import CustomAlertEngine"`
- [ ] Commit

## Phase 4: GUI Refactoring (Target: 3 hours)

### Small GUIs (Start here)

#### GUI: portfolio.py
- [ ] Change class to extend BaseTabWidget
- [ ] Replace QMessageBox with self.show_*()
- [ ] Test dialogs work
- [ ] Commit

#### GUI: technical_analysis.py
- [ ] Extend BaseTabWidget
- [ ] Replace dialogs
- [ ] Test
- [ ] Commit

#### GUI: screener.py (604 lines)
- [ ] Extend BaseTabWidget
- [ ] Replace dialogs
- [ ] Test
- [ ] Commit

### Large GUIs

#### GUI: options.py (628 lines)
- [ ] Extend BaseTabWidget
- [ ] Replace all QMessageBox calls with self.show_*()
- [ ] Extract dialog classes if >100 lines
- [ ] Test all dialogs work
- [ ] Commit

#### GUI: backtest.py (635 → 450 lines) - LARGE
- [ ] Extend BaseTabWidget
- [ ] Replace all dialogs with self.show_*()
- [ ] Simplify worker thread handling (use base pattern)
- [ ] Test
- [ ] Commit with message: "Refactor backtest GUI to use BaseTabWidget"

#### GUI: custom_alerts.py (677 → 480 lines) - LARGEST
- [ ] Extend BaseTabWidget
- [ ] Replace all QMessageBox with self.show_*()
- [ ] Extract dialog classes to `gui/dialogs/` subfolder:
  - [ ] create_condition_dialog.py
  - [ ] create_rule_dialog.py
  - [ ] notification_settings_dialog.py
- [ ] Test all dialogs work
- [ ] Commit with message: "Refactor custom_alerts GUI + extract dialogs"

### Remaining GUIs

- [ ] personalization.py
- [ ] dividend_tracker.py
- [ ] international_markets.py
- [ ] alerts.py
- [ ] stock_analysis.py
- [ ] dashboard.py
- [ ] chatbot.py
- [ ] broker.py
- [ ] reports.py
- [ ] watchlist.py
- [ ] stock_search.py

## Phase 5: Final Polish (Target: 1 hour)

- [ ] Create `utils/workers.py` with generic BackgroundWorker
- [ ] Create `utils/gui_helpers.py` with form/table builders
- [ ] Create `utils/constants.py` with shared enums
- [ ] Update all GUI tabs to use new utils
- [ ] Run full test suite
- [ ] All tests pass ✅

## Summary Stats

| Phase | Files | Time | Savings |
|-------|-------|------|---------|
| Foundation | 4 utils | Done | Enables rest |
| Phase 1 | 3 services | 2h | -300 lines |
| Phase 2 | 4 services | 3h | -400 lines |
| Phase 3 | 4 services | 4h | -600 lines |
| Phase 4 | 17 GUIs | 3h | -2,400 lines |
| Phase 5 | 3 utils | 1h | Enables testing |
| **TOTAL** | **35 files** | **13h** | **-3,700 lines** |

## How to Use This Checklist

1. Copy a section into a text editor
2. Check off items as you complete them
3. Commit after each service/GUI
4. Re-check the main checklist for overall progress

## Quick Status Check

```bash
# Count completed refactorings
grep -l "from utils.base_service import BaseService" services/*.py | wc -l

# Count completed GUI refactorings
grep -l "from utils.base_gui import BaseTabWidget" gui/*.py | wc -l

# See new file sizes
wc -l services/*.py | sort -n
wc -l gui/*.py | sort -n
```

## Next Steps

Start with: **portfolio_manager.py**

Follow: **REFACTORING_EXAMPLE.md** for exact changes

Reference: **REFACTORING_GUIDE.md** for questions

Estimate: **20-30 minutes per service**

Good luck! 🚀
