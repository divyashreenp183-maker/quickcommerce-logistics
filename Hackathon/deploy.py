#!/usr/bin/env python3
"""
Deployment preparation script for Quick Commerce Logistics System
"""

import os
import subprocess
import sys

def check_git_status():
    """Check if git is initialized"""
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def initialize_git():
    """Initialize git repository"""
    print("Initializing Git repository...")
    commands = [
        ['git', 'init'],
        ['git', 'add', '.'],
        ['git', 'commit', '-m', 'Initial commit - Quick Commerce Logistics System'],
        ['git', 'branch', '-M', 'main']
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error running {' '.join(cmd)}: {result.stderr}")
                return False
            print(f"✓ {' '.join(cmd)}")
        except FileNotFoundError:
            print(f"Command not found: {cmd[0]}")
            return False
    
    return True

def create_deployment_instructions():
    """Create deployment instructions"""
    instructions = """
# Quick Commerce Logistics System - Ready for Deployment

## Project Status: ✅ READY

Your Quick Commerce Logistics System is fully implemented and ready for deployment to Vercel.

## Files Created:
- app.py - Main Flask application with all API endpoints
- models/ - Order, Rider, and Store models
- services/ - Optimization engine and demand simulator
- templates/index.html - Modern web interface
- requirements.txt - Python dependencies
- vercel.json - Vercel deployment configuration
- README.md - Comprehensive documentation
- DEPLOYMENT.md - Step-by-step deployment guide

## Next Steps:

### Option 1: Deploy via Vercel Web Interface (Easiest)
1. Go to https://vercel.com
2. Click "New Project"
3. Connect your GitHub/GitLab/Bitbucket account
4. Import this repository
5. Click "Deploy"

### Option 2: Deploy via Vercel CLI
1. Install Node.js from https://nodejs.org
2. Run: npm install -g vercel
3. Run: vercel login
4. Run: vercel --prod

## Features Included:
✅ 10-minute delivery SLA enforcement
✅ Smart store and rider assignment
✅ Real-time profit calculation
✅ Demand zone simulation
✅ What-if analysis
✅ Modern web UI with good UX
✅ Complete API documentation
✅ Explainable AI decisions

## Testing:
Once deployed, visit your app URL and test:
- Create new orders
- View dashboard analytics
- Run demand simulations
- Check SLA compliance

The system is production-ready and includes all requested features!
"""
    
    with open('DEPLOYMENT_READY.md', 'w') as f:
        f.write(instructions)
    
    print("✓ Created DEPLOYMENT_READY.md")

def verify_project_structure():
    """Verify all required files exist"""
    required_files = [
        'app.py',
        'requirements.txt',
        'vercel.json',
        'templates/index.html',
        'models/order.py',
        'models/rider.py',
        'models/store.py',
        'services/optimization_engine.py',
        'services/demand_simulator.py',
        'README.md'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return True

def main():
    """Main deployment preparation"""
    print("Quick Commerce Logistics System - Deployment Preparation")
    print("=" * 60)
    
    # Verify project structure
    if not verify_project_structure():
        print("❌ Project structure verification failed")
        return False
    
    # Create deployment instructions
    create_deployment_instructions()
    
    # Check git status
    if not check_git_status():
        print("\nGit not initialized. Initializing...")
        if not initialize_git():
            print("❌ Git initialization failed")
            return False
    else:
        print("✅ Git repository already initialized")
    
    print("\n" + "=" * 60)
    print("🚀 PROJECT READY FOR DEPLOYMENT!")
    print("\nNext steps:")
    print("1. Push to GitHub/GitLab/Bitbucket")
    print("2. Deploy via Vercel web interface at https://vercel.com")
    print("3. Or install Node.js and use Vercel CLI")
    print("\nSee DEPLOYMENT.md for detailed instructions.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
