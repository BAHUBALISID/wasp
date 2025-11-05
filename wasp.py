#!/usr/bin/env python3

import requests
import json
import sys
import argparse
import time
import os

class WaspTool:
    def __init__(self):
        self.api_url = "https://dwxxyopsbstmftjbgmpt.supabase.co/functions/v1/fetch-mobile-details"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'WASP/1.0'
        })

    def display_banner(self):
        try:
            with open("banner.txt", "r", encoding="utf-8") as f:
                print(f.read())
        except FileNotFoundError:
            print("WASP - Wireless Asset Search Protocol v2.1.0")

    def show_scan_animation(self, mobile):
        print(f"\n\x1b[38;5;226m[WASP] TARGET ACQUIRED: {mobile}\x1b[0m")
        print("\x1b[38;5;201m" + "─" * 50 + "\x1b[0m")
        
        phases = [
            "INITIATING SECURE HANDshake",
            "ACCESSING CARRIER DATABASES", 
            "QUERYING NETWORK REGISTRY",
            "ANALYZING SUBSCRIBER PATTERNS",
            "COMPILING INTELLIGENCE DATA"
        ]
        
        for i, phase in enumerate(phases, 1):
            for frame in ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']:
                print(f"\x1b[38;5;201m{frame} PHASE {i}/5: {phase}\x1b[0m", end='\r')
                time.sleep(0.1)
            print(f"\x1b[38;5;46m✓ PHASE {i}/5: {phase} - COMPLETE\x1b[0m")
            time.sleep(0.2)
        
        print("\x1b[38;5;46m[WASP] DATA ACQUISITION SUCCESSFUL\x1b[0m")

    def fetch_mobile_details(self, mobile):
        try:
            params = {'mobile': mobile}
            response = self.session.get(self.api_url, params=params, timeout=40)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API RESPONSE: HTTP {response.status_code}"}
                
        except requests.exceptions.Timeout:
            return {"error": "REQUEST TIMEOUT - SERVER RESPONSE DELAYED"}
        except requests.exceptions.ConnectionError:
            return {"error": "CONNECTION FAILURE - NETWORK UNAVAILABLE"}
        except requests.exceptions.RequestException as e:
            return {"error": f"NETWORK ERROR: {str(e)}"}
        except json.JSONDecodeError:
            return {"error": "INVALID RESPONSE FORMAT"}

    def display_results(self, data, mobile):
        print(f"\n\x1b[38;5;81m┌────────────────────────────────────────────────────────┐")
        print(f"│                 TARGET ANALYSIS: {mobile}                │")
        print(f"└────────────────────────────────────────────────────────┘\x1b[0m\n")
        
        if "error" in data:
            print(f"\x1b[38;5;196m[SYSTEM FAILURE] {data['error']}\x1b[0m")
            print(f"\n\x1b[38;5;214m[DIAGNOSTICS]")
            print(f"• VERIFY TARGET NUMBER VALIDITY")
            print(f"• CHECK NETWORK CONNECTIVITY")
            print(f"• SERVER MAY BE TEMPORARILY OFFLINE")
            print(f"• RETRY AFTER 60 SECONDS\x1b[0m")
            return

        if not data:
            print(f"\x1b[38;5;214m[NO DATA] TARGET YIELDED NO RESULTS: {mobile}\x1b[0m")
            return

        print("\x1b[38;5;201m" + "─" * 55 + "\x1b[0m")
        
        field_mapping = {
            'name': 'TARGET IDENTITY',
            'fname': 'FATHERS IDENTITY', 
            'mobile': 'PRIMARY CONTACT',
            'alt': 'SECONDARY CONTACT',
            'id': 'ADHAR ID',
            'address': 'GEOGRAPHIC LOCATION',
            'circle': 'SERVICE ZONE'
        }
        
        for field, display_name in field_mapping.items():
            if field in data and data[field]:
                value = data[field]
                if field == 'address':
                    print(f"\x1b[38;5;201m[{display_name}]\x1b[0m")
                    address_lines = value.split(', ')
                    for line in address_lines:
                        print(f"  \x1b[38;5;46m{line}\x1b[0m")
                else:
                    print(f"\x1b[38;5;201m[{display_name}]\x1b[0m")
                    print(f"  \x1b[38;5;46m{value}\x1b[0m")
                print()

        known_fields = set(field_mapping.keys())
        additional_fields = set(data.keys()) - known_fields
        
        if additional_fields:
            print(f"\x1b[38;5;214m[AUXILIARY DATA]\x1b[0m")
            for field in additional_fields:
                value = data[field]
                if value is not None:
                    field_display = field.upper().replace('_', ' ')
                    print(f"  \x1b[38;5;201m{field_display}:\x1b[0m \x1b[38;5;46m{value}\x1b[0m")
            print()
        
        print("\x1b[38;5;201m" + "─" * 55 + "\x1b[0m")
        print(f"\x1b[38;5;46m[OPERATION COMPLETE] {time.strftime('%H:%M:%S')}\x1b[0m")

    def validate_mobile(self, mobile):
        mobile = mobile.strip()
        if not mobile.isdigit():
            return False, "INVALID CHARACTERS IN TARGET"
        if len(mobile) < 10:
            return False, "INSUFFICIENT TARGET DIGITS"
        if len(mobile) > 15:
            return False, "EXCESSIVE TARGET DIGITS"
        return True, mobile

    def process_mobile(self, mobile):
        is_valid, validation_result = self.validate_mobile(mobile)
        if not is_valid:
            print(f"\x1b[38;5;196m[TARGET REJECTED] {validation_result}\x1b[0m")
            return False
        
        self.show_scan_animation(mobile)
        result = self.fetch_mobile_details(mobile)
        self.display_results(result, mobile)
        return True

    def run(self):
        parser = argparse.ArgumentParser(
            description='WASP - Advanced Mobile Intelligence Tool'
        )
        parser.add_argument('mobile', nargs='?', help='Target mobile number')
        parser.add_argument('-f', '--file', help='File containing target numbers')
        
        args = parser.parse_args()
        
        self.display_banner()
        
        if args.file:
            try:
                with open(args.file, 'r') as f:
                    mobiles = [line.strip() for line in f if line.strip()]
                
                if not mobiles:
                    print(f"\x1b[38;5;196m[NO TARGETS] FILE EMPTY: {args.file}\x1b[0m")
                    return
                
                print(f"\x1b[38;5;214m[BATCH PROCESSING] {len(mobiles)} TARGETS FROM: {args.file}\x1b[0m")
                
                success_count = 0
                for i, mobile in enumerate(mobiles, 1):
                    print(f"\n\x1b[38;5;81m{'═' * 55}\x1b[0m")
                    print(f"\x1b[38;5;214m[TARGET {i}/{len(mobiles)}] {mobile}\x1b[0m")
                    
                    if self.process_mobile(mobile):
                        success_count += 1
                    
                    if i < len(mobiles):
                        time.sleep(2)
                
                print(f"\n\x1b[38;5;46m[BATCH COMPLETE] {success_count}/{len(mobiles)} SUCCESSFUL\x11b[0m")
                        
            except FileNotFoundError:
                print(f"\x1b[38;5;196m[FILE ERROR] NOT FOUND: {args.file}\x1b[0m")
                sys.exit(1)
            except Exception as e:
                print(f"\x1b[38;5;196m[FILE ERROR] {str(e)}\x1b[0m")
                sys.exit(1)
                
        elif args.mobile:
            self.process_mobile(args.mobile)
            
        else:
            try:
                while True:
                    mobile = input("\n\x1b[38;5;226m[WASP] ENTER TARGET NUMBER (QUIT TO EXIT): \x1b[0m").strip()
                    
                    if mobile.lower() in ['quit', 'exit', 'q']:
                        break
                    
                    if mobile:
                        self.process_mobile(mobile)
                    else:
                        print("\x1b[38;5;214m[INPUT REQUIRED] ENTER VALID TARGET\x1b[0m")
                        
            except KeyboardInterrupt:
                print(f"\n\x1b[38;5;196m[SESSION TERMINATED]\x1b[0m")

def main():
    try:
        tool = WaspTool()
        tool.run()
    except KeyboardInterrupt:
        print(f"\n\x1b[38;5;196m[OPERATION ABORTED]\x1b[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\x1b[38;5;196m[SYSTEM FAILURE] {str(e)}\x1b[0m")
        sys.exit(1)

if __name__ == "__main__":
    main()
