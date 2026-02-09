# Install GitHub CLI (gh)

## Quick Install (Windows)

Open PowerShell as **Administrator** and run:

```powershell
winget install --id GitHub.cli
```

**Alternative methods if winget not available:**

### Method 2: Chocolatey
```powershell
choco install gh
```

### Method 3: Scoop
```powershell
scoop install gh
```

### Method 4: Direct Download
Download installer from: https://cli.github.com/

---

## After Installation

1. **Close and reopen PowerShell** (to refresh PATH)

2. **Authenticate with GitHub:**
   ```powershell
   gh auth login
   ```

   Follow the prompts:
   - Choose: GitHub.com
   - Choose: HTTPS
   - Authenticate with: Browser (easiest)

3. **Verify it works:**
   ```powershell
   gh --version
   gh auth status
   ```

4. **Navigate back to repo:**
   ```powershell
   cd C:\Users\nliga\OneDrive\Documents\Repos\intentgraph
   ```

5. **Create the PRs:**
   ```powershell
   .\create-prs.bat
   ```

---

## Expected Output After Installation

```
gh version 2.x.x (latest)
✓ Logged in to github.com as Raytracer76
```

Then you're ready to create PRs!
