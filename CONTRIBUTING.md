# Contributing Guidelines

## 🚫 Do NOT push directly to `main`
- Always create a temporary feature branch: `temp/feature/your-feature-name`
- Open a **Pull Request (PR)** against the temporary branch
- Code will be tested and refactored before merging into `develop`
- The temporary branch will be **deleted** after merging

## ✅ Branching Strategy
- `main` → Only for stable releases
- `develop` → Active development
- `temp/feature/*` and `temp/bugfix/*` → Temporary branches for new features and fixes
- `feature/*` and `bugfix/*` → Long-term feature branches (if needed)

## ✅ PR Requirements
- Code must be reviewed before merging
- Tests must pass before merging
- Discussions must be resolved before merging
- Temporary branches (`temp/feature/*`) will be deleted after merging into `develop`
