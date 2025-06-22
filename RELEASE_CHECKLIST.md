# Release Checklist for Oversight Curriculum v1.0.0

## Pre-Release Validation

### ✅ Code Quality
- [ ] All tests pass: `pytest tests/`
- [ ] Code formatting: `black . && ruff check .`
- [ ] Type checking: `mypy src/`
- [ ] No TODO/FIXME comments in production code
- [ ] Documentation is up to date

### ✅ Package Configuration
- [ ] `pyproject.toml` has correct metadata
- [ ] Dependencies are properly specified
- [ ] License is MIT
- [ ] README.md is comprehensive
- [ ] CHANGELOG.md is updated

### ✅ Files Present
- [ ] `LICENSE` (MIT)
- [ ] `CITATION.cff` (for academic credit)
- [ ] `CHANGELOG.md` (with v1.0.0 entry)
- [ ] `README.md` (with proper badges)
- [ ] `pyproject.toml` (with all metadata)

## Release Process

### 1. Automated Release
```bash
# Run the automated release script
./scripts/release.sh
```

### 2. Manual Steps (if needed)
```bash
# Clean working directory
git clean -xfd

# Install package in editable mode
pip install -e .

# Run smoke test
python scripts/release_smoke_test.py

# Build package
python -m build

# Validate with twine
twine check dist/*

# Create git tag
git tag v1.0.0

# Push tag
git push origin v1.0.0

# Upload to PyPI
twine upload dist/*
```

## Post-Release Verification

### ✅ PyPI
- [ ] Package appears on PyPI: https://pypi.org/project/oversight-curriculum/
- [ ] README renders correctly on PyPI
- [ ] All metadata is displayed properly
- [ ] Download statistics are available

### ✅ Installation
- [ ] Package installs with pip: `pip install oversight-curriculum`
- [ ] CLI works: `python -m oversight_curriculum.src --help`
- [ ] Import works: `import oversight_curriculum`

### ✅ Documentation
- [ ] GitHub repository is updated
- [ ] Release notes are published
- [ ] Documentation links work

## Version Management

### Current Version: v1.0.0
- **Major**: 1 (first stable release)
- **Minor**: 0 (no new features)
- **Patch**: 0 (no bug fixes)

### Future Versions
- **v1.0.1**: Bug fixes
- **v1.1.0**: New features
- **v2.0.0**: Breaking changes

## Success Criteria

- [ ] Package successfully uploaded to PyPI
- [ ] All smoke tests pass
- [ ] Documentation is accessible
- [ ] Installation works on clean environments
- [ ] No critical issues reported

## Rollback Plan

If issues are discovered after release:

1. **Immediate**: Create v1.0.1 with fixes
2. **Documentation**: Update README with known issues
3. **Communication**: Notify users of any problems
4. **Investigation**: Root cause analysis for future prevention

---

**Release Date**: December 21, 2024  
**Release Manager**: Oversight Curriculum Team  
**Status**: Ready for Release 🚀 