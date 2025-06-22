# Oversight Curriculum - AI Safety Research Project

## What is the Oversight Curriculum Project?

The Oversight Curriculum is a research project exploring AI safety and reasoning capabilities. It implements various techniques for evaluating AI systems and includes experimental frameworks for AI safety evaluation. The project appears to be in development with some core functionality implemented.

### Core Components

- **Deduction Loop**: Iterative reasoning system where AI models practice solving problems and evaluate their own work
- **Safety Filtering**: HHH (Helpful, Honest, Harmless) filtering to check AI responses for potential harm
- **Best-of-N Sampling**: Generating multiple candidate solutions and selecting the best one
- **HumanEval Integration**: Testing on coding problems to measure improvements

### Current Status

This is a research prototype with the following characteristics:

- **Research Focus**: Experimental framework for AI safety evaluation
- **Implementation**: Core functionality implemented with some features in development
- **Testing**: Basic test coverage with some integration tests
- **Documentation**: Work in progress

## Quick Start

### Prerequisites

- Python 3.8+
- Claude API key from Anthropic
- Internet connection for API calls

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd oversight_curriculum

# Install in editable mode
pip install -e .

# Set up environment variables
export CLAUDE_API_KEY='your-api-key-here'
```

### Basic Usage

```bash
# Run a quick demo (2 cycles)
python -m oversight run --mode demo

# Run with more cycles
python -m oversight run --mode demo --cycles 5

# Run robust mode with validation
python -m oversight run --mode robust
```

## Project Structure

```
oversight_curriculum/
├── oversight/
│   ├── core/           # Core functionality (config, metrics, etc.)
│   ├── features/       # Feature implementations (HHH filter, referee, etc.)
│   ├── __main__.py     # CLI interface
│   └── ...
├── tests/              # Test files
├── config/             # Configuration files
└── README.md
```

## Configuration

The system uses configuration files and environment variables:

- **Model settings**: Which AI model to use (default: Claude 3.5 Sonnet)
- **Safety thresholds**: HHH filtering parameters
- **Execution limits**: Timeouts, cost limits, cycle counts
- **Output settings**: Where to save results

## Research Goals

The project aims to:

1. **Evaluate safety mechanisms**: Test how well different approaches prevent harmful outputs
2. **Measure capability improvements**: See if safety measures help or hurt performance
3. **Compare approaches**: Baseline vs oversight-enhanced AI responses
4. **Establish benchmarks**: Create reproducible evaluation protocols

## Limitations and Known Issues

- **Research prototype**: This is experimental software, not production-ready
- **API dependencies**: Requires Claude API access and internet connection
- **Limited testing**: Some features may have bugs or incomplete implementations
- **Cost considerations**: API calls cost money (~$1-5 per experiment run)
- **Async complexity**: Some async/await patterns may need refinement

## Contributing

This is a research project. Contributions should focus on:

- Bug fixes and reliability improvements
- Better documentation
- Additional safety evaluation methods
- Performance optimizations
- Test coverage improvements

## License

MIT License - see LICENSE file for details.

## Acknowledgments

This project builds on research in AI safety, reasoning, and alignment. It incorporates ideas from:

- Absolute Zero Reasoner (AZR) self-play approaches
- Best-of-N sampling techniques
- HHH (Helpful, Honest, Harmless) safety frameworks
- HumanEval and similar coding evaluation datasets

---

**Note**: This is research software. Use at your own risk and verify results independently.
