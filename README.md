# RBX404-telegram-digital-marketplace
# Telegram Digital Marketplace Bot

A production-ready Telegram bot for selling digital products with internal coin economy, referral system, and Telegram Stars payment integration.

## Features

- 🛍️ **Product Store** - Categories, search, details, preview
- 🪙 **Coin System** - Internal economy with daily check-in, missions
- ⭐ **Telegram Stars** - Native payment integration
- 👤 **User System** - Profiles, library, purchase history
- 👑 **Admin Panel** - Complete management dashboard
- 🤝 **Referral System** - Track referrals with anti-fake protection
- 💬 **Support Tickets** - Built-in customer support
- 🔒 **Secure Storage** - Private Telegram channel for product storage
- 🌐 **Multi-language** - Bengali & English (extensible)

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (optional, SQLite for development)
- Telegram Bot Token from @BotFather
- Private Telegram Channel for product storage

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/telegram-digital-marketplace.git
cd telegram-digital-marketplace
```

2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Configure environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize database

```bash
python -m bot.migrations.init
```

6. Run the bot

```bash
python -m bot.main
```

Docker Deployment

```bash
docker-compose up -d
```

Documentation

· Installation Guide
· Admin Guide
· API Reference
· Deployment Guide

License

MIT License - see LICENSE for details

```

---

### 2. Configuration Module

#### **`bot/config/__init__.py`**
```python
"""Configuration module for the bot."""

from .settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
```
