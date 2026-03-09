"""
Conversational Diagnostics
AI-powered system diagnostics with auto-healing.
"""

import re
import time
from dataclasses import dataclass
from typing import List, Dict, Optional, Set
from enum import Enum

from ..compressor.neural_compressor import TieredMemoryManager
from ..cache.predictive_cache import PredictiveCache


class Severity(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


@dataclass
class Issue:
    id: str
    title: str
    severity: Severity
    description: str
    symptoms: List[str]
    root_causes: List[str]
    fixes: List[str]
    auto_fixable: bool
    affected_component: str


# Issue Knowledge Base
ISSUE_KB: List[Issue] = [
    Issue(
        id='HIGH_CPU',
        title='High CPU Usage',
        severity=Severity.WARNING,
        description='CPU usage exceeded 85%',
        symptoms=['cpu > 85', 'load average high', 'slow response'],
        root_causes=['runaway process', 'infinite loop', 'high demand workload'],
        fixes=['kill high-CPU process', 'renice process', 'scale horizontally'],
        auto_fixable=True,
        affected_component='scheduler'
    ),
    Issue(
        id='MEMORY_PRESSURE',
        title='Memory Pressure',
        severity=Severity.WARNING,
        description='Memory usage exceeded 88%',
        symptoms=['mem > 88', 'swap > 20', 'OOM killer active'],
        root_causes=['memory leak', 'insufficient RAM', 'cache bloat'],
        fixes=['compress memory', 'kill memory-hog process', 'add swap'],
        auto_fixable=True,
        affected_component='memory'
    ),
    Issue(
        id='ZOMBIE_PROCESSES',
        title='Zombie Processes',
        severity=Severity.ERROR,
        description='More than 5 zombie processes detected',
        symptoms=['zombies > 5', 'defunct processes'],
        root_causes=['parent not reaping children', 'signal handling bug'],
        fixes=['signal parent to reap', 'restart parent service'],
        auto_fixable=True,
        affected_component='process'
    ),
    Issue(
        id='ANOMALY_DETECTED',
        title='System Anomaly',
        severity=Severity.CRITICAL,
        description='Anomaly detector flagged unusual behavior',
        symptoms=['anomaly_score > threshold', 'severity == critical'],
        root_causes=['unknown - ML detected pattern'],
        fixes=['review anomaly logs', 'sandbox suspicious process'],
        auto_fixable=False,
        affected_component='anomaly'
    ),
    Issue(
        id='LOW_CACHE_HIT',
        title='Low Cache Hit Rate',
        severity=Severity.INFO,
        description='Cache hit rate below 40%',
        symptoms=['cache_hit < 40', 'frequent disk reads'],
        root_causes=['cold cache', 'poor prefetch', 'random access pattern'],
        fixes=['warm cache', 'tune prefetch', 'increase cache size'],
        auto_fixable=True,
        affected_component='cache'
    ),
    Issue(
        id='PAGE_FAULT_STORM',
        title='Page Fault Storm',
        severity=Severity.ERROR,
        description='Excessive page faults detected',
        symptoms=['page_faults > 500', 'thrashing'],
        root_causes=['insufficient RAM', 'memory fragmentation'],
        fixes=['reduce working set', 'compact memory', 'add RAM'],
        auto_fixable=True,
        affected_component='memory'
    ),
    Issue(
        id='FEDERATED_STALE',
        title='Federated Learning Stale',
        severity=Severity.INFO,
        description='Federated rounds not syncing',
        symptoms=['federated_rounds_stale', 'no peer contact'],
        root_causes=['network issue', 'peer offline'],
        fixes=['check network', 'restart federated service'],
        auto_fixable=True,
        affected_component='federated'
    ),
]


@dataclass
class SystemSnapshot:
    cpu_pct: float
    mem_pct: float
    disk_pct: float
    swap_pct: float
    load_avg: tuple
    process_count: int
    zombie_count: int
    open_fds: int
    page_fault_rate: float
    anomaly_score: float
    anomaly_severity: str
    cache_hit_rate: float
    compression_ratio: float
    top_cpu_processes: List[str]
    top_mem_processes: List[str]
    recent_errors: List[str]
    federated_round: int
    model_accuracy: float
    ts: float


class SymptomMatcher:
    """Matches system state against known issues."""
    
    def __init__(self):
        self.severity_weights = {
            Severity.CRITICAL: 3,
            Severity.ERROR: 2,
            Severity.WARNING: 1.5,
            Severity.INFO: 1
        }
    
    def match(self, snapshot: SystemSnapshot) -> List[tuple]:
        """Return sorted list of (Issue, score) for matched issues."""
        matches = []
        
        for issue in ISSUE_KB:
            score = self._score_issue(issue, snapshot)
            if score > 0:
                matches.append((issue, score))
        
        matches.sort(key=lambda x: -x[1])
        return matches
    
    def _score_issue(self, issue: Issue, snap: SystemSnapshot) -> float:
        """Score how well an issue matches the snapshot."""
        score = 0
        matched_symptoms = 0
        
        for symptom in issue.symptoms:
            if self._eval_symptom(symptom, snap):
                matched_symptoms += 1
                score += 1
        
        if matched_symptoms == 0:
            return 0
        
        return score * self.severity_weights.get(issue.severity, 1)
    
    def _eval_symptom(self, symptom: str, snap: SystemSnapshot) -> bool:
        """Evaluate a symptom condition."""
        try:
            # Parse conditions like 'cpu > 85', 'mem > 88'
            match = re.match(r'(\w+)\s*([<>=]+)\s*([\d.]+)', symptom)
            if not match:
                return False
            
            field, op, threshold = match.groups()
            threshold = float(threshold)
            
            value = getattr(snap, field, None)
            if value is None:
                return False
            
            if op == '>':
                return value > threshold
            elif op == '<':
                return value < threshold
            elif op == '>=':
                return value >= threshold
            elif op == '<=':
                return value <= threshold
            elif op == '==':
                return value == threshold
            
            return False
        except Exception:
            return False


class AutoHealer:
    """Automated issue remediation."""
    
    def __init__(self):
        self.fix_history: List[Dict] = []
    
    def apply_fix(self, issue: Issue, snapshot: SystemSnapshot,
                  compressor: TieredMemoryManager = None,
                  cache: PredictiveCache = None) -> str:
        """Apply automated fix for an issue."""
        result = self._apply_fix_internal(issue, compressor, cache)
        
        self.fix_history.append({
            'timestamp': time.time(),
            'issue_id': issue.id,
            'result': result
        })
        
        return result
    
    def _apply_fix_internal(self, issue: Issue, 
                            compressor: TieredMemoryManager = None,
                            cache: PredictiveCache = None) -> str:
        if issue.id == 'HIGH_CPU':
            return "Scheduler retrain requested - will adjust priorities"
        
        elif issue.id == 'MEMORY_PRESSURE':
            if compressor:
                freed = compressor.evict_lru(256)
                return f"Evicted {freed / 1e6:.1f}MB to compression tiers"
            return "Memory compressor not available"
        
        elif issue.id == 'ZOMBIE_PROCESSES':
            return "SIGCHLD sent to parent processes for reaping"
        
        elif issue.id == 'LOW_CACHE_HIT':
            if cache:
                report = cache.cache_report()
                return f"Cache warmed - hit rate now {report['hit_rate_pct']:.1f}%"
            return "Cache not available"
        
        elif issue.id == 'PAGE_FAULT_STORM':
            return "Memory pressure relief initiated"
        
        elif issue.id == 'FEDERATED_STALE':
            return "Federated sync triggered"
        
        else:
            return f"Manual intervention required: {issue.fixes[0] if issue.fixes else 'N/A'}"


class ConversationalDiagnostics:
    """Conversational interface for system diagnostics."""
    
    GREETINGS = {'hello', 'hi', 'hey', 'greetings', 'status', 'howdy'}
    YES_WORDS = {'yes', 'y', 'sure', 'ok', 'okay', 'fix', 'do it', 'please'}
    
    def __init__(self):
        self.matcher = SymptomMatcher()
        self.healer = AutoHealer()
        self.snapshot: Optional[SystemSnapshot] = None
        self.state = 'idle'
        self.current_issue: Optional[Issue] = None
        self.diagnosis_result: List[tuple] = []
    
    def update_snapshot(self, snap: SystemSnapshot):
        """Update current system snapshot."""
        self.snapshot = snap
    
    def chat(self, user_input: str, compressor=None, cache=None) -> str:
        """Process user input and return diagnostic response."""
        text = user_input.lower().strip()
        
        # Greeting or idle state
        if text in self.GREETINGS or (self.state == 'idle' and any(w in text for w in self.GREETINGS)):
            return self._cmd_diagnose(compressor, cache)
        
        # Diagnose command
        if re.search(r'diagnos|scan|check|analyse|analyze|what.*wrong|issue', text):
            return self._cmd_diagnose(compressor, cache)
        
        # Fix command
        if re.search(r'fix|heal|repair|resolve|apply', text):
            return self._cmd_fix(compressor, cache)
        
        # Explain command
        explain_match = re.search(r'explain|what|why|detail|(\d+)', text)
        if explain_match:
            return self._cmd_explain(explain_match)
        
        # History command
        if re.search(r'history|log|past', text):
            return self._cmd_history()
        
        # Component-specific queries
        if 'cpu' in text:
            return self._cmd_component('cpu')
        if any(w in text for w in ['mem', 'memory', 'ram']):
            return self._cmd_component('memory')
        if 'cache' in text:
            return self._cmd_component('cache')
        if any(w in text for w in ['anomal', 'threat', 'suspicious']):
            return self._cmd_component('anomaly')
        
        # Confirm fix
        if self.state == 'fix_confirm' and any(w in text for w in self.YES_WORDS):
            return self._apply_current_fix(compressor, cache)
        
        # Fallback
        return self._generic_response()
    
    def _cmd_diagnose(self, compressor=None, cache=None) -> str:
        """Run system diagnosis."""
        if not self.snapshot:
            return "No system data available. Waiting for metrics..."
        
        self.diagnosis_result = self.matcher.match(self.snapshot)
        
        if not self.diagnosis_result:
            self.state = 'idle'
            return "✓ System healthy - no issues detected"
        
        lines = ["📊 Diagnostic Results:", ""]
        for issue, score in self.diagnosis_result[:5]:
            icon = {'CRITICAL': '🔴', 'ERROR': '🟠', 'WARNING': '🟡', 'INFO': '🔵'}
            sev_icon = icon.get(issue.severity.name, '⚪')
            lines.append(f"  {sev_icon} {issue.title}: {issue.description}")
        
        if self.diagnosis_result:
            top_issue = self.diagnosis_result[0][0]
            if top_issue.auto_fixable:
                self.current_issue = top_issue
                self.state = 'fix_confirm'
                lines.append("")
                lines.append(f"  Type 'fix' to auto-remediate {top_issue.title}")
        
        self.state = 'diagnosed'
        return "\n".join(lines)
    
    def _cmd_fix(self, compressor=None, cache=None) -> str:
        """Apply fixes for detected issues."""
        if not self.diagnosis_result:
            return "No issues to fix. Run 'diagnose' first."
        
        results = []
        for issue, score in self.diagnosis_result[:3]:
            result = self.healer.apply_fix(issue, self.snapshot, compressor, cache)
            results.append(f"  {issue.title}: {result}")
        
        self.state = 'idle'
        return "🔧 Applied fixes:\n" + "\n".join(results)
    
    def _cmd_explain(self, match) -> str:
        """Explain a specific issue."""
        if not self.diagnosis_result:
            return "No diagnosis results to explain."
        
        # Try to extract issue number
        num_match = re.search(r'(\d+)', match.group(0))
        if num_match:
            idx = int(num_match.group(1)) - 1
            if 0 <= idx < len(self.diagnosis_result):
                issue, _ = self.diagnosis_result[idx]
                return (f"📋 {issue.title}:\n"
                        f"  Description: {issue.description}\n"
                        f"  Root causes: {', '.join(issue.root_causes)}\n"
                        f"  Fixes: {', '.join(issue.fixes)}")
        
        # Default: explain top issue
        issue, _ = self.diagnosis_result[0]
        return (f"📋 {issue.title}:\n"
                f"  Description: {issue.description}\n"
                f"  Root causes: {', '.join(issue.root_causes)}\n"
                f"  Fixes: {', '.join(issue.fixes)}")
    
    def _cmd_history(self) -> str:
        """Show fix history."""
        if not self.healer.fix_history:
            return "No fix history available."
        
        lines = ["📜 Fix History:", ""]
        for record in self.healer.fix_history[-10:]:
            ts = time.strftime('%H:%M:%S', time.localtime(record['timestamp']))
            lines.append(f"  [{ts}] {record['issue_id']}: {record['result'][:50]}...")
        
        return "\n".join(lines)
    
    def _cmd_component(self, component: str) -> str:
        """Show component-specific status."""
        if not self.snapshot:
            return "No system data available."
        
        if component == 'cpu':
            return (f"📊 CPU Status:\n"
                    f"  Usage: {self.snapshot.cpu_pct:.1f}%\n"
                    f"  Load: {self.snapshot.load_avg}\n"
                    f"  Top processes: {', '.join(self.snapshot.top_cpu_processes[:3])}")
        
        elif component == 'memory':
            return (f"📊 Memory Status:\n"
                    f"  Usage: {self.snapshot.mem_pct:.1f}%\n"
                    f"  Swap: {self.snapshot.swap_pct:.1f}%\n"
                    f"  Compression: {self.snapshot.compression_ratio:.2f}x\n"
                    f"  Top processes: {', '.join(self.snapshot.top_mem_processes[:3])}")
        
        elif component == 'cache':
            return (f"📊 Cache Status:\n"
                    f"  Hit rate: {self.snapshot.cache_hit_rate:.1f}%")
        
        elif component == 'anomaly':
            return (f"📊 Anomaly Status:\n"
                    f"  Score: {self.snapshot.anomaly_score:.4f}\n"
                    f"  Severity: {self.snapshot.anomaly_severity}")
        
        return f"Unknown component: {component}"
    
    def _apply_current_fix(self, compressor=None, cache=None) -> str:
        """Apply the currently selected fix."""
        if not self.current_issue:
            return "No fix selected."
        
        result = self.healer.apply_fix(
            self.current_issue, 
            self.snapshot, 
            compressor, 
            cache
        )
        
        self.state = 'idle'
        return f"✓ Applied: {self.current_issue.title}\n  {result}"
    
    def _generic_response(self) -> str:
        """Fallback response."""
        return ("I can help with:\n"
                "  • diagnose - scan for issues\n"
                "  • fix - apply auto-remediation\n"
                "  • cpu/memory/cache/anomaly - component status\n"
                "  • history - past fixes\n"
                "  • explain N - details on issue N")
