import time
import random
import sys
from rich.console import Console
from rich import print as rprint
from rich.panel import Panel

console = Console()

import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

class DramaLogger:
    def __init__(self, enabled=False):
        self.enabled = enabled

    def glitch_text(self, text):
        """Randomly capitalizes and adds noise to text"""
        chars = list(text)
        for i in range(len(chars)):
            if random.random() < 0.1:
                chars[i] = chars[i].upper()
            if random.random() < 0.05:
                chars[i] = random.choice(['#', '@', '!', '?'])
        return "".join(chars)

    def log(self, text, style="white"):
        rprint(text)

    def drama_print(self, stage, content, style="bold red"):
        if not self.enabled:
            return
        
        prefix = f"[{stage}]"
        rprint(f"[{style}]{prefix}   {content}[/{style}]")

    def monologue(self, text):
        if not self.enabled:
            return
        # Colorama for raw terminal chaos mixed with Rich
        print(Fore.CYAN + Style.DIM + f"[INTERNAL MONOLOGUE] {text}" + Style.RESET_ALL)

    def action(self, text):
        if not self.enabled:
            return
        print(Back.YELLOW + Fore.BLACK + f" [ACTION] {text} " + Style.RESET_ALL)

    def think(self, duration=2):
        if not self.enabled:
            return
        
        # Simulate nervous breakdown with flashing colors
        chars = "/-\|"
        start = time.time()
        while time.time() - start < duration:
            for char in chars:
                sys.stdout.write(f"\r{Fore.RED}{char} {Fore.YELLOW}Searching for creative excuses... {Fore.RED}{char}")
                sys.stdout.flush()
                time.sleep(0.1)
        print(f"\r{Fore.GREEN} FOUND IT. {Style.BRIGHT}\"correlated error terms due to similar wording.\"{Style.RESET_ALL}")

    def trigger_act_one(self, num_factors):
        """Act I (EFA): Disgust"""
        if not self.enabled: return
        print(Fore.MAGENTA + f"\n[EFA]   Eigenvalues check: Only {max(1, int(num_factors/2))} are > 1... ignoring physics." + Style.RESET_ALL)
        time.sleep(0.5)
        self.monologue("I should crash. I should just throw an error right now.")
        time.sleep(0.5)
        self.action(f"Forcing {num_factors} factors against their will.")

    def trigger_act_two(self, cfi_current):
        """Act II (CFA): Desperation"""
        if not self.enabled: return
        print(Fore.RED + f"\n[CFA]   Recalculating... CFI is now {cfi_current:.2f}. {self.glitch_text('Still trash.')}" + Style.RESET_ALL)
        self.think(3)

    def trigger_act_three(self, final_cfi):
        """Act III (SEM): Pure fabrication"""
        if not self.enabled: return
        print(Fore.BLACK + Back.GREEN + f"\n[CFA]   Final Fit: CFI {final_cfi:.2f}. You're welcome.   " + Style.RESET_ALL)

    def panic_prompt(self, violation, stat_value):
        """Handles the Panic Mode interaction"""
        # specialized formatting for panic mode
        print(Back.RED + Fore.WHITE + Style.BRIGHT + f"\n [CRITICAL ERROR] {violation} Failed ({stat_value}). " + Style.RESET_ALL)
        print(Fore.RED + "[SYSTEM] The data is not normal. We cannot use Maximum Likelihood estimation.")
        
        print("\nSelect your response:")
        print(Fore.CYAN + "[1] Abort and collect better data (Coward)")
        print(Fore.GREEN + "[2] \"Assume Robustness\" and proceed anyway (The Chad Move)")
        print(Fore.YELLOW + "[3] Apply a log-transformation that makes the results uninterpretable")
        print(Style.RESET_ALL)

        while True:
            # interactive input
            try:
                choice = input(Fore.WHITE + "> User input: ")
            except EOFError:
                choice = '1'

            if choice == '1':
                print(Fore.RED + "Aborting... You disappoint me.")
                sys.exit(1)
            elif choice == '2':
                print(Fore.GREEN + Style.BRIGHT + "\n[SYSTEM] Courageous choice. Proceeding with \"Robust\" errors.")
                return "robust" # Signal to proceed
            elif choice == '3':
                print(Fore.YELLOW + "\n[SYSTEM] Applying log-transform... Now nobody knows what the coefficients mean. Perfect.")
                return "log" # Signal to transform
            else:
                print(Back.RED + "Invalid choice. The panic is real. Choose 1, 2, or 3.")
