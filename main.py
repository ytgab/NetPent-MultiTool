#!/usr/bin/env python3

import os
import re
import shutil
import subprocess
import sys
import time


# ============================================================
# NETPENT
# ============================================================

APP_NAME = "NETPENT"
VERSION = "1.5.0"

RESET = "\033[0m"
CYAN = "\033[96m"
BLUE = "\033[94m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
WHITE = "\033[97m"
GRAY = "\033[90m"

BOX_WIDTH = 86


# ============================================================
# TERMINAL / UI
# ============================================================

def clear():
    os.system("clear")


def terminal_width():
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 120


def ui_width():
    return min(
        BOX_WIDTH,
        max(60, terminal_width() - 8)
    )


def ui_left():
    """
    Returns the exact left edge of the centered UI.
    """

    return max(
        0,
        (terminal_width() - ui_width()) // 2
    )


def strip_ansi(text):
    return re.sub(
        r"\033\[[0-9;]*m",
        "",
        text
    )


def centered(text):
    length = len(strip_ansi(text))

    return (
        " " * max(
            0,
            (terminal_width() - length) // 2
        )
        + text
    )


def inside_center(text, width):

    length = len(strip_ansi(text))

    if length >= width:
        return text[:width]

    left = (width - length) // 2
    right = width - length - left

    return (
        " " * left
        + text
        + " " * right
    )


def inside_left(text, width):

    length = len(strip_ansi(text))

    if length >= width:
        return text[:width]

    return text + " " * (width - length)


def cprint(text=""):
    print(centered(text))


# ============================================================
# UNIVERSAL INPUT
# ============================================================

def ask(prompt):
    """
    UNIVERSAL INPUT FUNCTION.

    Every input in NETPENT goes through this function.

    This guarantees that prompts such as:

        netpent@linux:~$
        Target IP / hostname:
        Port:
        Press ENTER:

    all start at the same left edge of the centered UI.
    """

    padding = " " * ui_left()

    print(
        padding + prompt,
        end="",
        flush=True
    )

    return input().strip()


def get_target():

    print()

    return ask(
        f"{CYAN}Target IP / hostname: {RESET}"
    )


def get_port():

    print()

    value = ask(
        f"{CYAN}Port [80]: {RESET}"
    )

    if value == "":
        return "80"

    if not value.isdigit():

        cprint(
            f"{RED}[!] Invalid port.{RESET}"
        )

        pause()

        return None

    port = int(value)

    if port < 1 or port > 65535:

        cprint(
            f"{RED}[!] Port must be between 1 and 65535.{RESET}"
        )

        pause()

        return None

    return str(port)


def pause():

    print()

    ask(
        f"{CYAN}Press ENTER to continue... {RESET}"
    )


# ============================================================
# COMMAND HELPERS
# ============================================================

def command_exists(command):
    return shutil.which(command) is not None


def run_command(command):
    """
    Run an external command and keep its output aligned
    with the centered NETPENT interface.

    This applies automatically to:
        nmap
        hping3
        curl
        ip
        ss
        whois
        dig
        host
        traceroute
        openssl
        whatweb
        etc.
    """

    try:

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False
        )

        output = result.stdout or ""

        width = ui_width()
        padding = " " * ui_left()

        # Nothing was printed
        if not output.strip():

            if result.returncode != 0:

                print(
                    padding
                    + f"{RED}[!] Command exited with code "
                    f"{result.returncode}{RESET}"
                )

            return

        # Print every output line at the UI's left edge
        for line in output.rstrip().splitlines():

            clean_line = strip_ansi(line)

            # Keep very long terminal output inside the UI width.
            # Do not move it to the far right.
            if len(clean_line) > width:

                while len(clean_line) > width:

                    part = clean_line[:width]

                    print(
                        padding
                        + part
                    )

                    clean_line = clean_line[width:]

                if clean_line:

                    print(
                        padding
                        + clean_line
                    )

            else:

                print(
                    padding
                    + line
                )

        # Show command errors
        if result.returncode != 0:

            print()

            print(
                padding
                + f"{RED}[!] Command exited with code "
                f"{result.returncode}{RESET}"
            )

    except FileNotFoundError:

        print(
            " " * ui_left()
            + f"{RED}[!] Command not found: "
            f"{command[0]}{RESET}"
        )

    except Exception as error:

        print(
            " " * ui_left()
            + f"{RED}[!] Error: {error}{RESET}"
        )

# ============================================================
# LOGO
# ============================================================

def show_logo():

    logo = [
        "███╗   ██╗███████╗████████╗██████╗ ███████╗███╗   ██╗████████╗",
        "████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔════╝████╗  ██║╚══██╔══╝",
        "██╔██╗ ██║█████╗     ██║   ██████╔╝█████╗  ██╔██╗ ██║   ██║",
        "██║╚██╗██║██╔══╝     ██║   ██╔═══╝ ██╔══╝  ██║╚██╗██║   ██║",
        "██║ ╚████║███████╗   ██║   ██║     ███████╗██║ ╚████║   ██║",
        "╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝     ╚══════╝╚═╝  ╚═══╝   ╚═╝"
    ]

    print()

    for line in logo:

        cprint(
            f"{CYAN}{line}{RESET}"
        )

    print()

    cprint(
        f"{BLUE}~ Present Day, Present Time ~{RESET}"
    )

    print()


# ============================================================
# NAVIGATION
# ============================================================

def draw_navigation(active):

    width = ui_width()
    inner = width - 2

    categories = [
        "SCANNING",
        "NETWORK",
        "WEB",
        "DNS",
        "OSINT",
        "UTILITY"
    ]

    parts = []

    for category in categories:

        if category == active:

            parts.append(
                f"{GREEN}▶ {category}{RESET}"
            )

        else:

            parts.append(
                f"{WHITE}{category}{RESET}"
            )

    text = " | ".join(parts)

    cprint(
        f"{CYAN}┌{'─' * inner}┐{RESET}"
    )

    cprint(
        f"{CYAN}│{RESET}"
        + inside_center(text, inner)
        + f"{CYAN}│{RESET}"
    )

    cprint(
        f"{CYAN}└{'─' * inner}┘{RESET}"
    )


# ============================================================
# MENU
# ============================================================

def draw_menu(title, items):

    width = ui_width()
    inner = width - 2

    print()

    cprint(
        f"{BLUE}┌{'─' * inner}┐{RESET}"
    )

    cprint(
        f"{BLUE}│{RESET}"
        + inside_center(
            f"{CYAN}{title}{RESET}",
            inner
        )
        + f"{BLUE}│{RESET}"
    )

    cprint(
        f"{BLUE}├{'─' * inner}┤{RESET}"
    )

    for number, name, description in items:

        label = f"[{number}] {name}"

        label_width = 31

        if len(label) < label_width:

            label += (
                " " *
                (label_width - len(label))
            )

        line = (
            f"{CYAN}{label}{RESET}"
            f"{GRAY}—{RESET} "
            f"{WHITE}{description}{RESET}"
        )

        cprint(
            f"{BLUE}│{RESET}"
            + inside_left(line, inner)
            + f"{BLUE}│{RESET}"
        )

    cprint(
        f"{BLUE}└{'─' * inner}┘{RESET}"
    )


# ============================================================
# FOOTER
# ============================================================

def draw_footer():

    width = ui_width()
    inner = width - 2

    print()

    cprint(
        f"{CYAN}┌{'─' * inner}┐{RESET}"
    )

    footer = (
        "[P/N] Prev/Next Page"
        "  |  [60] Info"
        "  |  [61] Settings"
        "  |  [99] Exit"
    )

    cprint(
        f"{CYAN}│{RESET}"
        + inside_center(
            footer,
            inner
        )
        + f"{CYAN}│{RESET}"
    )

    cprint(
        f"{CYAN}└{'─' * inner}┘{RESET}"
    )

    print()

    cprint(
        f"{CYAN}{APP_NAME} v{VERSION}"
        f" | Linux Security Toolkit{RESET}"
    )


def draw_screen(page):

    clear()

    show_logo()

    current = PAGES[page]

    draw_navigation(
        current["name"]
    )

    draw_menu(
        current["title"],
        current["items"]
    )

    draw_footer()


# ============================================================
# SCANNING TOOLS
# ============================================================

def simple_port_scan():

    target = get_target()

    if not target:
        return

    if not command_exists("nmap"):

        cprint(
            f"{RED}[!] Nmap is not installed.{RESET}"
        )

        pause()
        return

    print()

    cprint(
        f"{GREEN}[+] Starting Simple Port Scan...{RESET}"
    )

    run_command([
        "nmap",
        target
    ])

    pause()


def service_detection():

    target = get_target()

    if not target:
        return

    if not command_exists("nmap"):

        cprint(
            f"{RED}[!] Nmap is not installed.{RESET}"
        )

        pause()
        return

    print()

    cprint(
        f"{GREEN}[+] Starting Service Detection...{RESET}"
    )

    run_command([
        "nmap",
        "-sV",
        target
    ])

    pause()


def os_detection():

    target = get_target()

    if not target:
        return

    if not command_exists("nmap"):

        cprint(
            f"{RED}[!] Nmap is not installed.{RESET}"
        )

        pause()
        return

    print()

    cprint(
        f"{YELLOW}[!] OS detection may require root privileges.{RESET}"
    )

    run_command([
        "sudo",
        "nmap",
        "-O",
        target
    ])

    pause()


def common_ports():

    target = get_target()

    if not target:
        return

    if not command_exists("nmap"):

        cprint(
            f"{RED}[!] Nmap is not installed.{RESET}"
        )

        pause()
        return

    print()

    cprint(
        f"{GREEN}[+] Scanning common ports...{RESET}"
    )

    run_command([
        "nmap",
        "--top-ports",
        "100",
        target
    ])

    pause()


def full_nmap_scan():

    target = get_target()

    if not target:
        return

    if not command_exists("nmap"):

        cprint(
            f"{RED}[!] Nmap is not installed.{RESET}"
        )

        pause()
        return

    print()

    cprint(
        f"{YELLOW}[!] Authorized testing only.{RESET}"
    )

    run_command([
        "nmap",
        "-sV",
        "-O",
        target
    ])

    pause()


# ============================================================
# NETWORK TOOLS
# ============================================================

def ping_test():

    target = get_target()

    if target:

        run_command([
            "ping",
            "-c",
            "4",
            target
        ])

    pause()


def traceroute_test():

    target = get_target()

    if not target:
        return

    if not command_exists("traceroute"):

        cprint(
            f"{RED}[!] traceroute is not installed.{RESET}"
        )

        pause()
        return

    run_command([
        "traceroute",
        target
    ])

    pause()


def dns_lookup():

    target = get_target()

    if not target:
        return

    if not command_exists("host"):

        cprint(
            f"{RED}[!] host is not installed.{RESET}"
        )

        pause()
        return

    run_command([
        "host",
        target
    ])

    pause()


def hping_test():

    target = get_target()

    if not target:
        return

    if not command_exists("hping3"):

        cprint(
            f"{RED}[!] hping3 is not installed.{RESET}"
        )

        pause()
        return

    port = get_port()

    if not port:
        return

    print()

    cprint(
        f"{YELLOW}[!] Limited diagnostic test: 5 packets.{RESET}"
    )

    run_command([
        "sudo",
        "hping3",
        "--icmp",
        "-d",
        "65000",
        "-V",
        port,
        target
    ])

    pause()


# ============================================================
# WEB TOOLS
# ============================================================

def normalize_url(target):

    if target.startswith("http://"):
        return target

    if target.startswith("https://"):
        return target

    return "https://" + target


def http_headers():

    target = get_target()

    if not target:
        return

    target = normalize_url(target)

    run_command([
        "curl",
        "-I",
        "--max-time",
        "10",
        target
    ])

    pause()


def http_status():

    target = get_target()

    if not target:
        return

    target = normalize_url(target)

    run_command([
        "curl",
        "-s",
        "-o",
        "/dev/null",
        "-w",
        "HTTP Status: %{http_code}\n",
        "--max-time",
        "10",
        target
    ])

    pause()


def tls_information():

    target = get_target()

    if not target:
        return

    target = (
        target
        .replace("https://", "")
        .replace("http://", "")
        .split("/")[0]
    )

    run_command([
        "openssl",
        "s_client",
        "-connect",
        f"{target}:443",
        "-servername",
        target
    ])

    pause()


def whatweb_test():

    target = get_target()

    if not target:
        return

    if not command_exists("whatweb"):

        cprint(
            f"{RED}[!] WhatWeb is not installed.{RESET}"
        )

        pause()
        return

    run_command([
        "whatweb",
        target
    ])

    pause()


# ============================================================
# DNS TOOLS
# ============================================================

def dig_query(record=None):

    target = get_target()

    if not target:
        return

    if not command_exists("dig"):

        cprint(
            f"{RED}[!] dig is not installed.{RESET}"
        )

        pause()
        return

    command = [
        "dig",
        target
    ]

    if record:
        command.append(record)

    run_command(command)

    pause()


def reverse_dns():

    target = get_target()

    if not target:
        return

    if not command_exists("dig"):

        cprint(
            f"{RED}[!] dig is not installed.{RESET}"
        )

        pause()
        return

    run_command([
        "dig",
        "-x",
        target
    ])

    pause()


# ============================================================
# OSINT
# ============================================================

def whois_lookup():

    target = get_target()

    if not target:
        return

    if not command_exists("whois"):

        cprint(
            f"{RED}[!] whois is not installed.{RESET}"
        )

        pause()
        return

    run_command([
        "whois",
        target
    ])

    pause()


def subdomain_check():

    target = get_target()

    if not target:
        return

    if not command_exists("host"):

        cprint(
            f"{RED}[!] host is not installed.{RESET}"
        )

        pause()
        return

    subdomains = [
        "www",
        "mail",
        "ftp",
        "api",
        "dev",
        "test"
    ]

    for subdomain in subdomains:

        hostname = (
            f"{subdomain}.{target}"
        )

        cprint(
            f"{CYAN}[*] Checking {hostname}{RESET}"
        )

        run_command([
            "host",
            hostname
        ])

    pause()


# ============================================================
# UTILITY
# ============================================================

def public_ip():

    if not command_exists("curl"):

        cprint(
            f"{RED}[!] curl is not installed.{RESET}"
        )

        pause()
        return

    run_command([
        "curl",
        "-s",
        "--max-time",
        "10",
        "https://checkip.amazonaws.com"
    ])

    pause()


def local_ip():

    run_command([
        "hostname",
        "-I"
    ])

    pause()


def interfaces():

    run_command([
        "ip",
        "addr"
    ])

    pause()


def active_connections():

    run_command([
        "ss",
        "-tunap"
    ])

    pause()


def tool_status():

    tools = [
        "nmap",
        "hping3",
        "whois",
        "host",
        "dig",
        "traceroute",
        "curl",
        "openssl",
        "whatweb"
    ]

    print()

    for tool in tools:

        if command_exists(tool):

            cprint(
                f"{GREEN}[+] {tool:<12} installed{RESET}"
            )

        else:

            cprint(
                f"{RED}[-] {tool:<12} missing{RESET}"
            )

    pause()


# ============================================================
# INFO
# ============================================================

def show_info():

    clear()

    show_logo()

    width = ui_width()
    inner = width - 2

    cprint(
        f"{CYAN}┌{'─' * inner}┐{RESET}"
    )

    information = [
        f"Name: {APP_NAME}",
        f"Version: {VERSION}",
        "Platform: Linux",
        "",
        "Security testing & network diagnostics",
        "",
        "Use only against systems you own",
        "or are authorized to test."
    ]

    for line in information:

        cprint(
            f"{CYAN}│{RESET}"
            + inside_center(
                line,
                inner
            )
            + f"{CYAN}│{RESET}"
        )

    cprint(
        f"{CYAN}└{'─' * inner}┘{RESET}"
    )

    pause()


# ============================================================
# SETTINGS
# ============================================================

def settings():

    while True:

        clear()

        show_logo()

        width = ui_width()
        inner = width - 2

        cprint(
            f"{CYAN}┌{'─' * inner}┐{RESET}"
        )

        cprint(
            f"{CYAN}│{RESET}"
            + inside_center(
                "SETTINGS",
                inner
            )
            + f"{CYAN}│{RESET}"
        )

        cprint(
            f"{CYAN}├{'─' * inner}┤{RESET}"
        )

        cprint(
            f"{CYAN}│{RESET}"
            + inside_center(
                "[1] Tool Status",
                inner
            )
            + f"{CYAN}│{RESET}"
        )

        cprint(
            f"{CYAN}│{RESET}"
            + inside_center(
                "[0] Back",
                inner
            )
            + f"{CYAN}│{RESET}"
        )

        cprint(
            f"{CYAN}└{'─' * inner}┘{RESET}"
        )

        print()

        choice = ask(
            f"{CYAN}netpent@settings:~$ {RESET}"
        ).lower()

        if choice == "0":
            return

        if choice == "1":

            tool_status()

        else:

            cprint(
                f"{RED}[!] Invalid option: {choice}{RESET}"
            )

            time.sleep(1)


# ============================================================
# PAGES
# ============================================================

PAGES = [

    {
        "name": "SCANNING",

        "title": "SCANNING TOOLS",

        "items": [
            (
                "1",
                "Simple Port Scan",
                "Basic Nmap port scan"
            ),
            (
                "2",
                "Service Detection",
                "Detect running services"
            ),
            (
                "3",
                "OS Detection",
                "Identify operating system"
            ),
            (
                "4",
                "Common Ports",
                "Scan common ports"
            ),
            (
                "5",
                "Full Nmap Scan",
                "Extended authorized scan"
            )
        ],

        "actions": {
            "1": simple_port_scan,
            "2": service_detection,
            "3": os_detection,
            "4": common_ports,
            "5": full_nmap_scan
        }
    },

    {
        "name": "NETWORK",

        "title": "NETWORK TESTING",

        "items": [
            (
                "1",
                "Ping",
                "ICMP connectivity test"
            ),
            (
                "2",
                "Traceroute",
                "Trace network path"
            ),
            (
                "3",
                "DNS Lookup",
                "Resolve hostname"
            ),
            (
                "4",
                "hping3 Test",
                "Limited packet diagnostic"
            ),
            (
                "5",
                "Local Network",
                "Show network interfaces"
            )
        ],

        "actions": {
            "1": ping_test,
            "2": traceroute_test,
            "3": dns_lookup,
            "4": hping_test,
            "5": local_network
        }
    },

    {
        "name": "WEB",

        "title": "WEB TESTING",

        "items": [
            (
                "1",
                "HTTP Headers",
                "Inspect response headers"
            ),
            (
                "2",
                "HTTP Status",
                "Check HTTP status"
            ),
            (
                "3",
                "TLS Information",
                "Inspect TLS connection"
            ),
            (
                "4",
                "WhatWeb",
                "Identify web technologies"
            )
        ],

        "actions": {
            "1": http_headers,
            "2": http_status,
            "3": tls_information,
            "4": whatweb_test
        }
    },

    {
        "name": "DNS",

        "title": "DNS & DOMAIN",

        "items": [
            (
                "1",
                "DNS Lookup",
                "Query DNS records"
            ),
            (
                "2",
                "Reverse DNS",
                "Reverse IP lookup"
            ),
            (
                "3",
                "MX Records",
                "Mail server records"
            ),
            (
                "4",
                "NS Records",
                "Name server records"
            ),
            (
                "5",
                "TXT Records",
                "TXT DNS records"
            )
        ],

        "actions": {
            "1": lambda: dig_query(),
            "2": reverse_dns,
            "3": lambda: dig_query("MX"),
            "4": lambda: dig_query("NS"),
            "5": lambda: dig_query("TXT")
        }
    },

    {
        "name": "OSINT",

        "title": "OSINT TOOLS",

        "items": [
            (
                "1",
                "Whois",
                "Domain registration information"
            ),
            (
                "2",
                "DNS Information",
                "Basic DNS information"
            ),
            (
                "3",
                "Subdomain Check",
                "Basic subdomain checks"
            )
        ],

        "actions": {
            "1": whois_lookup,
            "2": dns_lookup,
            "3": subdomain_check
        }
    },

    {
        "name": "UTILITY",

        "title": "UTILITY TOOLS",

        "items": [
            (
                "1",
                "Public IP",
                "Show public IP"
            ),
            (
                "2",
                "Local IP",
                "Show local addresses"
            ),
            (
                "3",
                "Interfaces",
                "Show network interfaces"
            ),
            (
                "4",
                "Connections",
                "Show active connections"
            ),
            (
                "5",
                "Tool Status",
                "Check installed tools"
            )
        ],

        "actions": {
            "1": public_ip,
            "2": local_ip,
            "3": interfaces,
            "4": active_connections,
            "5": tool_status
        }
    }
]


# ============================================================
# MAIN
# ============================================================

def main():

    page = 0

    while True:

        draw_screen(page)

        print()

        choice = ask(
            f"{CYAN}netpent@linux:~$ {RESET}"
        ).lower()

        # ----------------------------------------------------
        # PAGE NAVIGATION
        # ----------------------------------------------------

        if choice == "p":

            page -= 1

            if page < 0:
                page = len(PAGES) - 1

            continue

        if choice == "n":

            page += 1

            if page >= len(PAGES):
                page = 0

            continue

        # ----------------------------------------------------
        # GLOBAL OPTIONS
        # ----------------------------------------------------

        if choice == "60":

            show_info()
            continue

        if choice == "61":

            settings()
            continue

        if choice == "99":

            clear()

            print()

            cprint(
                f"{GREEN}Thanks for using {APP_NAME}.{RESET}"
            )

            print()

            sys.exit(0)

        # ----------------------------------------------------
        # TOOL SELECTION
        # ----------------------------------------------------

        current = PAGES[page]

        action = current["actions"].get(choice)

        if action:

            action()
            continue

        # ----------------------------------------------------
        # INVALID OPTION
        # ----------------------------------------------------

        cprint(
            f"{RED}[!] Invalid option: {choice}{RESET}"
        )

        time.sleep(1)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        clear()

        print()

        cprint(
            f"{YELLOW}Interrupted. Goodbye!{RESET}"
        )

        print()

        sys.exit(0)
