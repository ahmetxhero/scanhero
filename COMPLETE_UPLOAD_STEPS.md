# 🚀 Complete PyPI Upload Steps for ScanHero

## 📋 Current Status
✅ Package built successfully  
✅ Quality checks passed  
✅ GitHub repository created  
❌ PyPI upload pending (authentication needed)

## 🔑 Step 1: Get PyPI API Token

### Option A: Create New API Token
1. Go to https://pypi.org/manage/account/
2. Scroll down to "API tokens"
3. Click "Add API token"
4. Name: "ScanHero Upload"
5. Scope: "Entire account" (or create project-specific)
6. **Copy the token** (starts with `pypi-`)

### Option B: Use Existing Token
If you already have a PyPI API token, use that.

## 🔧 Step 2: Update Configuration

You have two options:

### Option A: Update .pypirc file
```bash
# Edit your .pypirc file
nano ~/.pypirc
```

Replace `<PYPI_API_TOKEN>` with your actual token:
```
[distutils]
index-servers =
    pypi
    github

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-actual-token-here

[github]
repository = https://upload.pypi.org/legacy/
username = __token__
password = <GITHUB_PAT>
```

### Option B: Use Command Line (Recommended)
Skip editing files and use command line authentication:

```bash
source venv/bin/activate
twine upload --username __token__ --password pypi-your-actual-token-here dist/*
```

## 🎯 Step 3: Upload to PyPI

### Recommended: TestPyPI First
```bash
# 1. Create TestPyPI account at https://test.pypi.org/account/register/
# 2. Upload to TestPyPI
source venv/bin/activate
twine upload --repository-url https://test.pypi.org/legacy/ --username __token__ --password pypi-your-test-token dist/*

# 3. Test installation
pip install --index-url https://test.pypi.org/simple/ scanhero
```

### Production PyPI Upload
```bash
source venv/bin/activate
twine upload dist/*
```

## 🔍 Step 4: Verify Upload

After successful upload:

1. **Check PyPI**: https://pypi.org/project/scanhero/
2. **Test Installation**:
   ```bash
   pip install scanhero
   scanhero --version
   scanhero scan 127.0.0.1 --ports 80,443,22
   ```

## 🚨 Important Notes

### Package Name
- Current name: `scanhero`
- If name is taken, you'll need to change it in `pyproject.toml`

### Version Management
- Current version: `1.0.0`
- For updates, increment version in `pyproject.toml` and `src/scanhero/__init__.py`

## 🎉 Quick Upload Command

Once you have your PyPI API token, run:

```bash
source venv/bin/activate
twine upload --username __token__ --password YOUR_ACTUAL_TOKEN_HERE dist/*
```

## 📊 Package Files Ready
- `scanhero-1.0.0-py3-none-any.whl` (19KB)
- `scanhero-1.0.0.tar.gz` (24KB)

Both files are in the `dist/` directory and ready for upload!

## 🆘 Need Help?

If you encounter issues:
1. **403 Forbidden**: Check your API token
2. **Package exists**: Change package name in `pyproject.toml`
3. **Network error**: Check internet connection

## 🚀 Ready to Go!

Your ScanHero package is professionally built and ready for PyPI distribution. Just get your API token and run the upload command!
