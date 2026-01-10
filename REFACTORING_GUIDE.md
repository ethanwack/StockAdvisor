# Refactoring Guide - Stock Advisor Project

This guide provides step-by-step instructions for refactoring the large files and reducing code duplication.

## What We've Created (Foundation)

### 1. `utils/base_service.py` ✅
Base class for all services with:
- **Logger initialization** - One place to configure logging
- **Database connection** - Auto-managed SQLite connections
- **Caching layer** - Built-in TTL caching with `_cache_get()` and `_cache_set()`
- **Error handling** - Centralized database error management

**Usage:**
```python
from utils.base_service import BaseService

class MyService(BaseService):
    def __init__(self, db_path="app.db"):
        super().__init__(db_path=db_path, cache_ttl=3600)
    
    def get_data(self, key):
        # Check cache first
        cached = self._cache_get(key)
        if cached:
            return cached
        
        # Fetch data
        data = self.db.execute("SELECT * FROM table WHERE id=?", (key,))
        
        # Store in cache
        self._cache_set(key, data)
        return data
```

### 2. `utils/base_gui.py` ✅
Base class for GUI tabs with:
- **Dialog helpers** - `show_info()`, `show_error()`, `show_confirm()`
- **Worker thread management** - Auto-track and cleanup threads
- **Logger** - Pre-configured logging for GUI components

**Usage:**
```python
from utils.base_gui import BaseTabWidget

class MyTab(BaseTabWidget):
    def init_ui(self):
        layout = QVBoxLayout()
        # ... your UI code ...
        self.setLayout(layout)
    
    def on_button_click(self):
        if self.show_confirm("Title", "Are you sure?"):
            # User confirmed
            pass
```

### 3. `utils/data_models.py` ✅
All @dataclass definitions in one place:
- `Trade` - Backtesting trades
- `BacktestResults` - Strategy performance
- `AlertCondition`, `AlertRule`, `AlertEvent` - Alert system
- `Position` - Portfolio holdings
- `ScreenerCriteria` - Stock filtering

**Benefit:** Single source of truth for data structures

### 4. `utils/validators.py` ✅
Centralized validation functions:
- `validate_symbol()` - Stock ticker validation
- `validate_price()` - Price validation
- `validate_date_range()` - Date validation
- `validate_email()` - Email validation
- `safe_validate()` - Non-throwing wrapper

**Usage:**
```python
from utils.validators import validate_symbol, ValidationError

try:
    validate_symbol(symbol)
except ValidationError as e:
    print(f"Invalid: {e}")
```

---

## Files to Refactor (Large Files >600 lines)

### Priority 1: Backend Services

#### `services/backtester.py` (633 lines) → Refactor to ~400 lines
**Current Issues:**
- Duplicates Trade, BacktestResults dataclasses
- Duplicates logger initialization
- Mixes data loading with backtesting logic

**Refactoring Steps:**

1. **Remove dataclass imports** - Use from `utils.data_models`
   ```python
   # Remove: from dataclasses import dataclass, field
   # Remove: class Trade, class PositionType, class OrderType
   # Add:    from utils.data_models import Trade, PositionType, OrderType, BacktestResults
   ```

2. **Extend BaseService** instead of raw class
   ```python
   # Before:
   class Backtester:
       def __init__(self, initial_capital=10000.0):
           self.logger = setup_logger(...)
           self.db = sqlite3.connect(...)
   
   # After:
   class Backtester(BaseService):
       def __init__(self, initial_capital=10000.0, db_path="app.db"):
           super().__init__(db_path=db_path)
           self.initial_capital = initial_capital
   ```

3. **Use validators in methods**
   ```python
   # Before:
   if not symbol or not isinstance(symbol, str):
       raise ValueError("Invalid symbol")
   if start_date >= end_date:
       raise ValueError("Date error")
   
   # After:
   from utils.validators import validate_symbol, validate_date_range
   validate_symbol(symbol)
   validate_date_range(start_date, end_date)
   ```

4. **Use cache from parent class**
   ```python
   # Before:
   self._cache = {}
   if key in self._cache:
       return self._cache[key]
   self._cache[key] = result
   
   # After:
   cached = self._cache_get(key)
   if cached:
       return cached
   self._cache_set(key, result)
   ```

5. **Use logger from parent**
   ```python
   # Before:
   self.logger = logging.getLogger(...)
   
   # After:
   self.logger.info("message")  # Pre-configured in BaseService
   ```

**Expected Savings:** ~233 lines removed

---

#### `services/custom_alert_engine.py` (647 lines) → Refactor to ~420 lines
**Current Issues:**
- Duplicates Alert dataclasses
- Duplicates database initialization
- Mixes engine logic with notification logic

**Refactoring Steps:**

1. **Import models from utils.data_models**
   ```python
   from utils.data_models import (
       AlertCondition, AlertRule, AlertEvent, AlertConditionType,
       LogicOperator, NotificationChannel, AlertSeverity
   )
   # Remove duplicate @dataclass definitions
   ```

2. **Extend BaseService**
   ```python
   from utils.base_service import BaseService
   
   class CustomAlertEngine(BaseService):
       def __init__(self, db_path="app.db"):
           super().__init__(db_path=db_path)
   ```

3. **Use validators**
   ```python
   from utils.validators import validate_symbol, ValidationError
   validate_symbol(symbol)  # Instead of custom logic
   ```

4. **Remove threading code** - Externalize to GUI layer
   ```python
   # Move this to GUI:
   # threading, time.sleep(), background loops
   # Keep engine as synchronous library
   ```

**Expected Savings:** ~227 lines

---

### Priority 2: GUI Tabs

#### `gui/backtest.py` (635 lines) → Refactor to ~450 lines
**Current Issues:**
- Duplicates BacktestWorker pattern (repeated in all tabs)
- Duplicates dialog creation logic
- Mixes UI setup with business logic

**Refactoring Steps:**

1. **Extend BaseTabWidget**
   ```python
   from utils.base_gui import BaseTabWidget
   
   class BacktestTab(BaseTabWidget):
       def init_ui(self):
           # Your layout code
           pass
   ```

2. **Use dialog helpers**
   ```python
   # Before:
   QMessageBox.information(self, "Title", "Message")
   
   # After:
   self.show_info("Title", "Message")
   self.show_error("Error", "Details")
   if self.show_confirm("Are you sure?", "Delete?"):
       # proceed
   ```

3. **Simplify worker thread code**
   ```python
   # Create generic BackgroundWorker in utils/workers.py
   # Use it: worker = BackgroundWorker(self.backtester.backtest, args)
   ```

4. **Extract table/form creation to utility**
   ```python
   # utils/gui_helpers.py
   def create_criteria_form(parent, criteria):
       """Generic form builder"""
       pass
   ```

**Expected Savings:** ~185 lines

---

#### `gui/custom_alerts.py` (677 lines) → Refactor to ~480 lines
**Current Issues:**
- Largest file in project
- Duplicates AlertWorker pattern
- Complex dialog nesting

**Refactoring Steps:**

1. **Extend BaseTabWidget**
2. **Extract dialogs to separate files**
   ```
   gui/
   ├── custom_alerts.py (main tab, ~300 lines)
   ├── dialogs/
   │   ├── create_condition_dialog.py (~100 lines)
   │   ├── create_rule_dialog.py (~120 lines)
   │   └── notification_dialog.py (~80 lines)
   ```

3. **Use generic worker from utils**
4. **Use base dialog helpers**

**Expected Savings:** ~197 lines

---

## Implementation Order

### Phase 1: Foundation (✅ Already Done)
- [x] Create `base_service.py`
- [x] Create `base_gui.py`
- [x] Create `data_models.py`
- [x] Create `validators.py`

### Phase 2: Services (Next)
1. Refactor `services/backtester.py` to use BaseService
2. Refactor `services/custom_alert_engine.py` to use BaseService
3. Refactor `services/portfolio_manager.py` to use BaseService
4. *Repeat for all 11 services*

### Phase 3: GUI (After Services)
1. Refactor `gui/backtest.py` to use BaseTabWidget
2. Refactor `gui/custom_alerts.py` to use BaseTabWidget + extract dialogs
3. *Repeat for all 17 GUI tabs*

### Phase 4: Extract Utilities (Final Polish)
1. Create `utils/workers.py` - Generic worker thread base class
2. Create `utils/gui_helpers.py` - Form/table builders
3. Create `utils/constants.py` - Shared enums and constants

---

## Code Size Reduction Summary

| File | Current | After | Saved |
|------|---------|-------|-------|
| backtester.py | 633 | 400 | 233 |
| custom_alert_engine.py | 647 | 420 | 227 |
| backtest.py | 635 | 450 | 185 |
| custom_alerts.py | 677 | 480 | 197 |
| **Total (4 files)** | **2,592** | **1,750** | **842** |
| **11 services** | ~5,000 | ~3,400 | ~1,600 |
| **17 GUI tabs** | ~8,000 | ~5,600 | ~2,400 |
| **TOTAL PROJECT** | ~14,500 | ~11,700 | ~2,800 |

### Benefits
- ✅ 19% reduction in codebase
- ✅ Single source of truth for data models
- ✅ Consistent logging across all modules
- ✅ Centralized database connection management
- ✅ Easier to test and maintain
- ✅ Faster onboarding for new developers

---

## Quick Refactoring Checklist

For each service or GUI file:

```
SERVICE REFACTORING CHECKLIST:
☐ Add: from utils.base_service import BaseService
☐ Change: class MyService: → class MyService(BaseService):
☐ Change: super().__init__(db_path=db_path) in __init__
☐ Remove: self.logger = logging.getLogger(...)
☐ Remove: self.db = sqlite3.connect(...)
☐ Remove: self._cache = {} and cache methods
☐ Add: from utils.data_models import [needed dataclasses]
☐ Remove: duplicate @dataclass definitions
☐ Add: from utils.validators import [needed validators]
☐ Replace: custom validation with validators
☐ Test: Run service and verify functionality

GUI TAB REFACTORING CHECKLIST:
☐ Add: from utils.base_gui import BaseTabWidget
☐ Change: class MyTab(QWidget): → class MyTab(BaseTabWidget):
☐ Change: def init_ui(self): remains same
☐ Replace: QMessageBox.* with self.show_*()
☐ Extract worker thread logic to utils/workers.py
☐ Replace: manual worker creation with base worker
☐ Add: self.add_worker(worker) to track threads
☐ Test: Run tab and verify UI and dialogs work
```

---

## Notes

- Each refactor maintains 100% functionality (no behavior changes)
- All existing tests should pass after refactoring
- Use git commits for each file refactored (easier to review)
- Consider parallel refactoring of services and GUI tabs after foundation set

