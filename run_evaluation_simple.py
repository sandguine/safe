#!/usr/bin/env python3
"""
Simple Multi-Model Evaluation Runner
===================================

This script runs the fixed multi-model evaluation with proper error handling.
"""

import asyncio
import os
import sys
from pathlib import Path

# Load environment variables from .env file first
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables")
except Exception as e:
    print(f"⚠️ Error loading .env file: {e}")

# Add oversight to path
sys.path.insert(0, str(Path(__file__).parent))

def check_api_key():
    """Check if API key is available."""
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        print("❌ CLAUDE_API_KEY environment variable not found!")
        print("   Please set it with: export CLAUDE_API_KEY='your-api-key-here'")
        print("   Or create a .env file with: CLAUDE_API_KEY=your-key")
        return False

    # Mask API key for display
    masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
    print(f"✅ API key found: {masked_key}")

    # Check format
    if not api_key.startswith("sk-ant-"):
        print("❌ API key format appears invalid (should start with 'sk-ant-')")
        return False

    print("✅ API key format appears valid")
    return True

async def run_evaluation():
    """Run the fixed multi-model evaluation."""
    try:
        from fixed_multi_model_evaluation import FixedMultiModelEvaluator

        print("🚀 Starting Fixed Multi-Model Evaluation")
        print("=" * 60)

        # Initialize evaluator
        evaluator = FixedMultiModelEvaluator()
        print(f"✅ Evaluator initialized with {len(evaluator.models)} models")

        # Run evaluation
        results = await evaluator.run_comprehensive_evaluation()

        print("✅ Evaluation completed successfully!")
        return results

    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        return None

async def main():
    """Main function."""
    print("🔧 Fixed Multi-Model Evaluation")
    print("=" * 60)

    # Check API key
    if not check_api_key():
        print("\n❌ Cannot proceed without valid API key")
        sys.exit(1)

    # Clean old results
    old_results_dir = "results/multi_model_evaluation"
    if os.path.exists(old_results_dir):
        print(f"\n🧹 Removing old results: {old_results_dir}")
        import shutil
        shutil.rmtree(old_results_dir)
        print("✅ Old results removed")

    # Run evaluation
    print("\n🚀 Running evaluation...")
    results = await run_evaluation()

    if results:
        print("\n🎉 EVALUATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("📊 Results saved to: results/fixed_multi_model_evaluation/")
        print("📈 Charts saved to: results/fixed_multi_model_evaluation/charts/")
        print("📋 Logs saved to: results/fixed_multi_model_evaluation/logs/")
    else:
        print("\n❌ Evaluation failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
