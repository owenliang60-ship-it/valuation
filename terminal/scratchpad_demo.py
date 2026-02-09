"""
Demo script showing how to use the AnalysisScratchpad system.

Run this to see example scratchpad creation and replay.
"""
from terminal.scratchpad import AnalysisScratchpad, read_scratchpad
from terminal.commands import list_analysis_scratchpads, replay_analysis_scratchpad
import json


def demo_scratchpad_creation():
    """Demonstrate creating a scratchpad with various events."""
    print("=" * 60)
    print("DEMO: Creating Analysis Scratchpad")
    print("=" * 60)

    # Create scratchpad
    scratchpad = AnalysisScratchpad(
        symbol="NVDA",
        depth="full",
        query="Analyze NVDA investment opportunity"
    )

    print(f"\n✓ Scratchpad created: {scratchpad.log_path}")
    print(f"  Symbol: {scratchpad.symbol}")
    print(f"  Depth: {scratchpad.depth}")
    print(f"  Hash: {scratchpad.hash}")

    # Simulate tool calls
    print("\n[Step 1] Fetching price data...")
    scratchpad.log_tool_call(
        "FMPPriceTool",
        {"symbol": "NVDA", "days": 60},
        {
            "current_price": 880.5,
            "52w_high": 900.0,
            "52w_low": 450.0,
            "volume": 40_000_000,
        }
    )

    print("[Step 2] Fetching fundamentals...")
    scratchpad.log_tool_call(
        "FMPFundamentalTool",
        {"symbol": "NVDA", "period": "quarter"},
        {
            "revenue": 22_000_000_000,
            "net_income": 12_000_000_000,
            "gross_margin": 0.75,
            "operating_margin": 0.62,
        }
    )

    # Simulate reasoning
    print("[Step 3] Valuation analysis...")
    scratchpad.log_reasoning(
        "valuation_check",
        "PE ratio 60x vs historical avg 45x. Premium justified by: "
        "(1) AI datacenter boom driving 100%+ revenue growth, "
        "(2) Gross margins expanding to 75% on H100/H200 mix, "
        "(3) Moat strengthening with CUDA ecosystem lock-in."
    )

    print("[Step 4] Growth lens complete...")
    scratchpad.log_lens_complete(
        "growth_story",
        "data/companies/NVDA/analyses/growth_story_2026-02-08.md"
    )

    print("[Step 5] Risk assessment...")
    scratchpad.log_reasoning(
        "risk_assessment",
        "Key risks: (1) Customer concentration - hyperscalers 40% of revenue, "
        "(2) AMD competition in MI300 series, (3) China export controls. "
        "Mitigation: diversifying into automotive/edge AI."
    )

    print("[Step 6] Final OPRMS rating...")
    scratchpad.log_final_rating({
        "dna": "S",
        "timing": "A",
        "timing_coeff": 1.0,
        "position_pct": 22.5,
        "evidence": [
            "Q4 earnings +265% YoY",
            "H100 backlog through Q3 2024",
            "CUDA dominance = 95% market share"
        ],
        "investment_bucket": "AI Infrastructure",
        "thesis": "Once-in-a-decade AI infrastructure buildout with monopolistic provider"
    })

    print("\n✓ Scratchpad complete!")
    return scratchpad.log_path


def demo_scratchpad_replay(log_path):
    """Demonstrate replaying a scratchpad."""
    print("\n" + "=" * 60)
    print("DEMO: Replaying Scratchpad")
    print("=" * 60)

    result = replay_analysis_scratchpad(str(log_path))

    print(f"\n📋 Query Info:")
    print(f"   Symbol: {result['query']['symbol']}")
    print(f"   Depth: {result['query']['depth']}")
    print(f"   Query: {result['query']['query']}")

    print(f"\n📊 Stats:")
    for key, value in result['stats'].items():
        print(f"   {key}: {value}")

    print(f"\n📅 Timeline:")
    for i, event in enumerate(result['timeline'][:8], 1):  # Show first 8
        print(f"   {i}. [{event['type']}] {event['summary'][:80]}")

    if result['final_rating']:
        print(f"\n⭐ Final Rating:")
        rating = result['final_rating']
        print(f"   DNA: {rating['dna']}, Timing: {rating['timing']}")
        print(f"   Position: {rating['position_pct']}%")
        print(f"   Bucket: {rating.get('investment_bucket', 'N/A')}")


def demo_list_scratchpads():
    """Demonstrate listing scratchpads."""
    print("\n" + "=" * 60)
    print("DEMO: Listing Scratchpads")
    print("=" * 60)

    result = list_analysis_scratchpads("NVDA", limit=5)

    print(f"\n📂 Found {result['count']} scratchpad(s) for {result['symbol']}")
    print(f"   (Total available: {result['total_available']})")

    for i, sp in enumerate(result['scratchpads'], 1):
        print(f"\n   {i}. {sp['filename']}")
        print(f"      Timestamp: {sp['timestamp']}")
        print(f"      Depth: {sp['depth']}")
        print(f"      Events: {sp['events_count']}")
        print(f"      Query: {sp['query'][:60]}...")


if __name__ == "__main__":
    # Run demo
    log_path = demo_scratchpad_creation()
    demo_scratchpad_replay(log_path)
    demo_list_scratchpads()

    print("\n" + "=" * 60)
    print("✅ Demo complete!")
    print("=" * 60)
    print(f"\nScratchpad saved to: {log_path}")
    print("You can inspect it with: cat", log_path)
