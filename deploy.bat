@echo off
echo ============================================
echo   Diwali E-Pass - GitHub Deployment Setup
echo ============================================
echo.

echo Step 1: Initializing Git repository...
git init
echo ✓ Git initialized
echo.

echo Step 2: Adding all files...
git add .
echo ✓ Files staged
echo.

echo Step 3: Creating first commit...
git commit -m "Initial commit - Diwali E-Pass System"
echo ✓ First commit created
echo.

echo ============================================
echo   Next Steps:
echo ============================================
echo.
echo 1. Go to: https://github.com/new
echo 2. Create a repository named: diwali-epass
echo 3. Copy the repository URL
echo 4. Run these commands:
echo.
echo    git remote add origin YOUR_REPO_URL
echo    git branch -M main
echo    git push -u origin main
echo.
echo 5. Then go to Render.com and deploy!
echo.
echo Full guide: Read RENDER_DEPLOYMENT_GUIDE.md
echo ============================================
pause
