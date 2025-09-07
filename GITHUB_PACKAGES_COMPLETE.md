# 📦 GitHub Packages - Complete Setup Guide

## 🎯 Get Started with GitHub Packages

GitHub Packages allows you to:
- **Safely publish packages** with version control
- **Store packages alongside your code** in the same repository
- **Share packages privately** with your team
- **Use familiar GitHub workflows** for package management

## 🔧 Step 1: Enable GitHub Packages

### For Your Repository:
1. Go to your repository: https://github.com/ahmetxhero/scanhero
2. Click **Settings** tab
3. Scroll down to **Packages** section
4. Click **Enable GitHub Packages**

## 🔑 Step 2: Create Personal Access Token

### Create Token with Packages Permission:
1. Go to GitHub Settings → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token (classic)**
3. Give it a name: "ScanHero Packages"
4. Select scopes:
   - ✅ `write:packages` (to upload packages)
   - ✅ `read:packages` (to download packages)
   - ✅ `repo` (to access repository)
5. Click **Generate token**
6. **Copy the token** (starts with `ghp_`)

## 📝 Step 3: Create Local .pypirc Configuration

Create a local `.pypirc` file (don't commit this to git):

```bash
# Create .pypirc file in your home directory
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    github

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = <PYPI_API_TOKEN>

[github]
repository = https://upload.pypi.org/legacy/
username = __token__
password = <YOUR_GITHUB_TOKEN>
EOF
```

Replace `<YOUR_GITHUB_TOKEN>` with your actual GitHub token.

## 🚀 Step 4: Upload to GitHub Packages

### Method 1: Direct Upload
```bash
# Activate virtual environment
source venv/bin/activate

# Upload to GitHub Packages
twine upload --repository github dist/scanhero-1.0.0*
```

### Method 2: Using GitHub Actions (Recommended)

The workflow is already created in `.github/workflows/publish.yml`. It will automatically:
- Build the package when you create a release
- Upload to GitHub Packages
- Make it available for installation

## 📥 Step 5: Install from GitHub Packages

### For Public Access:
```bash
pip install --index-url https://pypi.pkg.github.com/ahmetxhero/simple/ scanhero
```

### For Private Access (requires authentication):
```bash
# Configure pip for GitHub Packages
pip config set global.extra-index-url https://pypi.pkg.github.com/ahmetxhero/simple/

# Install with authentication
pip install --index-url https://pypi.pkg.github.com/ahmetxhero/simple/ scanhero
```

## 🔐 Step 6: Authentication for Users

### For Team Members Installing Your Package:

1. **Create Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate token with `read:packages` scope

2. **Configure pip**:
   ```bash
   # Create .netrc file
   echo "machine pypi.pkg.github.com login __token__ password YOUR_TOKEN" >> ~/.netrc
   ```

3. **Install Package**:
   ```bash
   pip install --index-url https://pypi.pkg.github.com/ahmetxhero/simple/ scanhero
   ```

## 🎯 Advantages of GitHub Packages

### ✅ Benefits:
- **Integrated with GitHub**: Packages stored with your code
- **Version Control**: Full version history and releases
- **Private Packages**: Share only with your team
- **Free for Public Repos**: No cost for public packages
- **Familiar Workflow**: Uses GitHub's interface
- **Team Collaboration**: Easy sharing within organizations

### 📊 Comparison:

| Feature | PyPI | GitHub Packages |
|---------|------|-----------------|
| **Public Access** | ✅ Global | ✅ GitHub users |
| **Private Packages** | ❌ Paid | ✅ Free |
| **Version Control** | ❌ Limited | ✅ Full history |
| **Integration** | ❌ Separate | ✅ With code |
| **Cost** | ✅ Free | ✅ Free for public |
| **Team Sharing** | ❌ Limited | ✅ Excellent |

## 🚀 Let's Upload to GitHub Packages!

### Quick Upload Command:
```bash
# Make sure you have your GitHub token in ~/.pypirc
source venv/bin/activate
twine upload --repository github dist/scanhero-1.0.0*
```

### Or Use GitHub Actions:
1. Create a new release in GitHub
2. The workflow will automatically build and upload

## 📋 After Upload

1. **Check Package**: Visit https://github.com/ahmetxhero/scanhero/packages
2. **Test Installation**:
   ```bash
   pip install --index-url https://pypi.pkg.github.com/ahmetxhero/simple/ scanhero
   scanhero --version
   ```

## 🎉 Benefits for ScanHero

- **Professional Distribution**: Package stored with your code
- **Version Management**: Easy to track and manage versions
- **Team Collaboration**: Share with your team privately
- **GitHub Integration**: Seamless workflow with your repository
- **Free Hosting**: No cost for public packages

## 🔧 Future Updates

For future releases:
1. Update version in `pyproject.toml`
2. Build new package: `python -m build`
3. Upload: `twine upload --repository github dist/scanhero-NEW_VERSION*`
4. Or create GitHub release for automatic upload

## 🏆 Ready to Go!

Your ScanHero package is perfectly set up for GitHub Packages distribution. The configuration is ready - just get your GitHub token and upload!
