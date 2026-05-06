# IdentityForge

## Description
IdentityForge is a Python-based identity manipulation simulator inspired by impersonation techniques, designed for ethical security testing in your private lab (Ubuntu 24.04, home network). It simulates email spoofing, caller ID spoofing (via VoIP placeholder), and social media profile cloning to test defenses against phishing, social engineering, and identity theft. Built with a CLI interface, SQLite logging, JSON output, and multi-threading, it integrates with your tools like **NetSentry**, **NatPiercer**, and **WiFiCrush**.

**Important**: Use IdentityForge only on networks and systems you own or have explicit permission to test. Unauthorized impersonation, spoofing, or profile manipulation is illegal and may lead to legal consequences, network disruptions, or ethical issues. This tool is restricted to your lab for responsible use. Modern email filters and VoIP systems may block spoofing attempts (,).[](https://perception-point.io/guides/phishing/5-types-of-impersonation-attacks-and-6-ways-to-prevent-them/)[](https://www.tookitaki.com/glossary/impersonation)

## Features
- **Email Spoofing**: Sends forged emails to simulate phishing attacks.
- **Caller ID Spoofing**: Simulates VoIP-based phone number spoofing (placeholder).
- **Profile Cloning**: Clones social media profiles for testing (simplified).
- **Output Formats**: SQLite database, JSON, and text logs.
- **Multi-Threading**: Efficient action processing.
- **Quiet Mode**: Minimizes terminal output.
- **Logging**: Saves logs to `identityforge.log` and results to `identityforge-output/`.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Network access for email and HTTP requests.
   - Root privileges (`sudo`) for socket operations.
   - Private network/lab you control.
2. **Install Dependencies**:
   - Save `setup_identityforge.sh` to a directory (e.g., `/home/user/identityforge/`).
   - Make executable and run:
     ```bash
     chmod +x setup_identityforge.sh
     ./setup_identityforge.sh
     ```
   - Installs Python, pip, and `requests`.
3. Save `identityforge.py` to the same directory.
4. Verify:
   ```bash
   python3 identityforge.py --help
   ```

## Usage
IdentityForge simulates identity manipulation techniques in a controlled lab setting to test security defenses. Below are examples and expected outcomes.

### Basic Commands
Simulate email spoofing:
```bash
sudo python3 identityforge.py -m email -t target@example.com -e spoof@example.com -s smtp.gmail.com -u user@gmail.com -p app_password
```

Simulate phone spoofing (placeholder):
```bash
sudo python3 identityforge.py -m phone -t +1234567890 --phone-number +0987654321 --voip-server sip.example.com
```

Simulate profile cloning:
```bash
sudo python3 identityforge.py -m profile --profile-url https://example.com/profile
```

Run in quiet mode:
```bash
sudo python3 identityforge.py -m email -t target@example.com -e spoof@example.com -s smtp.gmail.com -u user@gmail.com -p app_password -q
```

### Options
- `-m, --mode`: Mode (email, phone, or profile, required).
- `-t, --target`: Target email or phone number.
- `-e, --spoof-email`: Spoofed email address (email mode).
- `-s, --smtp-server`: SMTP server (email mode).
- `--smtp-port`: SMTP port (default: 587).
- `-u, --smtp-user`: SMTP username (email mode).
- `-p, --smtp-pass`: SMTP password (email mode).
- `--phone-number`: Spoofed phone number (phone mode).
- `--voip-server`: VoIP server (phone mode).
- `--profile-url`: Social media profile URL (profile mode).
- `-T, --threads`: Number of threads (default: 5).
- `-q, --quiet`: Log to file only.

### Features

#### Email Spoofing
- **Purpose**: Simulate phishing by sending forged emails.
- **Usage**:
  ```bash
  sudo python3 identityforge.py -m email -t target@example.com -e spoof@example.com -s smtp.gmail.com -u user@gmail.com -p app_password
  ```
- **Output**:
  ```
  2025-05-15 16:00:00 - INFO - Starting IdentityForge
  2025-05-15 16:00:02 - INFO - Email sent to target@example.com from spoof@example.com
  ```
- **Result File** (`identityforge-output/forge_20250515_160000.txt`):
  ```
  === IdentityForge Results ===
  Timestamp: 2025-05-15 16:00:02
  [2025-05-15 16:00:02] email: Email sent to target@example.com from spoof@example.com, Target=target@example.com, Spoof Email=spoof@example.com, Phone=None, Profile=None
  ```
- **JSON File** (`identityforge-output/forge_20250515_160000.json`):
  ```json
  {
    "mode": "email",
    "target": "target@example.com",
    "spoof_email": "spoof@example.com",
    "phone_number": null,
    "profile_url": null,
    "actions": [
      {
        "mode": "email",
        "target": "target@example.com",
        "spoof_email": "spoof@example.com",
        "phone_number": null,
        "profile_url": null,
        "status": "Email sent to target@example.com from spoof@example.com",
        "timestamp": "2025-05-15 16:00:02"
      }
    ],
    "timestamp": "2025-05-15 16:00:02"
  }
  ```
- **Tips**: Use **NetSentry** to monitor email traffic; test with disposable email services.

#### Phone Spoofing
- **Purpose**: Simulate caller ID spoofing (placeholder for VoIP integration).
- **Usage**:
  ```bash
  sudo python3 identityforge.py -m phone -t +1234567890 --phone-number +0987654321 --voip-server sip.example.com
  ```
- **Output**:
  ```
  2025-05-15 16:00:03 - INFO - Simulated VoIP call to +1234567890 from +0987654321 via sip.example.com
  ```
- **Tips**: Integrate with Asterisk for real VoIP spoofing; test in isolated VoIP lab.

#### Profile Cloning
- **Purpose**: Simulate social media profile cloning for testing.
- **Usage**:
  ```bash
  sudo python3 identityforge.py -m profile --profile-url https://example.com/profile
  ```
- **Output**:
  ```
  2025-05-15 16:00:04 - INFO - Cloned profile from https://example.com/profile as fake user abc123xyz
  ```
- **Tips**: Use **WiFiCrush** to access target network; verify with browser inspection.

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  sudo python3 identityforge.py -m email -t target@example.com -e spoof@example.com -s smtp.gmail.com -u user@gmail.com -p app_password -q
  ```
- **Tips**: Monitor `identityforge.log` with `tail -f identityforge.log`.

### Workflow
1. Set up lab (VM with network access).
2. Install dependencies:
   ```bash
   ./setup_identityforge.sh
   ```
3. Run IdentityForge:
   ```bash
   sudo python3 identityforge.py -m email -t target@example.com -e spoof@example.com -s smtp.gmail.com -u user@gmail.com -p app_password
   ```
4. Monitor output in terminal or `identityforge.log`.
5. Check results in `identityforge-output/` (text, JSON, SQLite).
6. Stop with `Ctrl+C`; secure outputs (`rm -rf identityforge-output/*`).

## Output
- **Logs**: `identityforge.log`, e.g.:
  ```
  2025-05-15 16:00:00 - INFO - Starting IdentityForge
  2025-05-15 16:00:02 - INFO - Email sent to target@example.com from spoof@example.com
  ```
- **Results**: `identityforge-output/forge_<timestamp>.txt` and `.json`.
- **Database**: `identityforge-output/identityforge.db` (SQLite).

## Notes
- **Environment**: Use on authorized networks/systems in your lab.
- **Impact**: Spoofing may be blocked by modern email filters or VoIP systems ().[](https://perception-point.io/guides/phishing/5-types-of-impersonation-attacks-and-6-ways-to-prevent-them/)
- **Ethics**: Avoid unauthorized impersonation to prevent legal/security issues ().[](https://www.tookitaki.com/glossary/impersonation)
- **Dependencies**: Requires `requests` for profile cloning; email mode needs SMTP access.
- **Root**: Requires `sudo` for socket operations.
- **Sources**: Inspired by impersonation attack techniques (,) and Kali Linux tools.[](https://perception-point.io/guides/phishing/5-types-of-impersonation-attacks-and-6-ways-to-prevent-them/)[](https://www.tookitaki.com/glossary/impersonation)

## Disclaimer
**Personal Use Only**: IdentityForge is for learning on networks/systems you own or have permission to test. Unauthorized impersonation or spoofing is illegal and may lead to legal consequences or ethical issues (). Ensure compliance with local laws.[](https://www.bitdefender.com/en-gb/blog/hotforsecurity/what-is-impersonation)

**Safe Use**:
- Use in a private lab (e.g., VM with isolated network).
- Secure outputs (`identityforge.log`, `identityforge-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Public/corporate networks without permission.
- Sharing sensitive output files.
- Production environments to prevent disruptions.

## Limitations
- **Email Spoofing**: May fail with SPF/DKIM/DMARC checks ().[](https://learn.microsoft.com/en-us/defender-office-365/anti-phishing-mdo-impersonation-insight)
- **Phone Spoofing**: Placeholder; requires external VoIP service (e.g., Asterisk).
- **Profile Cloning**: Simplified; real-world cloning needs advanced scraping ().[](https://www.bitdefender.com/en-us/cyberpedia/what-is-social-media-impersonation)
- **Interface**: CLI-only; lacks GUI or TUI.
- **Scope**: Focuses on simulation; lacks deepfake or biometric spoofing ().[](https://en.wikipedia.org/wiki/Identity_replacement_technology)

## Tips
- Test email spoofing with disposable email services to avoid spam filters.
- Use Wireshark or **NetSentry** to monitor spoofed traffic.
- Combine with **WiFiCrush** for network access or **NatPiercer** for tunneling.
- Verify VoIP setup with Asterisk or FreePBX for phone spoofing.
- Report impersonation attempts to authorities ().[](https://www.cifas.org.uk/services/identity-protection/victim-of-impersonation)

## License
For personal educational use; no formal license. Use responsibly.