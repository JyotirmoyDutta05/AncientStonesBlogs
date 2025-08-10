@echo off
echo ========================================
echo    Vercel Deployment Helper
echo ========================================
echo.
echo Choose an option:
echo 1. Deploy to Vercel (development)
echo 2. Deploy to Vercel (production)
echo 3. Install Vercel CLI
echo 4. Login to Vercel
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Deploying to Vercel (development)...
    vercel
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Deploying to Vercel (production)...
    vercel --prod
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Installing Vercel CLI...
    npm i -g vercel
    goto end
)

if "%choice%"=="4" (
    echo.
    echo Logging in to Vercel...
    vercel login
    goto end
)

if "%choice%"=="5" (
    echo.
    echo Exiting...
    goto end
)

echo.
echo Invalid choice. Please try again.
echo.

:end
echo.
echo Press any key to continue...
pause >nul
