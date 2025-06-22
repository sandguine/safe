"""
Unified CLI interface for oversight curriculum.
Allows running the system as: python -m oversight run --mode demo
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from runner import OversightRunner, RunnerConfig, ExecutionMode
from config import load_settings, get_execution_config


def create_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Oversight Curriculum - AI Safety & Reasoning System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m oversight run --mode demo
  python -m oversight run --mode robust --cycles 10
  python -m oversight run --mode hackathon --config custom_config.yaml
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run oversight experiments')
    run_parser.add_argument(
        '--mode',
        choices=['demo', 'robust', 'hackathon'],
        default='demo',
        help='Execution mode (default: demo)'
    )
    run_parser.add_argument(
        '--cycles',
        type=int,
        help='Number of cycles (overrides config)'
    )
    run_parser.add_argument(
        '--config',
        type=str,
        help='Configuration file path'
    )
    run_parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory (overrides config)'
    )
    run_parser.add_argument(
        '--model',
        type=str,
        help='Model name (overrides config)'
    )
    run_parser.add_argument(
        '--enable-referee',
        action='store_true',
        help='Enable referee safety filtering'
    )
    run_parser.add_argument(
        '--disable-referee',
        action='store_true',
        help='Disable referee safety filtering'
    )
    run_parser.add_argument(
        '--enable-hhh',
        action='store_true',
        help='Enable HHH safety filtering'
    )
    run_parser.add_argument(
        '--disable-hhh',
        action='store_true',
        help='Disable HHH safety filtering'
    )
    run_parser.add_argument(
        '--enable-best-of-n',
        action='store_true',
        help='Enable best-of-n sampling'
    )
    run_parser.add_argument(
        '--disable-best-of-n',
        action='store_true',
        help='Disable best-of-n sampling'
    )
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument(
        '--show',
        action='store_true',
        help='Show current configuration'
    )
    config_parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate configuration file'
    )
    config_parser.add_argument(
        '--file',
        type=str,
        help='Configuration file to validate'
    )
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument(
        '--unit',
        action='store_true',
        help='Run unit tests'
    )
    test_parser.add_argument(
        '--integration',
        action='store_true',
        help='Run integration tests'
    )
    test_parser.add_argument(
        '--coverage',
        action='store_true',
        help='Run tests with coverage'
    )
    test_parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )
    
    return parser


def load_runner_config(args: argparse.Namespace) -> RunnerConfig:
    """Load runner configuration from arguments and config file"""
    # Load settings
    settings = load_settings(args.config)
    
    # Get execution config for the mode
    exec_config = get_execution_config(args.mode)
    
    # Create runner config with overrides
    config = RunnerConfig(
        mode=ExecutionMode(args.mode),
        cycles=args.cycles or exec_config.cycles,
        max_puzzles_per_cycle=exec_config.max_puzzles_per_cycle,
        max_solutions_per_puzzle=exec_config.max_solutions_per_puzzle,
        enable_referee=not args.disable_referee and (args.enable_referee or exec_config.enable_referee),
        enable_hhh_filter=not args.disable_hhh and (args.enable_hhh or exec_config.enable_hhh_filter),
        enable_best_of_n=not args.disable_best_of_n and (args.enable_best_of_n or exec_config.enable_best_of_n),
        model_name=args.model or settings.model.name,
        output_dir=args.output_dir or settings.output.base_dir
    )
    
    return config


async def run_command(args: argparse.Namespace) -> int:
    """Execute the run command"""
    try:
        # Load configuration
        config = load_runner_config(args)
        
        print(f"Starting oversight curriculum in {args.mode} mode...")
        print(f"Configuration: {config}")
        
        # Create runner
        runner = OversightRunner(config)
        
        # Run based on mode
        if args.mode == "demo":
            results = await runner.run_demo()
        elif args.mode == "robust":
            results = await runner.run_robust()
        else:
            results = await runner.run_comparison()
        
        print(f"Execution completed successfully!")
        print(f"Results saved to: {config.output_dir}")
        
        return 0
        
    except Exception as e:
        print(f"Error during execution: {e}", file=sys.stderr)
        return 1


def config_command(args: argparse.Namespace) -> int:
    """Execute the config command"""
    try:
        if args.show:
            settings = load_settings(args.file)
            print("Current configuration:")
            print(f"Model: {settings.model.name}")
            print(f"Output directory: {settings.output.base_dir}")
            print(f"Cost limit: ${settings.cost.max_usd_per_run}")
            print(f"Logging level: {settings.logging.level}")
            
        elif args.validate:
            config_file = args.file or "config/settings.yaml"
            try:
                settings = load_settings(config_file)
                print(f"Configuration file {config_file} is valid!")
                return 0
            except Exception as e:
                print(f"Configuration file {config_file} is invalid: {e}", file=sys.stderr)
                return 1
        
        return 0
        
    except Exception as e:
        print(f"Error in config command: {e}", file=sys.stderr)
        return 1


def test_command(args: argparse.Namespace) -> int:
    """Execute the test command"""
    import subprocess
    import sys
    
    try:
        cmd = ["pytest"]
        
        if args.unit:
            cmd.extend(["tests/test_*.py"])
        elif args.integration:
            cmd.extend(["tests/integration/"])
        else:
            cmd.extend(["tests/"])
        
        if args.coverage:
            cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
        
        if args.verbose:
            cmd.append("-v")
        
        # Run pytest
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
        return result.returncode
        
    except Exception as e:
        print(f"Error running tests: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'run':
        return asyncio.run(run_command(args))
    elif args.command == 'config':
        return config_command(args)
    elif args.command == 'test':
        return test_command(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 