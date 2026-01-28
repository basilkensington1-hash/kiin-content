# A/B Testing Framework

A practical A/B testing system for Kiin content optimization.

## Quick Commands

```bash
# Create a new test
python3 ab_testing.py --create-test --content-type validation --variations 3

# Log results 
python3 ab_testing.py --log-result --test-id abc123 --variation A --views 1000 --saves 50

# Generate report
python3 ab_testing.py --report --test-id abc123

# List all tests
python3 ab_testing.py --list-tests
```

## What It Does

- **Generates content variations** with different hooks, colors, voice, and music
- **Tracks performance metrics** like views, saves, shares, comments
- **Analyzes results** to identify winning variations
- **Provides statistical guidance** for meaningful tests

## Files

- `ab_testing.py` - Main testing script
- `../config/ab_tests.json` - Test configuration and templates
- `../config/ab_test_results/` - Test data and results
- `../docs/AB_TESTING_GUIDE.md` - Complete documentation

## Example Workflow

1. **Plan**: Decide what to test (hook style, colors, voice tone)
2. **Create**: `python3 ab_testing.py --create-test --content-type tips --variations 3`
3. **Build**: Create content using generated variation specs
4. **Track**: Log performance data daily
5. **Analyze**: Generate reports to find winners
6. **Iterate**: Use insights for next test

See the [complete guide](../docs/AB_TESTING_GUIDE.md) for detailed instructions and best practices.