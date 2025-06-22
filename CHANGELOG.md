# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-21

### Added
- **OversightRunner**: Unified facade for oversight curriculum execution with dependency injection
- **Configuration System**: Type-safe configuration management using Pydantic with YAML support
- **Domain-Specific Exceptions**: Comprehensive error handling with retry/back-off logic
- **DeductionLoop**: Core AZR self-play system with propose/solve cycles
- **Safety Filters**: 
  - Referee system for content safety evaluation
  - HHH filter for harm detection and prevention
  - Best-of-N sampling for progressive solution generation
- **Metrics System**: Comprehensive metrics collection and comparison analysis
- **CLI Interface**: Unified command-line interface for all operations
- **Testing Infrastructure**: Unit tests, integration tests, and property-based testing
- **Professional Tooling**: Pre-commit hooks, linting, and code formatting
- **Documentation**: Comprehensive README with architecture diagrams and examples

### Features
- **Demo Mode**: Quick execution for demonstrations (≤15s)
- **Robust Mode**: Full validation with comprehensive reporting
- **Hackathon Mode**: Optimized for presentations and live demos
- **Cost Management**: Automatic cost monitoring and limits
- **Real-time Monitoring**: Live metrics and progress tracking
- **Error Recovery**: Automatic retry with exponential back-off
- **Output Generation**: CSV, JSON, and plot exports

### Technical Improvements
- Modular architecture with clear separation of concerns
- Type-safe configuration with environment variable support
- Comprehensive error handling and logging
- Cross-platform compatibility
- Professional development workflow with pre-commit hooks

### Documentation
- Architecture overview and diagrams
- Quick start guide with examples
- Configuration reference
- API documentation
- Testing guide
- Deployment instructions

## [Unreleased]

### Planned
- Additional safety filters and evaluation metrics
- Enhanced visualization and reporting
- Performance optimizations
- Extended test coverage
- Additional execution modes 