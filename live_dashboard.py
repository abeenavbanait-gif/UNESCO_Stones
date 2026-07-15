"""
live_dashboard.py — Real-time terminal dashboard for the UNESCO scraper.

Shows:
  • Progress bar (sites fetched / total)
  • Live feed of latest sites being written
  • Field fill-rate stats (OUV, description, criteria, etc.)
  • ETA and throughput
  • Last 10 sites written to the checkpoint

Run: python3 live_dashboard.py
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

CHECKPOINT  = Path("cache/fetch_checkpoint.json")
JSON_OUTPUT = Path("data/unesco_master_list.json")
TOTAL       = 1248
REFRESH_SEC = 3   # how often to redraw

# ANSI colours
G  = "\033[92m"   # green
Y  = "\033[93m"   # yellow
C  = "\033[96m"   # cyan
B  = "\033[94m"   # blue
R  = "\033[91m"   # red
W  = "\033[97m"   # white bold
DIM= "\033[2m"
RST= "\033[0m"
CLS= "\033[2J\033[H"   # clear screen + home

BAR_WIDTH = 40


def progress_bar(done: int, total: int) -> str:
    pct   = done / total if total else 0
    filled= int(BAR_WIDTH * pct)
    bar   = "█" * filled + "░" * (BAR_WIDTH - filled)
    return f"{G}{bar}{RST} {W}{done:,}/{total:,}{RST} ({pct:.1%})"


def eta_str(done: int, total: int, elapsed_s: float) -> str:
    if done == 0 or elapsed_s == 0:
        return "calculating…"
    rate   = done / elapsed_s          # sites/sec
    remain = (total - done) / rate     # seconds left
    return f"{timedelta(seconds=int(remain))}  ({rate:.2f} sites/s)"


def load_checkpoint():
    if CHECKPOINT.exists():
        try:
            return json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        except Exception:
            pass
    if JSON_OUTPUT.exists():
        try:
            sites = json.loads(JSON_OUTPUT.read_text(encoding="utf-8"))
            return {"sites": sites, "completed_ids": [s.get("unesco_id", 0) for s in sites]}
        except Exception:
            pass
    return {"sites": [], "completed_ids": []}


def field_stats(sites):
    if not sites:
        return {}
    n = len(sites)
    return {
        "Description":  sum(1 for s in sites if s.get("brief_description", "").strip()),
        "OUV":          sum(1 for s in sites if s.get("ouv_statement", "").strip()),
        "Criteria":     sum(1 for s in sites if s.get("criteria", "").strip()),
        "Year":         sum(1 for s in sites if s.get("year_inscribed", 0)),
        "Country":      sum(1 for s in sites if s.get("country", "").strip()),
        "Category":     sum(1 for s in sites if s.get("category", "").strip()),
        "Endangered ⚠": sum(1 for s in sites if s.get("is_endangered")),
    }, n


def render(start_time: float):
    data     = load_checkpoint()
    sites    = data.get("sites", [])
    done     = len(data.get("completed_ids", sites))
    elapsed  = time.time() - start_time
    now_str  = datetime.now().strftime("%H:%M:%S")
    stats, n = field_stats(sites) if sites else ({}, 0)

    out = [CLS]
    out.append(f"{W}╔══════════════════════════════════════════════════════════════════╗{RST}")
    out.append(f"{W}║  🌍  UNESCO World Heritage Sites — Live Scraper Dashboard        ║{RST}")
    out.append(f"{W}╚══════════════════════════════════════════════════════════════════╝{RST}")
    out.append(f"   {DIM}Last update: {now_str}   Elapsed: {timedelta(seconds=int(elapsed))}{RST}\n")

    # Progress
    out.append(f"  {C}Progress{RST}")
    out.append(f"  {progress_bar(done, TOTAL)}")
    out.append(f"  {Y}ETA: {eta_str(done, TOTAL, elapsed)}{RST}\n")

    # Field fill rates
    if stats:
        out.append(f"  {C}Field Coverage  ({n} sites in checkpoint){RST}")
        for field, count in stats.items():
            pct = count / n * 100
            bar = "▓" * int(pct / 5) + "░" * (20 - int(pct / 5))
            colour = G if pct > 90 else (Y if pct > 50 else R)
            out.append(f"  {field:<16} {colour}{bar}{RST} {count:>5}/{n}  {pct:5.1f}%")
        out.append("")

    # Last 12 sites written
    recent = sites[-12:] if sites else []
    if recent:
        out.append(f"  {C}Latest sites written:{RST}")
        for s in reversed(recent):
            sid    = s.get("unesco_id", "?")
            name   = s.get("site_name", "Unknown")[:52]
            year   = s.get("year_inscribed", "—")
            cat    = s.get("category", "?")[:3]
            danger = f" {R}⚠ DANGER{RST}" if s.get("is_endangered") else ""
            ouv_ok = f"{G}✓ OUV{RST}" if s.get("ouv_statement") else f"{DIM}· OUV{RST}"
            dsc_ok = f"{G}✓ Desc{RST}" if s.get("brief_description") else f"{DIM}· Desc{RST}"
            out.append(
                f"  {DIM}[{sid:>5}]{RST} {W}{name:<52}{RST} "
                f"{DIM}{year} {cat}{RST} {ouv_ok} {dsc_ok}{danger}"
            )

    out.append(f"\n  {DIM}Refreshing every {REFRESH_SEC}s — Ctrl+C to exit{RST}")
    print("\n".join(out), flush=True)


def main():
    start = time.time()
    print(f"{C}Starting live dashboard… (Ctrl+C to stop){RST}")
    try:
        while True:
            render(start)
            time.sleep(REFRESH_SEC)
    except KeyboardInterrupt:
        print(f"\n{G}Dashboard closed.{RST}")


if __name__ == "__main__":
    main()
