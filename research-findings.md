# Python TUI Library Research: Real-Time Dashboard

**Research Date:** 2026-03-02  
**Target Use Case:** Martin Command Center - Real-time dashboard with 30-second auto-refresh, multi-panel layout, async data fetching

---

## Summary

| Library | Pros | Cons | Auto-Refresh | Code Complexity | Recommendation |
|---------|------|------|--------------|-----------------|----------------|
| **Textual** | Built on Rich, excellent async support, CSS-like layout system, first-party timer API | Steeper learning curve for layouts | ✅ Native `set_interval()` | Medium-High | **RECOMMENDED** |
| **Rich** | Beautiful rendering, Live display for updates, well-documented | Manual layout management, no built-in panels | ✅ Via Live display | Low-Medium | Good alternative |
| **Blessed** | Lightweight, simple API, good cross-platform | No built-in layout system, manual screen management | ⚠️ Manual | Low | Not recommended for dashboards |
| **Urwid** | Mature, full-featured | Heavy, dated API, steep learning curve | ⚠️ Manual | High | Overkill |
| **Dashing** | Purpose-built for dashboards | Not as actively maintained | ✅ Configurable | Low | Niche option |

---

## Detailed Analysis

### 1. Textual (RECOMMENDED) ⭐

**Overview:** Modern async-first TUI framework built on top of Rich. Actively maintained by the same author.

**Pros:**
- Native async support with `await` patterns
- Built-in `set_interval()` timer for auto-refresh (perfect for 30-second updates)
- Horizontal/Vertical container layouts for multi-panel dashboards
- CSS-like styling system
- Reactive attributes auto-refresh UI on data change
- Excellent documentation and examples
- Cross-platform (Windows, Mac, Linux)

**Cons:**
- Higher learning curve than Rich alone
- Requires understanding of widget composition

**Auto-Refresh Capability:** ⭐⭐⭐⭐⭐  
Built-in `set_interval(30, callback)` method - exactly what you need.

**Code Complexity:** Medium  
```python
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static
from textual import work

class DashboardApp(App):
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Vertical(Static("Panel 1", id="p1"), id="col1"),
            Vertical(Static("Panel 2", id="p2"), id="col2"),
        )
    
    def on_mount(self) -> None:
        self.set_interval(30, self.refresh_data)  # 30-second refresh
    
    @work(exclusive=True)
    async def refresh_data(self):
        data = await self.fetch_data()  # Async data fetching
        self.query_one("#p1", Static).update(f"Data: {data}")
    
    async def fetch_data(self):
        # Your async data fetching logic
        return "new data"

if __name__ == "__main__":
    app = DashboardApp()
    app.run()
```

---

### 2. Rich

**Overview:** Rich provides beautiful terminal rendering and includes a `Live` display for real-time updates.

**Pros:**
- Excellent visual rendering (colors, progress bars, tables)
- `Live` context manager for auto-updating displays
- Works on Windows natively
- Lower barrier to entry than Textual
- Can be combined with Textual

**Cons:**
- No built-in layout system (manual positioning)
- No native async - requires threading or manual coordination
- Multi-panel requires manual calculation

**Auto-Refresh Capability:** ⭐⭐⭐  
`Live` class with `refresh_per_second` parameter.

**Code Complexity:** Low-Medium  
```python
from rich.console import Console
from rich.live import Live
from rich.table import Table
import asyncio

console = Console()

async def main():
    with Live(console=console, refresh_per_second=0.033) as live:  # ~30 sec
        while True:
            data = await fetch_data()
            table = Table(title="Dashboard")
            table.add_column("Metric")
            table.add_column("Value")
            table.add_row("Status", str(data))
            live.update(table)
            await asyncio.sleep(30)

asyncio.run(main())
```

---

### 3. Blessed

**Overview:** Lightweight terminal manipulation library, predecessor to Rich.

**Pros:**
- Simple, minimal API
- Good cross-platform support
- Keyboard input handling
- Very lightweight

**Cons:**
- No layout system - manual cursor positioning
- No built-in auto-refresh
- Requires manual screen clearing/redrawing
- Not ideal for complex dashboards

**Auto-Refresh Capability:** ⭐⭐  
Manual implementation required.

**Code Complexity:** Low  
Not recommended for dashboard use case due to manual layout work.

---

### 4. Other Options

**Urwid:**
- Mature full-featured TUI library
- Good for complex interactive apps
- Cons: Heavy, dated API, steep learning curve
- Overkill for a simple dashboard

**Dashing:**
- Purpose-built for terminal dashboards
- Simple declarative syntax
- Cons: Less actively maintained
- Could work but limited community support

---

## Recommendation

### **Primary: Textual**

For the Martin Command Center requirements:
- ✅ 30-second auto-refresh: `set_interval(30, callback)`
- ✅ Multi-panel: `Horizontal()` + `Vertical()` containers
- ✅ Async data: Native `async`/`await` with `@work` decorator
- ✅ Clean professional look: Built-in styling system
- ✅ Windows support: Works natively

### **Alternative: Rich**

If you want simpler code and don't need complex layouts:
- Use `Live` display with manual table/panel rendering
- Requires threading or manual async handling
- Better for simpler single-panel dashboards

---

## Installation

```bash
pip install textual rich
```

---

## Reference Links

- Textual Docs: https://textual.textualize.io/
- Rich Live Display: https://rich.readthedocs.io/en/stable/live.html
- Textual Tutorial: https://textual.textualize.io/tutorial/
