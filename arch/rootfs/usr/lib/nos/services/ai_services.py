"""
NeuralOS AI Services
Semantic filesystem, anomaly detection, resource prediction, context engine.
"""

import numpy as np
import hashlib
import re
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from collections import deque, Counter
from datetime import datetime

from ..kernel.nn_core import MLP, Autoencoder


# ============================================================================
# Hash Embedding - Deterministic pseudo-embedding for text
# ============================================================================

def _hash_embed(text: str, dim: int = 64) -> np.ndarray:
    """Deterministic pseudo-embedding using MD5."""
    tokens = re.findall(r'\w+', text.lower())
    embedding = np.zeros(dim)
    
    for token in tokens:
        h = hashlib.md5(token.encode()).digest()
        h_int = int.from_bytes(h, 'big')
        for i in range(dim):
            bit = (h_int >> i) & 1
            embedding[i] += 1 if bit else -1
    
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    return embedding


# ============================================================================
# Semantic File System
# ============================================================================

@dataclass
class FileRecord:
    path: str
    content_hash: str
    embedding: np.ndarray
    tags: List[str]
    size_bytes: int
    last_modified: float
    access_count: int = 0
    last_accessed: float = 0.0


class SemanticFileSystem:
    """Semantic search over files using hash embeddings."""
    
    def __init__(self):
        self._index: Dict[str, FileRecord] = {}
        self._tag_index: Dict[str, List[str]] = {}
        self._access_log: List[Tuple[float, str]] = []
    
    def index_file(self, path: str, content_hint: str = '', 
                   tags: Optional[List[str]] = None, size_bytes: int = 0):
        """Index a file with semantic embedding."""
        if tags is None:
            tags = self._auto_tag(path, content_hint)
        
        text = f"{path.split('/')[-1]} {content_hint} {' '.join(tags)}"
        embedding = _hash_embed(text)
        content_hash = hashlib.sha256(content_hint.encode()).hexdigest()[:16]
        
        record = FileRecord(
            path=path,
            content_hash=content_hash,
            embedding=embedding,
            tags=tags,
            size_bytes=size_bytes,
            last_modified=time.time()
        )
        
        self._index[path] = record
        for tag in tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            self._tag_index[tag].append(path)
    
    def _auto_tag(self, path: str, hint: str) -> List[str]:
        """Auto-tag based on extension and content."""
        ext_map = {
            '.py': ['code', 'python'],
            '.js': ['code', 'javascript'],
            '.ts': ['code', 'typescript'],
            '.cpp': ['code', 'cpp'],
            '.h': ['code', 'cpp', 'header'],
            '.json': ['data', 'config'],
            '.yaml': ['config', 'yaml'],
            '.yml': ['config', 'yaml'],
            '.csv': ['data', 'spreadsheet'],
            '.pdf': ['document', 'pdf'],
            '.md': ['document', 'markdown'],
            '.txt': ['document', 'text'],
            '.log': ['log', 'system'],
            '.sh': ['script', 'shell'],
            '.bash': ['script', 'shell'],
            '.conf': ['config', 'system'],
            '.cfg': ['config', 'system'],
        }
        
        tags = []
        for ext, ext_tags in ext_map.items():
            if path.endswith(ext):
                tags.extend(ext_tags)
                break
        
        combined = f"{path} {hint}".lower()
        keyword_map = {
            'tax': 'finance',
            'readme': 'documentation',
            'config': 'config',
            'test': 'testing',
            'spec': 'testing',
        }
        for kw, tag in keyword_map.items():
            if kw in combined:
                tags.append(tag)
        
        return tags if tags else ['general']
    
    def semantic_search(self, query: str, top_k: int = 5,
                        tag_filter: Optional[str] = None) -> List[Tuple[float, FileRecord]]:
        """Search files by semantic similarity."""
        query_emb = _hash_embed(query)
        candidates = []
        
        for path, record in self._index.items():
            if tag_filter and tag_filter not in record.tags:
                continue
            
            score = float(np.dot(query_emb, record.embedding))
            
            # Recency boost
            age_days = (time.time() - record.last_modified) / 86400
            recency_boost = 0.05 * max(0, 1 - age_days / 30)
            score += recency_boost
            
            candidates.append((score, record))
        
        candidates.sort(key=lambda x: -x[0])
        return candidates[:top_k]
    
    def record_access(self, path: str):
        """Record file access for hot file tracking."""
        if path in self._index:
            self._index[path].access_count += 1
            self._index[path].last_accessed = time.time()
            self._access_log.append((time.time(), path))
    
    def hot_files(self, top_k: int = 10) -> List[FileRecord]:
        """Get most frequently accessed files."""
        sorted_files = sorted(
            self._index.values(), 
            key=lambda r: -r.access_count
        )
        return sorted_files[:top_k]
    
    def stats(self) -> Dict:
        return {
            'indexed_files': len(self._index),
            'unique_tags': len(self._tag_index),
            'total_size_mb': sum(r.size_bytes for r in self._index.values()) / 1e6
        }


# ============================================================================
# Anomaly Detector
# ============================================================================

class AnomalyDetector:
    """Autoencoder-based anomaly detection for system metrics."""
    
    def __init__(self, input_dim: int = 28, bottleneck: int = 4):
        self.input_dim = input_dim
        self.model = Autoencoder(input_dim, bottleneck)
        self.error_history: deque = deque(maxlen=200)
        self.training_count = 0
        self.threshold: Optional[float] = None
    
    def _build_feature_vector(self, metrics: Dict) -> np.ndarray:
        """Build 28-dim feature vector from system metrics."""
        # Syscall frequencies (20 dims) - normalized
        syscall_dims = ['read', 'write', 'open', 'close', 'mmap', 
                        'fork', 'exec', 'socket', 'connect', 'accept',
                        'bind', 'listen', 'mprotect', 'brk', 'ioctl',
                        'select', 'poll', 'epoll', 'stat', 'dup']
        syscalls = [metrics.get(s, 0) / 1000 for s in syscall_dims]
        
        # System metrics (8 dims)
        sys_metrics = [
            metrics.get('cpu_pct', 0) / 100,
            metrics.get('mem_pct', 0) / 100,
            metrics.get('net_bytes', 0) / 1e7,
            metrics.get('disk_ops', 0) / 1000,
            metrics.get('open_fds', 0) / 1024,
            metrics.get('thread_count', 0) / 200,
            metrics.get('ctx_switches', 0) / 1e4,
            metrics.get('uptime_s', 0) / 86400,
        ]
        
        return np.array(syscalls + sys_metrics, dtype=np.float32)
    
    def observe(self, metrics: Dict) -> Dict:
        """Observe system metrics, detect anomalies."""
        x = self._build_feature_vector(metrics).reshape(1, -1)
        error = self.model.reconstruction_error(x)[0]
        self.error_history.append(error)
        
        # Train periodically
        self.training_count += 1
        if self.training_count % 10 == 0 and len(self.error_history) > 20:
            self._train_batch()
        
        # Calculate threshold
        if len(self.error_history) > 50:
            errors = np.array(self.error_history)
            self.threshold = float(np.mean(errors) + 3 * np.std(errors))
        
        # Determine severity
        severity = 'normal'
        if self.threshold:
            if error > self.threshold * 2:
                severity = 'critical'
            elif error > self.threshold:
                severity = 'warning'
            elif error > self.threshold * 0.5:
                severity = 'elevated'
        
        return {
            'score': float(error),
            'threshold': self.threshold,
            'severity': severity,
            'is_anomaly': severity in ['warning', 'critical']
        }
    
    def _train_batch(self):
        """Train on recent error history."""
        if len(self.error_history) < 20:
            return
        
        # Synthesize training data from history
        errors = list(self.error_history)
        for _ in range(5):
            # Create synthetic samples near recent errors
            base = np.random.choice(errors)
            noise = np.random.randn(self.input_dim) * 0.01
            x = np.random.randn(1, self.input_dim) * 0.5 + 0.5
            self.model.train_step(x)
    
    def baseline_summary(self) -> Dict:
        return {
            'samples_observed': self.training_count,
            'threshold': self.threshold,
            'recent_error_mean': np.mean(self.error_history) if self.error_history else 0
        }


# ============================================================================
# Resource Predictor
# ============================================================================

class ResourcePredictor:
    """MLP-based CPU/memory usage forecasting."""
    
    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.cpu_history: deque = deque(maxlen=window_size)
        self.mem_history: deque = deque(maxlen=window_size)
        
        # CPU prediction model
        self.cpu_model = MLP([window_size, 32, 16, 5], ['relu', 'relu', 'linear'], lr=5e-4)
        # Memory prediction model
        self.mem_model = MLP([window_size, 32, 16, 5], ['relu', 'relu', 'linear'], lr=5e-4)
    
    def record(self, cpu_pct: float, mem_pct: float):
        """Record CPU and memory usage."""
        self.cpu_history.append(cpu_pct / 100)
        self.mem_history.append(mem_pct / 100)
    
    def predict(self) -> Dict:
        """Predict next 5 steps for CPU and memory."""
        if len(self.cpu_history) < self.window_size:
            return {'cpu_forecast': [], 'mem_forecast': [], 'spike_warning': False}
        
        # Train on sliding windows
        cpu_data = list(self.cpu_history)
        mem_data = list(self.mem_history)
        
        for i in range(len(cpu_data) - self.window_size):
            x = np.array(cpu_data[i:i+self.window_size]).reshape(1, -1)
            y = np.array(cpu_data[i+1:i+self.window_size+1]).reshape(1, -1)
            if y.shape[1] == self.window_size:
                self.cpu_model.train_step(x, y)
        
        for i in range(len(mem_data) - self.window_size):
            x = np.array(mem_data[i:i+self.window_size]).reshape(1, -1)
            y = np.array(mem_data[i+1:i+self.window_size+1]).reshape(1, -1)
            if y.shape[1] == self.window_size:
                self.mem_model.train_step(x, y)
        
        # Predict next 5 steps
        x_cpu = np.array(cpu_data[-self.window_size:]).reshape(1, -1)
        x_mem = np.array(mem_data[-self.window_size:]).reshape(1, -1)
        
        cpu_forecast = (self.cpu_model.predict(x_cpu)[0] * 100).tolist()
        mem_forecast = (self.mem_model.predict(x_mem)[0] * 100).tolist()
        
        spike_warning = any(c > 85 for c in cpu_forecast) or any(m > 90 for m in mem_forecast)
        
        return {
            'cpu_forecast': cpu_forecast,
            'mem_forecast': mem_forecast,
            'spike_warning': spike_warning,
            'recommend_action': self._recommend_action(cpu_forecast, mem_forecast)
        }
    
    def _recommend_action(self, cpu: List[float], mem: List[float]) -> Optional[str]:
        if any(c > 90 for c in cpu):
            return "Consider killing high-CPU processes or scaling horizontally"
        if any(m > 95 for m in mem):
            return "Memory pressure detected - consider compression or swap"
        return None


# ============================================================================
# Context Engine
# ============================================================================

class ContextEngine:
    """Detects current user activity mode."""
    
    MODES = ['coding', 'browsing', 'media', 'writing', 'gaming', 
             'sysadmin', 'idle', 'data_analysis', 'communication']
    
    def __init__(self):
        self.mode_scores: Dict[str, float] = {m: 0.0 for m in self.MODES}
        self.current_mode = 'idle'
        
        self.process_keywords = {
            'coding': ['python', 'node', 'gcc', 'vim', 'neovim', 'code', 'git', 'make', 'cargo', 'rustc'],
            'data_analysis': ['jupyter', 'pandas', 'numpy', 'matplotlib', 'sklearn', 'tensorflow', 'pytorch', 'R'],
            'sysadmin': ['systemctl', 'docker', 'kubectl', 'ansible', 'terraform', 'ssh', 'podman'],
            'browsing': ['firefox', 'chrome', 'chromium', 'brave', 'lynx'],
            'media': ['vlc', 'mpv', 'spotify', 'ffmpeg', 'audacity'],
            'gaming': ['steam', 'lutris', 'mango', 'gamescope'],
            'writing': ['libreoffice', 'latex', 'pandoc', 'typora', 'obsidian'],
            'communication': ['thunderbird', 'signal', 'discord', 'slack', 'teams'],
        }
        
        self.alpha = 0.2  # EMA blending factor
    
    def update(self, running_processes: List[str]):
        """Update mode scores based on running processes."""
        new_scores = {m: 0.0 for m in self.MODES}
        
        for proc in running_processes:
            proc_lower = proc.lower()
            for mode, keywords in self.process_keywords.items():
                for kw in keywords:
                    if kw in proc_lower:
                        new_scores[mode] += 1.0
        
        # Normalize
        total = sum(new_scores.values()) + 1e-8
        for mode in self.MODES:
            new_scores[mode] /= total
        
        # EMA blend
        for mode in self.MODES:
            self.mode_scores[mode] = (
                self.alpha * new_scores[mode] + 
                (1 - self.alpha) * self.mode_scores[mode]
            )
        
        self.current_mode = max(self.MODES, key=lambda m: self.mode_scores[m])
    
    def suggested_prefetch_tags(self) -> List[str]:
        """Suggest file tags to prefetch based on current mode."""
        mode_tags = {
            'coding': ['code', 'python', 'config'],
            'data_analysis': ['data', 'spreadsheet', 'document'],
            'sysadmin': ['config', 'log', 'script'],
            'browsing': ['document'],
            'media': ['media', 'document'],
            'writing': ['document', 'markdown'],
            'communication': ['document'],
            'idle': [],
            'gaming': [],
        }
        return mode_tags.get(self.current_mode, [])
    
    def summary(self) -> Dict:
        return {
            'current_mode': self.current_mode,
            'mode_scores': self.mode_scores.copy()
        }
