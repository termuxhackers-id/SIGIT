import socket
import os

from ..services import *
from .display import (
    clear, LOGO, separator, print_user_result, save_results,
    print_header, print_found, input_prompt
)
from ..core.colors import Colors
from ..core.config import config

c = Colors()


class Menu:
    @staticmethod
    def show():
        clear()
        print(LOGO)
        print(f"""
         {c.BG_WHITE}\033[2;30m Choose number or type exit for exiting {c.RESET}
    
        {c.BLUE}  01{c.RESET} Userrecon       {c.DIM}Username reconnaissance 
        {c.BLUE}  02{c.RESET} PhoneInfo       {c.DIM}Phone number information
        {c.BLUE}  03{c.RESET} MailFinder      {c.DIM}Find email with name
        {c.BLUE}  04{c.RESET} IPlocation      {c.DIM}IP to location tracker
        {c.BLUE}  05{c.RESET} SubdomainScan   {c.DIM}Subdomain enumeration
        {c.BLUE}  06{c.RESET} PortScanner     {c.DIM}Network port scanner
        {c.BLUE}  07{c.RESET} DNSRecon        {c.DIM}DNS reconnaissance
        {c.BLUE}  08{c.RESET} WHOISLookup     {c.DIM}Domain WHOIS information
        {c.BLUE}  09{c.RESET} SSLChecker      {c.DIM}SSL/TLS certificate check
        {c.BLUE}  10{c.RESET} HeaderAnalyzer  {c.DIM}Security headers analysis
        {c.BLUE}  11{c.RESET} GitHubRecon     {c.DIM}GitHub user reconnaissance
        {c.BLUE}  12{c.RESET} BreachChecker   {c.DIM}Check data breaches
        {c.BLUE}  13{c.RESET} TechDetector    {c.DIM}Website tech stack detector
        {c.BLUE}  14{c.RESET} ReverseIP       {c.DIM}Reverse IP lookup
        {c.BLUE}  15{c.RESET} Exit            {c.DIM}Exit application
        """)

    @staticmethod
    async def run():
        handlers = {
            "1": Menu.userrecon, "01": Menu.userrecon,
            "2": Menu.phoneinfo, "02": Menu.phoneinfo,
            "3": Menu.mailfinder, "03": Menu.mailfinder,
            "4": Menu.iplocation, "04": Menu.iplocation,
            "5": Menu.subdomain, "05": Menu.subdomain,
            "6": Menu.portscan, "06": Menu.portscan,
            "7": Menu.dnsrecon, "07": Menu.dnsrecon,
            "8": Menu.whois, "08": Menu.whois,
            "9": Menu.sslcheck, "09": Menu.sslcheck,
            "10": Menu.headers,
            "11": Menu.github,
            "12": Menu.breach,
            "13": Menu.techdetect,
            "14": Menu.reverseip,
        }

        while True:
            try:
                cmd = input(f"{config.SPACE}{c.BLUE}> choose:{c.RESET} ").strip().lower()
                if cmd in ("exit", "15"):
                    print(f"{c.RED}{config.SPACE}* Exiting!{c.RESET}")
                    break
                if cmd in handlers:
                    await handlers[cmd]()
                else:
                    print(f"{c.RED}{config.SPACE}* Invalid option{c.RESET}")
            except KeyboardInterrupt:
                print(f"{c.RED}\n{config.SPACE}* Aborted!{c.RESET}")
                break

    # ==================== HANDLERS ====================

    @staticmethod
    async def userrecon():
        username = input_prompt("enter username:")
        if not username: return
        print_header("USER RECON")
        results = await UserRecon.check_username(username)
        for r in results:
            print_user_result(r)
        separator()
        print_found(len(results))
        input(f"{config.SPACE}Press Enter to continue...")
        Menu.show()

    @staticmethod
    async def phoneinfo():
        phone = input_prompt("enter number:")
        if not phone: return
        data = await PhoneInfo.lookup(phone)
        print_header(f"PHONE INFO: {phone}")
        fields = {
            "phone_type": "Type", "country_prefix": "Prefix", "country_code": "Code",
            "country": "Country", "international_number": "Global",
            "local_number": "Local", "carrier": "Provider"
        }
        for k, label in fields.items():
            if k in data:
                print(f"{config.SPACE}{c.BLUE}-{c.RESET} {label:8}: {c.YELLOW}{data[k]}{c.RESET}")
        separator()
        input(f"{config.SPACE}Press Enter to continue...")
        Menu.show()

    @staticmethod
    async def mailfinder():
        name = input_prompt("enter full name:").lower()
        if not name: return
        print_header("GENERATING EMAILS")
        emails = await MailFinder.find_emails(name)
        if emails:
            filename = "result_mailfinder.txt"
            save_results(emails, filename)
        else:
            print(f"{config.SPACE}{c.RED}* No valid emails found{c.RESET}")
        separator()
        input(f"{config.SPACE}Press Enter to continue...")
        Menu.show()

    @staticmethod
    async def iplocation():
        local_ip = os.popen('curl -s ifconfig.co').read().strip()
        print(f"{config.SPACE}{c.BLUE}> local IP: {c.YELLOW}{local_ip}{c.RESET}")
        ip = input_prompt("enter IP:")
        if not ip: return
        data = await IPLocation.lookup(ip)
        print_header(f"IP LOCATION: {ip}")
        for k in ["ip", "city", "country", "loc", "org", "timezone"]:
            if k in data:
                print(f"{config.SPACE}{c.BLUE}-{c.RESET} {k.upper():8}: {data[k]}")
        separator()
        input(f"{config.SPACE}Press Enter to continue...")
        Menu.show()

    @staticmethod
    async def subdomain():
        domain = input_prompt("enter domain:")
        if not domain: return
        print_header("SUBDOMAIN SCAN")
        subs = await SubdomainScanner.scan(domain)
        for sub in subs:
            print(f"{config.SPACE}{c.BG_GREEN} FOUND {c.RESET} {sub}")
        if subs:
            save_results(subs, "result_subdomains.txt")
        separator()
        input(f"{config.SPACE}Press Enter to continue...")
        Menu.show()

    @staticmethod
    async def portscan():
        target = input_prompt("enter target (domain/IP):")
        if not target: return
        print_header(f"SCANNING {target}")
        results = await PortScanner.scan(target)
        for r in results:
            svc = PortScanner.COMMON_PORTS.get(r['port'], 'Unknown')
            print(f"{config.SPACE}{c.BG_GREEN} OPEN {c.RESET} Port {c.YELLOW}{r['port']}{c.RESET} - {svc}")
        if results:
            save_results([f"{r['port']}\t{PortScanner.COMMON_PORTS.get(r['port'], 'Unknown')}" for r in results],
                        "result_portscan.txt")
        separator()
        input(f"{config.SPACE}Press Enter to continue...")
        Menu.show()

    @staticmethod
    async def dnsrecon():
        domain = input_prompt("enter domain:")
        if not domain: return
        print_header("DNS RECON")
        data = await DNSRecon.lookup(domain)
        for k, v in data.items():
            if isinstance(v, list):
                for item in v:
                    print(f"{config.SPACE}{c.BLUE}{k} Record:{c.RESET} {item}")
            else:
                print(f"{config.SPACE}{c.BLUE}{k} Record:{c.RESET} {v}")
        separator()
        input(f"{config.SPACE}Press Enter to continue...")
        Menu.show()

    @staticmethod
    async def whois():
        domain = input_prompt("enter domain:")
        if not domain: return
        print_header("WHOIS LOOKUP")
        data = await WHOISLookup.lookup(domain)
        for line in data.split('\n')[:30]:
            if line.strip():
                print(f"{config.SPACE}{c.DIM}{line}{c.RESET}")
        separator()
        input(f"{config.SPACE}Press Enter to continue...")
        Menu.show()

    @staticmethod
    async def sslcheck():
        domain = input_prompt("enter domain:").split('/')[0].replace('http://', '').replace('https://', '')
        if not domain: return
        print_header("SSL CHECK")
        data = await SSLChecker.check(domain)
        if data:
            print(f"{config.SPACE}{c.BLUE}Subject:{c.RESET} {data['subject'].get('commonName', 'N/A')}")
            print(f"{config.SPACE}{c.BLUE}Issuer:{c.RESET} {data['issuer'].get('organizationName', 'N/A')}")
            print(f"{config.SPACE}{c.BLUE}Valid From:{c.RESET} {data['not_before']}")
            print(f"{config.SPACE}{c.BLUE}Valid Until:{c.RESET} {data['not_after']}")
            if data.get('expired'):
                print(f"{config.SPACE}{c.RED}Certificate EXPIRED!{c.RESET}")
            else:
                from datetime import datetime
                days = (datetime.strptime(data['not_after'], '%b %d %H:%M:%S %Y %Z') - datetime.now()).days
                print(f"{config.SPACE}{c.GREEN}Valid ({days} days left){c.RESET}")
        else:
            print(f"{config.SPACE}{c.RED}Failed to retrieve certificate{c.RESET}")
        separator()
        input(f"{config.SPACE}Press Enter to continue...")
        Menu.show()

    @staticmethod
    async def headers():
        url = input_prompt("enter URL:")
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        data = await HeaderAnalyzer.analyze(url)
        print_header("SECURITY HEADERS")
        score = data['score']
        total = data['total']
        print(f"{config.SPACE}{c.BLUE}Security Score:{c.RESET} {score}/{total} ({data['percentage']:.0f}%)")
        if data['percentage'] >= 80:
            print(f"{config.SPACE}{c.GREEN}Excellent security posture!{c.RESET}")
        elif data['percentage'] >= 50:
            print(f"{config.SPACE}{c.YELLOW}Moderate security{c.RESET}")
        else:
            print(f"{config.SPACE}{c.RED}Poor security - needs improvement{c.RESET}")
        separator()
        input(f"{config.SPACE}Press Enter to continue...")
        Menu.show()

    @staticmethod
    async def github():
        user = input_prompt("enter GitHub username:")
        if not user: return
        data = await GitHubRecon.recon(user)
        if not data:
            print(f"{config.SPACE}{c.RED}User not found or error{c.RESET}")
        else:
            print_header("GITHUB RECON")
            for k in ['name', 'bio', 'location', 'email', 'company', 'followers', 'public_repos']:
                print(f"{config.SPACE}{c.BLUE}{k.replace('_', ' ').title()}:{c.RESET} {data.get(k, 'N/A')}")
            if data.get('recent_repos'):
                print(f"\n{config.SPACE}{c.BG_BLUE} RECENT REPOS {c.RESET}")
                for repo in data['recent_repos']:
                    print(f"{config.SPACE}{c.YELLOW}▸{c.RESET} {repo['name']} - {repo.get('description', '')[:50]}")
        separator()
        input(f"{config.SPACE}Press Enter to continue...")
        Menu.show()

    @staticmethod
    async def breach():
        email = input_prompt("enter email:")
        if not email: return
        data = await DataBreachChecker.check(email)
        print_header("BREACH CHECK")
        if data.get('breaches'):
            print(f"{config.SPACE}{c.RED}Email found in {len(data['breaches'])} breaches!{c.RESET}")
            for b in data['breaches'][:10]:
                print(f"{config.SPACE}{c.YELLOW}▸{c.RESET} {b}")
        else:
            print(f"{config.SPACE}{c.GREEN}No breaches found{c.RESET}")
        separator()
        input(f"{config.SPACE}Press Enter to continue...")
        Menu.show()

    @staticmethod
    async def techdetect():
        url = input_prompt("enter URL:")
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        data = await TechStackDetector.detect(url)
        print_header("TECH STACK")
        for cat in ['servers', 'frameworks', 'analytics', 'cdn']:
            if data[cat]:
                print(f"{config.SPACE}{c.BLUE}{cat.title()}:{c.RESET} {', '.join(data[cat])}")
        separator()
        input(f"{config.SPACE}Press Enter to continue...")
        Menu.show()

    @staticmethod
    async def reverseip():
        domain = input_prompt("enter domain:")
        if not domain: return
        domains = await ReverseIPLookup.lookup(domain)
        print_header("REVERSE IP")
        if domains:
            print(f"{config.SPACE}{c.BLUE}IP:{c.RESET} {socket.gethostbyname(domain)}")
            for i, d in enumerate(domains[:20], 1):
                print(f"{config.SPACE}{c.YELLOW}{i}.{c.RESET} {d}")
            if len(domains) > 20:
                print(f"{config.SPACE}{c.DIM}... and {len(domains)-20} more{c.RESET}")
            save_results(domains, "result_reverseip.txt")
        separator()
        input(f"{config.SPACE}Press Enter to continue...")
        Menu.show()