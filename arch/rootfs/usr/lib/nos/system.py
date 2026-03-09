"""
NeuralOS System - Main Integration Layer
NeuralNode: The brain of NeuralOS
"""

import time
import subprocess
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .kernel.nn_core import MLP
from .services.ai_services import (
    SemanticFileSystem, AnomalyDetector,
    ResourcePredictor, ContextEngine
)
from .compressor.neural_compressor import TieredMemoryManager
from .cache.predictive_cache import PredictiveCache
from .diagnostics.conversational_diagnostics import (
    ConversationalDiagnostics, SystemSnapshot
)
from .pkg_manager.neural_pkg_manager import NeuralPkgManager


@dataclass
class ProcessInfo:
    pid: int
    name: str
    cpu_pct: float
    mem_pct: float
    status: str


class NeuralNode:
    """
    Main NeuralOS integration class.
    All AI subsystems route through this node.
    """
    
    def __init__(self, node_id: str = 'primary'):
        self.node_id = node_id
        self.start_time = time.time()
        
        # Initialize all AI subsystems
        self.fs = SemanticFileSystem()
        self.anomaly_detector = AnomalyDetector()
        self.resource_predictor = ResourcePredictor()
        self.context = ContextEngine()
        self.compressor = TieredMemoryManager()
        self.cache = PredictiveCache()
        self.diagnostics = ConversationalDiagnostics()
        self.pkg_manager = NeuralPkgManager()
        
        # Bootstrap filesystem with sample files
        self._bootstrap_fs()
        
        # Process tracking
        self._processes: Dict[int, ProcessInfo] = {}
        self._next_pid = 1000
        self._event_log: List[Dict] = []
    
    def _bootstrap_fs(self):
        """Index sample files for demonstration."""
        sample_files = [
            ('/home/user/project/main.py', 'python code application', ['code', 'python'], 5000),
            ('/home/user/docs/report.pdf', 'business report finance', ['document', 'pdf'], 500000),
            ('/etc/app/config.yaml', 'application configuration', ['config', 'yaml'], 2000),
            ('/var/log/system.log', 'system logs error warning', ['log', 'system'], 100000),
            ('/home/user/data/dataset.csv', 'data analysis spreadsheet', ['data', 'csv'], 2000000),
            ('/home/user/.bashrc', 'shell configuration script', ['script', 'shell'], 3000),
            ('/home/user/notes/todo.md', 'notes todo list', ['document', 'markdown'], 1500),
        ]
        
        for path, hint, tags, size in sample_files:
            self.fs.index_file(path, hint, tags, size)
    
    def run_command(self, natural_cmd: str) -> Dict:
        """
        Process natural language command and route to appropriate subsystem.
        """
        cmd = natural_cmd.lower().strip()
        
        # 1. Diagnostic commands
        if any(kw in cmd for kw in ['anomaly', 'diagnose', 'fix', 'heal', 'why', 'what is wrong']):
            result = self.diagnostics.chat(natural_cmd, self.compressor, self.cache)
            return {'type': 'diagnostic', 'message': result}
        
        # 2. File search commands
        if any(kw in cmd for kw in ['find', 'search', 'locate', 'where is']):
            query = cmd
            for prefix in ['find ', 'search ', 'locate ', 'where is ']:
                query = query.replace(prefix, '')
            results = self.fs.semantic_search(query.strip(), top_k=10)
            return {
                'type': 'file_search',
                'query': query,
                'results': [(score, r.path, r.tags) for score, r in results]
            }
        
        # 3. Package install
        if cmd.startswith('install '):
            pkg_name = cmd.replace('install ', '').strip()
            result = self.pkg_manager.install(pkg_name)
            return {
                'type': 'pkg_install',
                'package': pkg_name,
                'result': result
            }
        
        # 4. Package remove
        if cmd.startswith('remove '):
            pkg_name = cmd.replace('remove ', '').strip()
            result = self.pkg_manager.remove(pkg_name)
            return {
                'type': 'pkg_remove',
                'package': pkg_name,
                'result': result
            }
        
        # 5. Package recommendations
        if any(kw in cmd for kw in ['recommend', 'suggest']):
            recs = self.pkg_manager.recommend(self.context.current_mode, top_k=10)
            return {
                'type': 'pkg_recommend',
                'mode': self.context.current_mode,
                'recommendations': recs
            }
        
        # 6. Package search
        if 'pkg search' in cmd or 'search package' in cmd:
            query = cmd.replace('pkg search', '').replace('search package', '').strip()
            results = self.pkg_manager.search(query)
            return {
                'type': 'pkg_search',
                'query': query,
                'results': results
            }
        
        # 7. Memory/compression commands
        if any(kw in cmd for kw in ['memory', 'compress', 'ram']):
            report = self.compressor.memory_report()
            return {
                'type': 'memory_report',
                'report': report
            }
        
        # 8. Cache commands
        if 'cache' in cmd:
            report = self.cache.cache_report()
            return {
                'type': 'cache_report',
                'report': report
            }
        
        # 9. Resource prediction
        if any(kw in cmd for kw in ['predict', 'forecast']):
            forecast = self.resource_predictor.predict()
            return {
                'type': 'resource_forecast',
                'forecast': forecast
            }
        
        # 10. Status/dashboard
        if any(kw in cmd for kw in ['status', 'dashboard', 'overview']):
            return {'type': 'dashboard', 'data': self.dashboard()}
        
        # 11. Process spawning
        if cmd.startswith('spawn '):
            proc_cmd = cmd.replace('spawn ', '').strip()
            return self._spawn_process(proc_cmd)
        
        # Unknown command
        return {
            'type': 'unknown',
            'hint': f"Unknown command: {natural_cmd}",
            'suggestions': [
                'diagnose - scan for issues',
                'find <query> - search files',
                'install <pkg> - install package',
                'memory - memory report',
                'cache - cache statistics',
                'predict - resource forecast',
                'status - system dashboard'
            ]
        }
    
    def simulate_activity(self, n_ticks: int = 20):
        """
        Simulate system activity for warming up AI models.
        Generates synthetic CPU/memory usage patterns.
        """
        import math
        
        for tick in range(n_ticks):
            # Sinusoidal CPU pattern with noise
            base_cpu = 30 + 20 * math.sin(tick * 0.5)
            cpu = max(0, min(100, base_cpu + (hash(str(tick)) % 20) - 10))
            
            # Memory slowly increases
            mem = min(95, 40 + tick * 2 + (hash(str(tick + 100)) % 10))
            
            # Record for prediction
            self.resource_predictor.record(cpu, mem)
            
            # Anomaly detection observation
            metrics = {
                'cpu_pct': cpu,
                'mem_pct': mem,
                'read': hash(str(tick)) % 100,
                'write': hash(str(tick + 50)) % 50,
            }
            anomaly_result = self.anomaly_detector.observe(metrics)
            
            # Context engine update
            processes = ['python', 'vim', 'bash'] if tick % 3 == 0 else ['firefox', 'chrome']
            self.context.update(processes)
            
            # File access simulation
            if tick % 5 == 0:
                self.fs.record_access('/home/user/project/main.py')
                self.cache.get('/home/user/project/main.py')
            
            # Update diagnostics snapshot
            self.diagnostics.update_snapshot(SystemSnapshot(
                cpu_pct=cpu,
                mem_pct=mem,
                disk_pct=30 + tick % 20,
                swap_pct=5 + tick % 10,
                load_avg=(cpu/25, cpu/50, cpu/100),
                process_count=50 + tick,
                zombie_count=hash(str(tick)) % 3,
                open_fds=500 + tick * 10,
                page_fault_rate=hash(str(tick)) % 100,
                anomaly_score=anomaly_result['score'],
                anomaly_severity=anomaly_result['severity'],
                cache_hit_rate=60 + tick % 30,
                compression_ratio=2.0 + tick % 3,
                top_cpu_processes=['python', 'chrome', 'node'],
                top_mem_processes=['firefox', 'java', 'code'],
                recent_errors=[],
                federated_round=tick // 10,
                model_accuracy=0.85 + tick * 0.01,
                ts=time.time()
            ))
    
    def dashboard(self) -> Dict:
        """Generate comprehensive system dashboard."""
        mem_report = self.compressor.memory_report()
        cache_report = self.cache.cache_report()
        forecast = self.resource_predictor.predict()
        context_summary = self.context.summary()
        pkg_stats = self.pkg_manager.stats()
        anomaly_summary = self.anomaly_detector.baseline_summary()
        fs_stats = self.fs.stats()
        
        return {
            'node_id': self.node_id,
            'uptime_seconds': time.time() - self.start_time,
            'current_mode': context_summary['current_mode'],
            'memory': mem_report,
            'cache': cache_report,
            'forecast': forecast,
            'context': context_summary,
            'packages': pkg_stats,
            'anomaly': anomaly_summary,
            'filesystem': fs_stats,
            'event_count': len(self._event_log)
        }
    
    def _spawn_process(self, cmd: str) -> Dict:
        """Spawn a simulated process."""
        pid = self._next_pid
        self._next_pid += 1
        
        self._processes[pid] = ProcessInfo(
            pid=pid,
            name=cmd,
            cpu_pct=0.0,
            mem_pct=0.0,
            status='running'
        )
        
        self._event_log.append({
            'ts': time.time(),
            'event': 'process_spawn',
            'pid': pid,
            'cmd': cmd
        })
        
        return {
            'type': 'process_spawn',
            'pid': pid,
            'cmd': cmd,
            'status': 'running'
        }
    
    def kill_process(self, pid: int) -> Dict:
        """Kill a simulated process."""
        if pid not in self._processes:
            return {'error': f'Process {pid} not found'}
        
        proc = self._processes.pop(pid)
        self._event_log.append({
            'ts': time.time(),
            'event': 'process_kill',
            'pid': pid
        })
        
        return {
            'type': 'process_kill',
            'pid': pid,
            'name': proc.name,
            'status': 'killed'
        }
    
    def event_log(self, limit: int = 50) -> List[Dict]:
        """Get recent events."""
        return self._event_log[-limit:]


class NeuralOSNetwork:
    """
    Network of NeuralNodes for federated learning.
    """
    
    def __init__(self):
        self.nodes: List[NeuralNode] = []
    
    def add_node(self, node: NeuralNode):
        """Add a node to the network."""
        self.nodes.append(node)
    
    def run_full_simulation(self, rounds: int = 5, ticks_per_round: int = 20):
        """Run simulation across all nodes."""
        for round_num in range(rounds):
            print(f"\n=== Federated Round {round_num + 1}/{rounds} ===")
            
            for node in self.nodes:
                node.simulate_activity(ticks_per_round)
                dashboard = node.dashboard()
                print(f"  Node '{node.node_id}': "
                      f"mode={dashboard['current_mode']}, "
                      f"mem_ratio={dashboard['memory']['compression_ratio']:.2f}x")
            
            # Federated gradient exchange would happen here
            # See §8.4 for full implementation
    
    def federated_average(self):
        """Compute federated average of model weights."""
        # Stub - real implementation in federated_learning.py
        pass


# Convenience function for creating a node
def create_node(node_id: str = 'primary') -> NeuralNode:
    """Create and initialize a NeuralNode."""
    node = NeuralNode(node_id)
    node.simulate_activity(10)  # Warm up models
    return node
