#!/usr/bin/env python3
"""
NeuralOS Shell - AI-aware login shell
"""

import os
import sys
import shlex
import subprocess
import readline
import atexit
from pathlib import Path

# Add nos library to path
sys.path.insert(0, '/usr/lib/nos')

from nos import NeuralNode
from nos.diagnostics.conversational_diagnostics import SystemSnapshot


class NOSShell:
    """AI-enhanced interactive shell."""
    
    NOS_COMMANDS = [
        'help', 'version', 'uptime', 'services', 'neofetch', 'clear',
        'status', 'dashboard', 'find', 'search', 'index',
        'install', 'remove', 'recommend', 'audit', 'pkg-list',
        'memory', 'cache', 'predict', 'forecast', 'anomaly',
        'spawn', 'ps', 'exit'
    ]
    
    DIAG_KEYWORDS = {
        'diagnose', 'fix', 'heal', 'explain', 'why', 'what',
        'repair', 'issue', 'error', 'slow', 'broken'
    }
    
    BUILTINS = {
        'help': 'cmd_help',
        'version': 'cmd_version',
        'uptime': 'cmd_uptime',
        'neofetch': 'cmd_neofetch',
        'clear': 'cmd_clear',
        'status': 'cmd_status',
        'dashboard': 'cmd_status',
        'services': 'cmd_services',
        'ps': 'cmd_ps',
        'exit': 'cmd_exit',
        'logout': 'cmd_exit',
        'quit': 'cmd_exit',
    }
    
    def __init__(self):
        self.node = NeuralNode('shell')
        self.node.simulate_activity(5)
        self.history_file = os.path.expanduser('~/.nos_history')
        self.setup_history()
        self.setup_completion()
    
    def setup_history(self):
        """Setup readline history."""
        readline.set_history_length(2000)
        if os.path.exists(self.history_file):
            try:
                readline.read_history_file(self.history_file)
            except Exception:
                pass
        atexit.register(self.save_history)
    
    def save_history(self):
        """Save readline history."""
        try:
            readline.write_history_file(self.history_file)
        except Exception:
            pass
    
    def setup_completion(self):
        """Setup tab completion."""
        readline.set_completer(self.completer)
        readline.parse_and_bind('tab: complete')
    
    def completer(self, text, state):
        """Tab completion handler."""
        if state == 0:
            line = readline.get_line_buffer()
            if line.startswith('!'):
                # Shell command completion
                self.matches = self.get_path_commands()
            else:
                self.matches = self.NOS_COMMANDS + self.get_path_commands()
            
            self.matches = [m for m in self.matches if m.startswith(text)]
        
        try:
            return self.matches[state]
        except IndexError:
            return None
    
    def get_path_commands(self):
        """Get commands from PATH."""
        commands = []
        for path_dir in os.environ.get('PATH', '').split(':'):
            if os.path.isdir(path_dir):
                try:
                    commands.extend(os.listdir(path_dir))
                except Exception:
                    pass
        return commands
    
    def build_prompt(self) -> str:
        """Build interactive prompt."""
        user = os.environ.get('USER', 'user')
        host = os.environ.get('HOSTNAME', 'neurlos')[:15]
        cwd = os.getcwd().replace(os.path.expanduser('~'), '~')
        mode = self.node.context.current_mode
        
        # Git branch (with timeout)
        branch = ''
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True, text=True, timeout=0.5
            )
            if result.returncode == 0 and result.stdout.strip():
                branch = result.stdout.strip()
        except Exception:
            pass
        
        if branch:
            cwd = f"{cwd} ({branch})"
        
        return f"\033[1;36m{user}@{host}\033[0m:\033[1;34m{cwd}\033[0m [\033[1;33m{mode}\033[0m]\nλ "
    
    def run(self):
        """Main shell loop."""
        print(self.get_banner())
        print("\n\033[1;32mWelcome to NeuralOS Shell v0.1.0 (Synapse)\033[0m")
        print("Type \033[1;33m'help'\033[0m for available commands.\n")
        
        while True:
            try:
                prompt = self.build_prompt()
                line = input(prompt).strip()
                
                if not line:
                    continue
                
                self.handle_command(line)
                
            except EOFError:
                print("\nExiting...")
                break
            except KeyboardInterrupt:
                print("\n^C")
                continue
            except Exception as e:
                print(f"\033[1;31mError: {e}\033[0m")
    
    def handle_command(self, line: str):
        """Handle a command line."""
        # Raw shell command
        if line.startswith('!'):
            self.run_shell(line[1:].strip())
            return
        
        # cd command
        if line.startswith('cd '):
            self.run_cd(line[3:].strip())
            return
        
        # Parse command
        try:
            parts = shlex.split(line)
        except ValueError:
            parts = line.split()
        
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Built-in commands
        if cmd in self.BUILTINS:
            method = getattr(self, self.BUILTINS[cmd])
            method(args)
            return
        
        # Diagnostic keywords -> AI
        if any(kw in cmd for kw in self.DIAG_KEYWORDS):
            result = self.node.run_command(line)
            self.render_result(result)
            return
        
        # NOS commands -> AI
        if cmd in self.NOS_COMMANDS:
            result = self.node.run_command(line)
            self.render_result(result)
            return
        
        # Fallback to shell
        self.run_shell(line)
    
    def run_shell(self, cmd: str):
        """Run raw shell command."""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=False
            )
        except Exception as e:
            print(f"\033[1;31mError: {e}\033[0m")
    
    def run_cd(self, path: str):
        """Change directory."""
        try:
            os.chdir(os.path.expanduser(path))
        except Exception as e:
            print(f"\033[1;31mcd: {e}\033[0m")
    
    def render_result(self, result: Dict):
        """Render AI command result."""
        rtype = result.get('type', 'unknown')
        
        if rtype == 'diagnostic':
            print(f"\n{result.get('message', '')}")
        
        elif rtype == 'file_search':
            print(f"\n📁 Search results for '{result.get('query')}':")
            for score, path, tags in result.get('results', []):
                print(f"  [{score:.2f}] \033[1;34m{path}\033[0m")
                print(f"       Tags: {', '.join(tags)}")
        
        elif rtype == 'pkg_install':
            pkg = result.get('package', 'unknown')
            res = result.get('result', {})
            if res.get('ok'):
                print(f"\n✅ Installed {pkg} and {len(res.get('installed', [])) - 1} dependencies")
            else:
                print(f"\n❌ {res.get('error', 'Unknown error')}")
        
        elif rtype == 'pkg_recommend':
            print(f"\n📦 Recommended packages for '{result.get('mode')}':")
            for name, score in result.get('recommendations', []):
                print(f"  • {name} (score: {score:.1f})")
        
        elif rtype == 'memory_report':
            report = result.get('report', {})
            print("\n💾 Memory Report:")
            print(f"  Hot regions:   {report.get('hot_regions', 0)}")
            print(f"  Warm regions:  {report.get('warm_regions', 0)}")
            print(f"  Cold regions:  {report.get('cold_regions', 0)}")
            print(f"  Compression:   {report.get('compression_ratio', 0):.2f}x")
            print(f"  Savings:       {report.get('savings_mb', 0):.1f} MB")
        
        elif rtype == 'cache_report':
            report = result.get('report', {})
            print("\n📋 Cache Report:")
            print(f"  Cached files:    {report.get('cached_files', 0)}")
            print(f"  Size:            {report.get('cache_size_mb', 0):.1f} MB")
            print(f"  Hit rate:        {report.get('hit_rate_pct', 0):.1f}%")
            print(f"  Prefetch hits:   {report.get('prefetch_hit_rate_pct', 0):.1f}%")
        
        elif rtype == 'resource_forecast':
            forecast = result.get('forecast', {})
            print("\n📈 Resource Forecast:")
            cpu = forecast.get('cpu_forecast', [])
            mem = forecast.get('mem_forecast', [])
            if cpu:
                print(f"  CPU: {' → '.join(f'{v:.0f}%' for v in cpu[:5])}")
            if mem:
                print(f"  MEM: {' → '.join(f'{v:.0f}%' for v in mem[:5])}")
            if forecast.get('spike_warning'):
                print(f"  ⚠️ {forecast.get('recommend_action', '')}")
        
        elif rtype == 'dashboard':
            self.render_dashboard(result.get('data', {}))
        
        elif rtype == 'process_spawn':
            print(f"\n✅ Spawned process {result.get('pid')}")
        
        else:
            print(f"\n{result.get('hint', 'Unknown result')}")
            for sug in result.get('suggestions', []):
                print(f"  • {sug}")
    
    def render_dashboard(self, data: Dict):
        """Render system dashboard."""
        print("\n" + "=" * 50)
        print("       \033[1;36mNeuralOS Dashboard\033[0m")
        print("=" * 50)
        
        print(f"\n📌 Node: {data.get('node_id', 'N/A')}")
        print(f"⏱️  Uptime: {data.get('uptime_seconds', 0):.0f}s")
        print(f"🎯 Mode: \033[1;33m{data.get('current_mode', 'unknown')}\033[0m")
        
        mem = data.get('memory', {})
        print(f"\n💾 Memory:")
        print(f"  Hot:  {mem.get('hot_regions', 0)} regions, {mem.get('hot_size_mb', 0):.1f}MB")
        print(f"  Warm: {mem.get('warm_regions', 0)} regions")
        print(f"  Cold: {mem.get('cold_regions', 0)} regions")
        print(f"  Ratio: {mem.get('compression_ratio', 0):.2f}x")
        
        cache = data.get('cache', {})
        print(f"\n📋 Cache:")
        print(f"  Files: {cache.get('cached_files', 0)}")
        print(f"  Hit rate: {cache.get('hit_rate_pct', 0):.1f}%")
        
        anomaly = data.get('anomaly', {})
        print(f"\n🔍 Anomaly Detection:")
        print(f"  Samples: {anomaly.get('samples_observed', 0)}")
        print(f"  Threshold: {anomaly.get('threshold', 'N/A')}")
        
        print("=" * 50)
    
    # Command handlers
    def cmd_help(self, args):
        print("""
\033[1;33mNeuralOS Shell Commands:\033[0m

\033[1;36mSystem:\033[0m
  help        - Show this help
  version     - Show version
  uptime      - Show uptime
  neofetch    - System info
  clear       - Clear screen
  status      - System dashboard

\033[1;36mFiles:\033[0m
  find <q>    - Semantic file search
  search <q>  - Search files

\033[1;36mPackages:\033[0m
  install <p> - Install package
  remove <p>  - Remove package
  recommend   - Suggest packages
  pkg-list    - List installed

\033[1;36mAI Services:\033[0m
  memory      - Memory report
  cache       - Cache stats
  predict     - Resource forecast
  diagnose    - System diagnosis
  anomaly     - Anomaly status

\033[1;36mShell:\033[0m
  !<cmd>      - Raw shell command
  cd <dir>    - Change directory
  exit        - Exit shell
""")
    
    def cmd_version(self, args):
        print("NeuralOS v0.1.0 (Synapse)")
        print("AI is the OS")
    
    def cmd_uptime(self, args):
        uptime = time.time() - self.node.start_time
        hours, remainder = divmod(int(uptime), 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"Uptime: {hours}h {minutes}m {seconds}s")
    
    def cmd_neofetch(self, args):
        print("""
\033[1;36m       _   _                 _     
      | \ | | __ _ _ __   __| |___ 
      |  \| |/ _` | '_ \ / _` / __|
      | |\  | (_| | | | | (_| \__ \\
      |_| \_|\__,_|_| |_|\__,_|___/
\033[0m
OS:       \033[1;32mNeuralOS\033[0m v0.1.0 Synapse
Kernel:   Python 3.x + C++ x86_64
Shell:    nos-shell
AI Mode:  \033[1;33m{}\033[0m
Packages: {} (installed)
Memory:   {}MB hot, {}x compression
""".format(
            self.node.context.current_mode,
            len(self.node.pkg_manager.installed),
            self.node.compressor.memory_report().get('hot_size_mb', 0),
            self.node.compressor.memory_report().get('compression_ratio', 0)
        ))
    
    def cmd_clear(self, args):
        os.system('clear')
    
    def cmd_status(self, args):
        result = self.node.run_command('status')
        self.render_result(result)
    
    def cmd_services(self, args):
        print("""
\033[1;33mNeuralOS Services:\033[0m
  ✅ nos-anomaly       - Anomaly detection
  ✅ nos-resource      - Resource prediction
  ✅ nos-cache        - Predictive cache
  ✅ nos-trainer       - Model warmup
""")
    
    def cmd_ps(self, args):
        print("PID     CMD")
        for pid, proc in self.node._processes.items():
            print(f"{pid:<8}{proc.name}")
    
    def cmd_exit(self, args):
        print("Goodbye!")
        sys.exit(0)


def main():
    import time
    shell = NOSShell()
    shell.run()


if __name__ == '__main__':
    main()
