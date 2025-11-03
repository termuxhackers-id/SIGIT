<div align="left" style="position: relative;">
  <h1>SIGIT</h1>
  <p align="left">
    <em><code>Simple Information Gathering Toolkit - Modular OSINT CLI</code></em>
  </p>
  <p align="left">
    <img src="https://img.shields.io/github/license/termuxhackers-id/SIGIT?style=default&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
    <img src="https://img.shields.io/github/last-commit/termuxhackers-id/SIGIT?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
    <img src="https://img.shields.io/github/languages/top/termuxhackers-id/SIGIT?style=default&color=0080ff" alt="repo-top-language">
    <img src="https://img.shields.io/github/languages/count/termuxhackers-id/SIGIT?style=default&color=0080ff" alt="repo-language-count">
    <img src="https://img.shields.io/pypi/v/sigit?style=default&logo=pypi&logoColor=white&color=0080ff" alt="PyPI">
    <img src="https://img.shields.io/badge/Python-3.12%2B-blue?style=default&logo=python&logoColor=white&color=0080ff" alt="Python">
  </p>
  <p align="left">
    <img src="https://img.shields.io/badge/asyncio-aiohttp-green?style=default&logo=python&logoColor=white&color=0080ff" alt="Tech Stack">
    <img src="https://img.shields.io/badge/14%20Tools-OSINT-orange?style=default&logo=tools&logoColor=white&color=0080ff" alt="Tools Count">
  </p>
</div>
<br clear="right">

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
  - [Project Index](#project-index)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Testing](#testing)
- [Project Roadmap](#project-roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

<code>Modular OSINT CLI for Reconnaissance, Security Testing, and Digital Forensics</code>

**SIGIT** is a **Simple Information Gathering Toolkit** — a modern Python CLI tool designed to **collect public information (OSINT)** quickly, efficiently, and in a modular way.

**Built with:**
- `asyncio` + `aiohttp` → **Async & Non-blocking**
- `ThreadPoolExecutor` → **Parallel Scanning**
- **Modular Design** → Services separated from CLI (Reusable)
- **Zero Resource Leak** → `AsyncClient` auto-closes sessions

---

## Features

<code>14 Powerful OSINT Tools in One CLI</code>

<table>
  <tr>
    <th>No</th>
    <th>Tool</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>01</td>
    <td><strong>UserRecon</strong></td>
    <td>Check username across 19 platforms (GitHub, Twitter, Instagram, etc)</td>
  </tr>
  <tr>
    <td>02</td>
    <td><strong>PhoneInfo</strong></td>
    <td>Phone number → Country, Carrier, Type</td>
  </tr>
  <tr>
    <td>03</td>
    <td><strong>MailFinder</strong></td>
    <td>Generate & validate emails from full name</td>
  </tr>
  <tr>
    <td>04</td>
    <td><strong>IPLocation</strong></td>
    <td>IP → Location, ISP, GPS Coordinates</td>
  </tr>
  <tr>
    <td>05</td>
    <td><strong>SubdomainScan</strong></td>
    <td>Enumerate common subdomains (www, api, admin, etc)</td>
  </tr>
  <tr>
    <td>06</td>
    <td><strong>PortScanner</strong></td>
    <td>Scan 17 common ports (SSH, HTTP, MySQL, etc)</td>
  </tr>
  <tr>
    <td>07</td>
    <td><strong>DNSRecon</strong></td>
    <td>A, MX, NS, TXT records via Google DNS</td>
  </tr>
  <tr>
    <td>08</td>
    <td><strong>WHOISLookup</strong></td>
    <td>Full domain registration info</td>
  </tr>
  <tr>
    <td>09</td>
    <td><strong>SSLChecker</strong></td>
    <td>SSL/TLS certificate analysis (expiry, issuer)</td>
  </tr>
  <tr>
    <td>10</td>
    <td><strong>HeaderAnalyzer</strong></td>
    <td>Security headers score (HSTS, CSP, XFO, etc)</td>
  </tr>
  <tr>
    <td>11</td>
    <td><strong>GitHubRecon</strong></td>
    <td>User info + 5 latest repos</td>
  </tr>
  <tr>
    <td>12</td>
    <td><strong>BreachChecker</strong></td>
    <td>Check email in data breaches</td>
  </tr>
  <tr>
    <td>13</td>
    <td><strong>TechDetector</strong></td>
    <td>Detect CMS, Framework, CDN, Analytics</td>
  </tr>
  <tr>
    <td>14</td>
    <td><strong>ReverseIP</strong></td>
    <td>Other domains on the same IP</td>
  </tr>
</table>

**Additional Features:**
- Auto-save results to `.txt`
- Colorful CLI with ASCII logo
- Cross-platform (Linux, macOS, Windows/WSL)
- Production-ready (Type hints, Tests, Linting)

---

## Project Structure

<pre style="font-family: 'JetBrains Mono', monospace; background: #161b22; color: #c9d1d9; padding: 1rem; border-radius: 8px; overflow-x: auto;">
└── sigit/
    ├── pyproject.toml     → Build config & dependencies
    ├── README.md          → Documentation
    ├── run.py             → Entry point
    ├── sigit/             → Source code
    │   ├── __init__.py
    │   ├── core/          → AsyncClient, Config, Colors
    │   │   ├── client.py
    │   │   ├── config.py
    │   │   └── colors.py
    │   ├── services/      → 14 OSINT modules (Modular!)
    │   │   ├── __init__.py
    │   │   ├── user_recon.py
    │   │   ├── ip_location.py
    │   │   ├── phone_info.py
    │   │   ├── mail_finder.py
    │   │   ├── subdomain_scanner.py
    │   │   ├── port_scanner.py
    │   │   ├── dns_recon.py
    │   │   ├── whois.py
    │   │   ├── ssl_checker.py
    │   │   ├── header_analyzer.py
    │   │   ├── github_recon.py
    │   │   ├── breach_checker.py
    │   │   ├── tech_detector.py
    │   │   └── reverse_ip.py
    │   └── cli/           → Interactive menu
    │       ├── __init__.py
    │       ├── menu.py
    │       └── display.py
    ├── tests/             → Unit tests
    └── LICENSE            → MIT License
</pre>

### Project Index
<details open>
  <summary><b><code>sigit/</code></b></summary>
  <details>
    <summary><b>core/</b></summary>
    <blockquote>
      <table>
        <tr>
          <td><b><a href="sigit/core/client.py">client.py</a></b></td>
          <td><code>Async HTTP Client (Zero Leak)</code></td>
        </tr>
        <tr>
          <td><b><a href="sigit/core/config.py">config.py</a></b></td>
          <td><code>Configuration & Constants</code></td>
        </tr>
        <tr>
          <td><b><a href="sigit/core/colors.py">colors.py</a></b></td>
          <td><code>Terminal Colors</code></td>
        </tr>
      </table>
    </blockquote>
  </details>
  <details>
    <summary><b>services/</b> (14 Modules)</summary>
    <blockquote>
      <table>
        <tr>
          <td><b><a href="sigit/services/user_recon.py">user_recon.py</a></b></td>
          <td><code>19 Social Media Checker</code></td>
        </tr>
        <tr>
          <td><b><a href="sigit/services/port_scanner.py">port_scanner.py</a></b></td>
          <td><code>17 Common Ports</code></td>
        </tr>
        <tr>
          <td><b><a href="sigit/services/mail_finder.py">mail_finder.py</a></b></td>
          <td><code>Email Generator + Validator</code></td>
        </tr>
      </table>
    </blockquote>
  </details>
  <details>
    <summary><b>cli/</b></summary>
    <blockquote>
      <table>
        <tr>
          <td><b><a href="sigit/cli/menu.py">menu.py</a></b></td>
          <td><code>Interactive Menu Handler</code></td>
        </tr>
        <tr>
          <td><b><a href="sigit/cli/display.py">display.py</a></b></td>
          <td><code>Colored Output & Logo</code></td>
        </tr>
      </table>
    </blockquote>
  </details>
</details>

---

## Getting Started

### Prerequisites

- **Python:** 3.12+
- **Internet:** Required for OSINT APIs

### Installation

**From PyPI (Recommended):**
<pre style="background: #161b22; color: #c9d1d9; padding: 1rem; border-radius: 8px;">
pip install sigit
</pre>

**From Source:**
<pre style="background: #161b22; color: #c9d1d9; padding: 1rem; border-radius: 8px;">
git clone https://github.com/termuxhackers-id/SIGIT
cd SIGIT
pip install -e .
</pre>

### Usage

<pre style="background: #161b22; color: #c9d1d9; padding: 1rem; border-radius: 8px;">
sigit
</pre>

**Example Output:**
<pre style="background: #161b22; color: #c9d1d9; padding: 1rem; border-radius: 8px;">
> choose: 1
> enter username: john
[200] https://github.com/john
[404] https://twitter.com/john
> Found 5 results
</pre>

### Testing

<pre style="background: #161b22; color: #c9d1d9; padding: 1rem; border-radius: 8px;">
pytest
</pre>

---

## Project Roadmap

- Done **Modular Services** (14 Tools Complete)
- Done **AsyncClient** (Zero Resource Leak)
- Done **Interactive CLI** (Colors + Auto-save)
- Done **PyPI Ready** (pyproject.toml)
- To Do **Web API** (FastAPI endpoints)
- To Do **Telegram Bot** Integration
- To Do **Docker Support**
- To Do **GUI Version** (CustomTkinter)

---

## Contributing

- Discussions [Join the Discussions](https://github.com/termuxhackers-id/SIGIT/discussions)
- Issues [Report Issues](https://github.com/termuxhackers-id/SIGIT/issues)
- Pull Requests [Submit Pull Requests](https://github.com/termuxhackers-id/SIGIT/blob/main/CONTRIBUTING.md)

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**
2. **Clone Locally**  
   <pre style="background: #161b22; color: #c9d1d9; padding: 1rem; border-radius: 8px;">
   git clone https://github.com/termuxhackers-id/SIGIT
   </pre>
3. **Create a New Branch**  
   <pre style="background: #161b22; color: #c9d1d9; padding: 1rem; border-radius: 8px;">
   git checkout -b feature/add-new-service
   </pre>
4. **Make Your Changes**
5. **Commit**  
   <pre style="background: #161b22; color: #c9d1d9; padding: 1rem; border-radius: 8px;">
   git commit -m 'feat: add shodan integration'
   </pre>
6. **Push**  
   <pre style="background: #161b22; color: #c9d1d9; padding: 1rem; border-radius: 8px;">
   git push origin feature/add-new-service
   </pre>
7. **Submit a Pull Request**
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="center">
   <a href="https://github.com/termuxhackers-id/SIGIT/graphs/contributors">
      <img src="https://contrib.rocks/image?repo=termuxhackers-id/SIGIT">
   </a>
</p>
</details>

---

## License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/). See the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Made with love by <a href="https://github.com/termuxhackers-id">TermuxHackers.id</a></sub><br>
  <sub><i>Simple. Modular. Powerful.</i></sub>
</div>
