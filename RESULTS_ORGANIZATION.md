# Results Organization System

## Overview

The results organization system provides a clean, structured approach to managing demo outputs and analysis results.

## New Structure

### Directory Organization

```
results/
├── latest/                    # Symlink to most recent enhanced demo
├── enhanced_demo_YYYYMMDD_HHMMSS/
│   ├── data.json             # Complete raw results and logs
│   ├── report.txt            # Detailed human-readable report
│   └── summary.md            # Key metrics and insights (markdown)
└── evaluation_YYYYMMDD_HHMMSS/
    ├── data.json             # Evaluation data
    └── report.txt            # Evaluation report
```

### File Naming Convention

- **Enhanced Demo Results**: `enhanced_demo_YYYYMMDD_HHMMSS/`
- **Evaluation Results**: `evaluation_YYYYMMDD_HHMMSS/`
- **Consistent Internal Files**: `data.json`, `report.txt`, `summary.md`

## Benefits

### 1. **Clean Organization**

- No more scattered files in root directory
- Logical grouping by experiment type and timestamp
- Consistent file naming across all results

### 2. **Easy Access**

- `results/latest/` symlink always points to most recent enhanced demo
- Automatic detection by plotting scripts
- Clear separation between different experiment types

### 3. **Comprehensive Documentation**

- `summary.md` provides key metrics at a glance
- `report.txt` contains detailed analysis
- `data.json` stores complete raw data for further analysis

### 4. **Automated Workflow**

- Demo automatically creates organized structure
- Plotting scripts auto-detect latest results
- Organization script cleans up old scattered files

## Usage

### Running the Demo

```bash
python enhanced_demo.py
# Results automatically saved to: results/enhanced_demo_YYYYMMDD_HHMMSS/
```

### Accessing Results

```bash
# View latest results
ls results/latest/

# View specific results
ls results/enhanced_demo_20250622_115347/

# Read summary
cat results/latest/summary.md
```

### Generating Plots

```bash
# Auto-detect latest results
python plot_results.py

# Specify specific results
python plot_results.py --results results/enhanced_demo_20250622_115347/data.json
```

### Organizing Old Files

```bash
# Clean up scattered files
python organize_results.py
```

## Migration from Old System

The organization script (`organize_results.py`) automatically:

1. Finds all scattered result files
2. Creates organized directory structure
3. Moves and renames files appropriately
4. Creates summary files for old data
5. Sets up latest symlink

## File Types

### Enhanced Demo Results

- **data.json**: Complete logged data including all completions, scores, and safety results
- **report.txt**: Human-readable detailed report with insights
- **summary.md**: Markdown summary with key metrics and next steps

### Evaluation Results

- **data.json**: Evaluation data and metrics
- **report.txt**: Evaluation report and analysis

## Integration with Analysis Tools

- **Plotting Script**: Automatically detects latest results via symlink
- **Analysis Tools**: Can work with any organized results directory
- **Documentation**: Summary files provide quick overview of results

## Future Enhancements

1. **Version Control**: Track changes in results over time
2. **Comparison Tools**: Compare results between different runs
3. **Metadata**: Add experiment configuration and parameters
4. **Export Formats**: Support for different output formats (CSV, Excel, etc.)

---

*This system provides a foundation for scalable, organized result management.*
