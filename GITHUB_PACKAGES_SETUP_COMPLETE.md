# 📦 GitHub Packages - Complete Setup for ScanHero

## 🎯 Get Started with GitHub Packages

GitHub Packages allows you to:
- **Safely publish packages** with version control
- **Store packages alongside your code** in the same repository  
- **Share packages privately** with your team
- **Use familiar GitHub workflows** for package management

## 🔧 Step 1: Enable GitHub Packages in Repository

### Enable Packages for Your Repository:
1. Go to: https://github.com/ahmetxhero/scanhero
2. Click **Settings** tab
3. Scroll down to **Packages** section
4. Click **Enable GitHub Packages** (if not already enabled)

## 🔑 Step 2: Create GitHub Personal Access Token

### Create Token with Packages Permission:
1. Go to: https://github.com/settings/tokens
2. Click **Generate new token (classic)**
3. Give it a name: "ScanHero Packages"
4. Select these scopes:
   - ✅ `write:packages` (to upload packages)
   - ✅ `read:packages` (to download packages)
   - ✅ `repo` (to access repository)
5. Click **Generate token**
6. **Copy the token** (starts with `ghp_`)

## 📝 Step 3: Configure Local Environment

### Create .pypirc file (locally, don't commit to git):
```bash
# Create .pypirc in your home directory
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

### Method 1: Use the Upload Script
```bash
./github_packages_upload.sh
```

### Method 2: Manual Upload
```bash
source venv/bin/activate
twine upload --repository github dist/scanhero-1.0.0*
```

### Method 3: Direct Command
```bash
source venv/bin/activate
twine upload --repository-url https://upload.pypi.org/legacy/ --username __token__ --password YOUR_GITHUB_TOKEN dist/scanhero-1.0.0*
```

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

## 🔐 Step 6: Authentication for Team Members

### For users installing your package:

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

### 📊 GitHub Packages vs PyPI:

| Feature | PyPI | GitHub Packages |
|---------|------|-----------------|
| **Public Access** | ✅ Global | ✅ GitHub users |
| **Private Packages** | ❌ Paid | ✅ Free |
| **Version Control** | ❌ Limited | ✅ Full history |
| **Integration** | ❌ Separate | ✅ With code |
| **Cost** | ✅ Free | ✅ Free for public |
| **Team Sharing** | ❌ Limited | ✅ Excellent |

## 🚀 Quick Start Commands

### Upload to GitHub Packages:
```bash
# Get your GitHub token first, then:
./github_packages_upload.sh
```

### Or use manual command:
```bash
source venv/bin/activate
twine upload --repository-url https://upload.pypi.org/legacy/ --username __token__ --password YOUR_GITHUB_TOKEN dist/scanhero-1.0.0*
```

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

### Next Steps:
1. Get GitHub token with packages permissions
2. Run: `./github_packages_upload.sh`
3. Test installation from GitHub Packages
