# 🚀 Quick Start Guide

## Setup Instructions (5 minutes)

### Step 1: Install uv (if not already installed)

```powershell
# Windows PowerShell (run as user, not admin)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2: Navigate to Project

```bash
cd C:\Users\brene\AppData\Local\AnthropicClaude\app-1.0.1307\workspace\portkodiak-aishield
```

### Step 3: Initialize Git (First Time Only)

```bash
git init
git add .
git commit -m "Initial project structure - Phase 0 complete"
```

### Step 4: Install Dependencies

```bash
# This will take 2-3 minutes
uv sync
```

### Step 5: Install Pre-commit Hooks

```bash
uv run pre-commit install
```

### Step 6: Test Development Environment

```bash
# This should run without errors
uv run dev
```

You should see:
```
============================================================
PortKodiakAIShield - Development Mode
============================================================
Python version: 3.11.x
Working directory: C:\...\portkodiak-aishield
Development environment ready!
Press Ctrl+C to stop
```

Press `Ctrl+C` to stop.

### Step 7: Run Tests

```bash
uv run pytest
```

You should see 3 tests passing.

---

## ✅ Verification Checklist

After completing the steps above, verify:

- [ ] `uv --version` shows uv is installed
- [ ] `uv sync` completed without errors
- [ ] `uv run dev` launches successfully
- [ ] `uv run pytest` shows all tests passing
- [ ] Git repository initialized (`.git` folder exists)
- [ ] Pre-commit hooks installed

---

## 🎯 What's Next?

You've completed **Phase 0: Project Setup**! 🎉

### Check Your Progress

Open `PROJECT_STATUS.md` to see current status.

### Next Steps (Phase 1)

1. Review the roadmap in `ROADMAP.md`
2. Read `docs/developer_guide.md`
3. Start Phase 1, Iteration 1.1: Windows Service Skeleton

### Useful Commands

```bash
# Development
uv run dev                    # Start dev environment
uv run portkodiak-service     # Run service
uv run portkodiak-ui          # Launch UI

# Testing
uv run pytest                 # Run all tests
uv run pytest tests/unit      # Unit tests only
uv run pytest --cov           # With coverage

# Code Quality
uv run ruff check .           # Linting
uv run black .                # Formatting
uv run mypy app/              # Type checking

# Pre-commit
uv run pre-commit run --all-files  # Run all hooks
```

---

## 🐛 Troubleshooting

### "uv: command not found"

**Solution:** Add uv to PATH or restart terminal after installation.

```powershell
# Check if uv is in PATH
$env:Path
```

### "Python version not found"

**Solution:** Install Python 3.11+

```bash
# uv can install Python for you
uv python install 3.11
```

### "pytest: No module named 'app'"

**Solution:** Make sure you're in the project root directory and ran `uv sync`

```bash
cd portkodiak-aishield
uv sync
```

### "Permission denied" on Windows

**Solution:** Some operations need admin privileges

```powershell
# Run PowerShell as Administrator for service-related tasks
```

---

## 📚 Documentation Links

- [Full Roadmap](ROADMAP.md) - Complete project plan
- [Developer Guide](docs/developer_guide.md) - Development setup
- [Project Status](PROJECT_STATUS.md) - Current progress
- [GPL Compliance](docs/compliance/gpl_obligations.md) - License info

---

## 🆘 Need Help?

1. Check `PROJECT_STATUS.md` for current state
2. Review `ROADMAP.md` for what comes next
3. Read `docs/developer_guide.md` for detailed instructions
4. Open an issue on GitHub (after creating repo)

---

**Congratulations! Your development environment is ready! 🎉**

Now you can start building the Windows Application Firewall with ML-based Anomaly Detection.
