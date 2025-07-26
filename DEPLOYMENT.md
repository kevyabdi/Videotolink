# Deployment Guide

This guide explains how to deploy your Telegram File Saver Bot on various platforms.

## GitHub Repository Setup

### 1. Prepare Your Files
- Use `main.py` as your main file
- Set your admin user ID in environment variables
- Never commit your actual credentials

### 2. Upload to GitHub
```bash
# Initialize git repository
git init

# Add files
git add .

# Commit
git commit -m "Initial commit - Telegram File Saver Bot v2.0"

# Add remote repository
git remote add origin https://github.com/yourusername/telegram-file-saver-bot.git

# Push to GitHub
git push -u origin main
