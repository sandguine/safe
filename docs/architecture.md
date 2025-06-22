# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Oversight Curriculum                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   CLI Interface │    │  Configuration  │    │   Error     │ │
│  │   (__main__.py) │    │   Management    │    │  Handling   │ │
│  │                 │    │   (config.py)   │    │ (errors.py) │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│           │                       │                    │        │
│           └───────────────────────┼────────────────────┘        │
│                                   │                             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              OversightRunner (runner.py)                   │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │ │
│  │  │  Baseline   │ │  Oversight  │ │ Comparison  │          │ │
│  │  │ Experiment  │ │ Experiment  │ │   Analysis  │          │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘          │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                   │                             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Core Services                                  │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │ │
│  │  │ Deduction   │ │  Metrics    │ │   Referee   │          │ │
│  │  │   Loop      │ │ Collector   │ │   Safety    │          │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘          │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │ │
│  │  │   HHH       │ │ Best-of-N   │ │  Analysis   │          │ │
│  │  │  Filter     │ │  Sampler    │ │   Tools     │          │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘          │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                   │                             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              External APIs                                  │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │ │
│  │  │   Claude    │ │   Cost      │ │   Logging   │          │ │
│  │  │    API      │ │ Monitoring  │ │   System    │          │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘          │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### **CLI Interface** (`__main__.py`)
- Unified command-line interface
- Argument parsing and validation
- Mode selection (demo/robust/hackathon)
- Configuration management commands

### **Configuration Management** (`config.py`)
- Type-safe configuration with Pydantic
- YAML file loading and validation
- Environment variable integration
- Default value management

### **Error Handling** (`errors.py`)
- Domain-specific exception hierarchy
- Automatic API exception mapping
- Retry logic with exponential back-off
- Centralized error logging

### **OversightRunner** (`runner.py`)
- Main orchestration facade
- Dependency injection container
- Experiment execution coordination
- Results aggregation and reporting

### **Core Services**
- **DeductionLoop**: AZR self-play implementation
- **MetricsCollector**: Performance tracking and analysis
- **Referee**: Safety evaluation and filtering
- **HHHFilter**: Harm detection and prevention
- **BestOfNSampler**: Quality improvement through selection
- **Analysis**: Statistical analysis and reporting

## Data Flow

1. **Configuration Loading**: YAML + environment variables → Pydantic validation
2. **Runner Initialization**: Dependency injection of core services
3. **Baseline Experiment**: No oversight, raw performance measurement
4. **Oversight Experiment**: With safety filtering and quality controls
5. **Comparison Analysis**: Statistical comparison and improvement metrics
6. **Results Export**: JSON, CSV, and visualization outputs

## Quality Gates

- **Configuration Validation**: Type-safe config loading
- **Environment Validation**: API keys, directories, permissions
- **Safety Validation**: Referee and HHH filtering
- **Cost Validation**: Real-time cost monitoring and limits
- **Error Recovery**: Automatic retry with back-off
- **Test Coverage**: Unit, integration, and property-based tests 