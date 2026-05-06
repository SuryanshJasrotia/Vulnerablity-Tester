#!/usr/bin/env python3

import argparse
import logging
import sys
import time
import json
import os
import smtplib
import socket
import threading
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from email.mime.text import MIMEText
from email.header import Header
import requests
import random
import string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('identityforge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IdentityForge:
    def __init__(self, mode: str, target: str = None, spoof_email: str = None, smtp_server: str = None,
                 smtp_port: int = 587, smtp_user: str = None, smtp_pass: str = None,
                 phone_number: str = None, voip_server: str = None, profile_url: str = None,
                 threads: int = 5, quiet: bool = False):
        self.mode = mode
        self.target = target
        self.spoof_email = spoof_email
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass
        self.phone_number = phone_number
        self.voip_server = voip_server
        self.profile_url = profile_url
        self.threads = threads
        self.quiet = quiet
        self.output_dir = 'identityforge-output'
        self.output_file = os.path.join(self.output_dir, 
            f"forge_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        self.json_file = os.path.join(self.output_dir, 
            f"forge_{time.strftime('%Y%m%d_%H%M%S')}.json")
        self.db_file = os.path.join(self.output_dir, 'identityforge.db')
        os.makedirs(self.output_dir, exist_ok=True)
        self.actions = []
        self.running = True
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('identityforge.log')]

    def init_db(self):
        """Initialize SQLite database for storing action logs."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mode TEXT,
                    target TEXT,
                    spoof_email TEXT,
                    phone_number TEXT,
                    profile_url TEXT,
                    status TEXT,
                    timestamp TEXT
                )
            ''')
            conn.commit()

    def store_action(self, status: str):
        """Store action details in database."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO actions (mode, target, spoof_email, phone_number, profile_url, status, timestamp) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (self.mode, self.target, self.spoof_email, self.phone_number, self.profile_url, status, timestamp)
            )
            conn.commit()
        self.actions.append({
            'mode': self.mode,
            'target': self.target,
            'spoof_email': self.spoof_email,
            'phone_number': self.phone_number,
            'profile_url': self.profile_url,
            'status': status,
            'timestamp': timestamp
        })

    def email_spoof(self):
        """Simulate email spoofing by sending a forged email."""
        logger.info(f"Starting email spoof to {self.target} from {self.spoof_email}")
        try:
            msg = MIMEText("This is a test email from IdentityForge for security testing.")
            msg['Subject'] = Header("Test Email - Security Simulation")
            msg['From'] = self.spoof_email
            msg['To'] = self.target

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_pass:
                    server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.spoof_email, self.target, msg.as_string())
            
            status = f"Email sent to {self.target} from {self.spoof_email}"
            logger.info(status)
            self.store_action(status)
        except Exception as e:
            status = f"Email spoof failed: {e}"
            logger.error(status)
            self.store_action(status)

    def phone_spoof(self):
        """Simulate caller ID spoofing via VoIP (placeholder for VoIP integration)."""
        logger.info(f"Starting phone spoof to {self.target} from {self.phone_number}")
        try:
            # Placeholder: Simulate VoIP call (requires external VoIP service like Asterisk)
            status = f"Simulated VoIP call to {self.target} from {self.phone_number} via {self.voip_server}"
            logger.info(status)
            self.store_action(status)
        except Exception as e:
            status = f"Phone spoof failed: {e}"
            logger.error(status)
            self.store_action(status)

    def profile_clone(self):
        """Simulate social media profile cloning."""
        logger.info(f"Starting profile cloning from {self.profile_url}")
        try:
            # Fetch profile data (simplified; real-world requires scraping)
            response = requests.get(self.profile_url, timeout=5)
            if response.status_code == 200:
                fake_username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
                status = f"Cloned profile from {self.profile_url} as fake user {fake_username}"
                logger.info(status)
                self.store_action(status)
            else:
                status = f"Profile clone failed: HTTP {response.status_code}"
                logger.error(status)
                self.store_action(status)
        except Exception as e:
            status = f"Profile clone failed: {e}"
            logger.error(status)
            self.store_action(status)

    def run(self):
        """Run IdentityForge in specified mode."""
        logger.info("Starting IdentityForge")
        try:
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                if self.mode == 'email':
                    if not all([self.target, self.spoof_email, self.smtp_server]):
                        logger.error("Email mode requires target, spoof_email, and smtp_server")
                        sys.exit(1)
                    executor.submit(self.email_spoof)
                elif self.mode == 'phone':
                    if not all([self.target, self.phone_number, self.voip_server]):
                        logger.error("Phone mode requires target, phone_number, and voip_server")
                        sys.exit(1)
                    executor.submit(self.phone_spoof)
                elif self.mode == 'profile':
                    if not self.profile_url:
                        logger.error("Profile mode requires profile_url")
                        sys.exit(1)
                    executor.submit(self.profile_clone)
                else:
                    logger.error("Invalid mode. Use 'email', 'phone', or 'profile'")
                    sys.exit(1)
                
                # Keep running until actions complete or interrupted
                while self.running:
                    time.sleep(1)
        except KeyboardInterrupt:
            logger.info("IdentityForge stopped by user")
            self.running = False
        finally:
            self.save_results()

    def save_results(self):
        """Save action logs to files."""
        with open(self.output_file, 'a') as f:
            f.write("=== IdentityForge Results ===\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            for action in self.actions:
                f.write(f"[{action['timestamp']}] {action['mode']}: {action['status']}, "
                        f"Target={action['target']}, Spoof Email={action['spoof_email']}, "
                        f"Phone={action['phone_number']}, Profile={action['profile_url']}\n")
        
        with open(self.json_file, 'w') as f:
            json.dump({
                'mode': self.mode,
                'target': self.target,
                'spoof_email': self.spoof_email,
                'phone_number': self.phone_number,
                'profile_url': self.profile_url,
                'actions': self.actions,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=4)
        
        logger.info(f"Results saved to {self.output_file} and {self.json_file}")

def main():
    parser = argparse.ArgumentParser(
        description="IdentityForge: Identity manipulation simulator for security testing.",
        epilog="Example: ./identityforge.py -m email -t target@example.com -e spoof@example.com -s smtp.gmail.com -u user -p pass"
    )
    parser.add_argument('-m', '--mode', required=True, choices=['email', 'phone', 'profile'],
                       help="Mode: email, phone, or profile")
    parser.add_argument('-t', '--target', help="Target email or phone number")
    parser.add_argument('-e', '--spoof-email', help="Spoofed email address (email mode)")
    parser.add_argument('-s', '--smtp-server', help="SMTP server (email mode)")
    parser.add_argument('--smtp-port', type=int, default=587, help="SMTP port (default: 587)")
    parser.add_argument('-u', '--smtp-user', help="SMTP username (email mode)")
    parser.add_argument('-p', '--smtp-pass', help="SMTP password (email mode)")
    parser.add_argument('--phone-number', help="Spoofed phone number (phone mode)")
    parser.add_argument('--voip-server', help="VoIP server (phone mode)")
    parser.add_argument('--profile-url', help="Social media profile URL (profile mode)")
    parser.add_argument('-T', '--threads', type=int, default=5,
                       help="Number of threads (default: 5)")
    parser.add_argument('-q', '--quiet', action='store_true',
                       help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
         IdentityForge v1.0
      Identity Manipulation Tool
    ==============================
    """)

    try:
        forge = IdentityForge(
            mode=args.mode,
            target=args.target,
            spoof_email=args.spoof_email,
            smtp_server=args.smtp_server,
            smtp_port=args.smtp_port,
            smtp_user=args.smtp_user,
            smtp_pass=args.smtp_pass,
            phone_number=args.phone_number,
            voip_server=args.voip_server,
            profile_url=args.profile_url,
            threads=args.threads,
            quiet=args.quiet
        )
        forge.run()
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()