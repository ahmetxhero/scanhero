# 🚀 PyPI Upload Guide for ScanHero

## 📋 Prerequisites

Before uploading to PyPI, you need to:

1. **Create a PyPI Account** (if you don't have one)
2. **Set up Authentication**
3. **Upload the Package**

## 🔐 Step 1: Create PyPI Account

1. Go to https://pypi.org/account/register/
2. Create an account with your email
3. Verify your email address
4. **Important**: Choose a unique username (it will be part of your package URL)

## 🔑 Step 2: Authentication Options

### Option A: API Token (Recommended)

1. **Create API Token**:
   - Go to https://pypi.org/manage/account/
   - Scroll down to "API tokens"
   - Click "Add API token"
   - Give it a name (e.g., "ScanHero Upload")
   - Copy the token (starts with `pypi-`)

2. **Upload with Token**:
   ```bash
   source venv/bin/activate
   twine upload --username __token__ --password pypi-your-token-here dist/*
   ```

### Option B: Username/Password

1. **Upload with Credentials**:
   ```bash
   source venv/bin/activate
   twine upload --username your-pypi-username --password your-pypi-password dist/*
   ```

### Option C: Interactive Upload

1. **Interactive Mode** (will prompt for credentials):
   ```bash
   source venv/bin/activate
   twine upload dist/*
   ```

## 🎯 Step 3: Upload Commands

### For Production PyPI:
```bash
# Activate virtual environment
source venv/bin/activate

# Upload to PyPI (production)
twine upload dist/*
```

### For TestPyPI (Recommended First):
```bash
# Upload to TestPyPI first to test
twine upload --repository testpypi dist/*
```

## 🔍 Step 4: Verify Upload

After successful upload:

1. **Check PyPI**: Go to https://pypi.org/project/scanhero/
2. **Test Installation**:
   ```bash
   pip install scanhero
   scanhero --version
   ```

## 🚨 Important Notes

### Package Name Conflict
- If you get a "package already exists" error, you need to:
  1. Change the package name in `pyproject.toml`
  2. Update `src/scanhero/__init__.py` version
  3. Rebuild the package

### Current Package Name
- Current name: `scanhero`
- If this name is taken, consider: `ahmetxhero-scanhero` or `scanhero-ahmetxhero`

## 🛠️ Alternative: TestPyPI First

**Recommended approach** - Upload to TestPyPI first:

```bash
# 1. Create TestPyPI account at https://test.pypi.org/account/register/
# 2. Upload to TestPyPI
source venv/bin/activate
twine upload --repository testpypi dist/*

# 3. Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ scanhero

# 4. If everything works, upload to production PyPI
twine upload dist/*
```

## 📊 Current Package Status

✅ **Package Built**: `scanhero-1.0.0-py3-none-any.whl` (19KB)
✅ **Quality Checked**: Passed twine validation
✅ **Ready for Upload**: All files in `dist/` directory

## 🎉 After Successful Upload

Once uploaded, users can install ScanHero with:

```bash
pip install scanhero
```

And use it immediately:

```bash
# CLI usage
scanhero scan 192.168.1.1 --ports 80,443,22

# Python API
python -c "import scanhero; print('ScanHero installed successfully!')"
```

## 🔧 Troubleshooting

### Common Issues:

1. **403 Forbidden**: Authentication issue - check credentials
2. **Package exists**: Name conflict - change package name
3. **Network error**: Check internet connection
4. **Permission denied**: Make sure you own the package name

### Get Help:
- PyPI Help: https://pypi.org/help/
- Twine Documentation: https://twine.readthedocs.io/

## 🚀 Ready to Upload!

Your ScanHero package is ready for PyPI upload. Choose your preferred authentication method and run the upload command!
