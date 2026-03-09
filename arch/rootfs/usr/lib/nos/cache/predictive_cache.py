"""
Predictive File Cache
Markov access prediction, time patterns, LRU-K eviction.
"""

import numpy as np
import zlib
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import deque, Counter, defaultdict
from datetime import datetime


@dataclass
class CacheEntry:
    path: str
    data: bytes
    compressed: bool = False
    original_size: int = 0
    stored_size: int = 0
    access_times: List[float] = field(default_factory=list)
    prefetch_score: float = 0.0
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if len(self.access_times) > 20:
            self.access_times = self.access_times[-20:]
    
    @property
    def access_count(self) -> int:
        return len(self.access_times)
    
    @property
    def last_accessed(self) -> float:
        return self.access_times[-1] if self.access_times else 0.0
    
    @property
    def access_frequency(self) -> float:
        """Accesses per hour over last 24h window."""
        if not self.access_times:
            return 0.0
        now = time.time()
        recent = [t for t in self.access_times if now - t < 86400]
        if len(recent) < 2:
            return 0.0
        span_hours = (now - min(recent)) / 3600
        return len(recent) / max(span_hours, 1)


class MarkovAccessPredictor:
    """Order-2 Markov chain for file access prediction."""
    
    def __init__(self):
        self._transitions: defaultdict = defaultdict(Counter)
        self._history: deque = deque(maxlen=3)
    
    def record_access(self, path: str):
        """Record file access for Markov prediction."""
        self._history.append(path)
        
        if len(self._history) >= 3:
            state = (self._history[-3], self._history[-2])
            next_file = self._history[-1]
            self._transitions[state][next_file] += 1
    
    def predict_next(self, top_k: int = 5) -> List[Tuple[str, float]]:
        """Predict next accessed files."""
        if len(self._history) < 2:
            return []
        
        state = (self._history[-2], self._history[-1])
        
        # Try order-2 first
        if state in self._transitions:
            trans = self._transitions[state]
            total = sum(trans.values())
            predictions = [
                (path, count / total) 
                for path, count in trans.most_common(top_k)
            ]
            if predictions:
                return predictions
        
        # Fallback to order-1
        if len(self._history) >= 1:
            state_1 = self._history[-1]
            trans_1 = Counter()
            for (s1, s2), counts in self._transitions.items():
                if s2 == state_1:
                    trans_1.update(counts)
            
            if trans_1:
                total = sum(trans_1.values())
                return [
                    (path, count / total)
                    for path, count in trans_1.most_common(top_k)
                ]
        
        return []
    
    def _prune(self):
        """Remove low-count states."""
        if len(self._transitions) > 2000:
            to_remove = [
                state for state, counts in self._transitions.items()
                if sum(counts.values()) < 2
            ]
            for state in to_remove:
                del self._transitions[state]


class TimePatternModel:
    """Time-based access pattern prediction."""
    
    def __init__(self):
        self._hourly: Counter = Counter()
        self._day_buckets: Counter = Counter()
        self._history: Dict[str, List[float]] = defaultdict(list)
    
    def record(self, path: str, ts: Optional[float] = None):
        """Record access timestamp."""
        ts = ts or time.time()
        hour = datetime.fromtimestamp(ts).hour
        day = datetime.fromtimestamp(ts).weekday()
        
        self._hourly[hour] += 1
        self._day_buckets[day] += 1
        self._history[path].append(ts)
    
    def predict_for_hour(self, hour: int, top_k: int = 10) -> List[str]:
        """Predict files accessed during given hour."""
        # Weight by hourly pattern
        hour_weight = self._hourly.get(hour, 0) + 1
        
        candidates = []
        for path, times in self._history.items():
            # Count accesses at this hour
            hour_accesses = sum(
                1 for t in times 
                if datetime.fromtimestamp(t).hour == hour
            )
            score = hour_accesses * hour_weight
            if score > 0:
                candidates.append((path, score))
        
        candidates.sort(key=lambda x: -x[1])
        return [p for p, _ in candidates[:top_k]]
    
    def predict_next_hour(self, top_k: int = 10) -> List[str]:
        """Predict files for next hour."""
        next_hour = (datetime.now().hour + 1) % 24
        return self.predict_for_hour(next_hour, top_k)
    
    def predict_now(self, top_k: int = 10) -> List[str]:
        """Predict files for current hour."""
        return self.predict_for_hour(datetime.now().hour, top_k)


class LRUKEviction:
    """LRU-K eviction policy (K=2)."""
    
    def __init__(self, k: int = 2):
        self.k = k
        self._access_history: Dict[str, deque] = {}
    
    def record_access(self, path: str):
        """Record access for LRU-K tracking."""
        if path not in self._access_history:
            self._access_history[path] = deque(maxlen=self.k)
        self._access_history[path].append(time.time())
    
    def eviction_candidate(self, candidates: List[str]) -> Optional[str]:
        """Find best eviction candidate by K-th access time."""
        if not candidates:
            return None
        
        def kth_time(path: str) -> float:
            history = self._access_history.get(path, deque())
            if len(history) < self.k:
                return 0.0  # Evict first
            return history[0]  # K-th access time
        
        # Evict oldest K-th access
        return min(candidates, key=kth_time)


class PredictiveCache:
    """AI-driven predictive file cache."""
    
    def __init__(self, max_size_mb: int = 256):
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size = max_size_mb * 1024 * 1024
        
        self._markov = MarkovAccessPredictor()
        self._time_model = TimePatternModel()
        self._lru_k = LRUKEviction(k=2)
        
        self._hits = 0
        self._misses = 0
        self._prefetch_hits = 0
        self._evictions = 0
        
        self._prefetch_set: set = set()
        self._prefetch_queue: List[Tuple[float, str]] = []
    
    def get(self, path: str) -> Optional[bytes]:
        """Get cached data, update predictors."""
        self._markov.record_access(path)
        self._time_model.record(path)
        self._lru_k.record_access(path)
        
        if path in self._cache:
            entry = self._cache[path]
            entry.access_times.append(time.time())
            
            if path in self._prefetch_set:
                self._prefetch_hits += 1
                self._prefetch_set.discard(path)
            
            self._hits += 1
            
            if entry.compressed:
                return zlib.decompress(entry.data)
            return entry.data
        
        self._misses += 1
        self._trigger_prefetch()
        return None
    
    def put(self, path: str, data: bytes, 
            tags: Optional[List[str]] = None,
            prefetch_score: float = 0.5):
        """Cache data with optional compression."""
        # Compress if beneficial
        compressed = False
        stored_data = data
        
        if len(data) > 512:
            comp = zlib.compress(data, level=1)
            if len(comp) < len(data) * 0.9:
                compressed = True
                stored_data = comp
        
        # Evict if needed
        current_size = sum(e.stored_size for e in self._cache.values())
        while current_size + len(stored_data) > self._max_size and self._cache:
            self._evict_one()
        
        entry = CacheEntry(
            path=path,
            data=stored_data,
            compressed=compressed,
            original_size=len(data),
            stored_size=len(stored_data),
            access_times=[time.time()],
            prefetch_score=prefetch_score,
            tags=tags or []
        )
        
        self._cache[path] = entry
    
    def _evict_one(self):
        """Evict one cache entry using LRU-K."""
        if not self._cache:
            return
        
        candidates = list(self._cache.keys())
        victim = self._lru_k.eviction_candidate(candidates)
        
        if victim and victim in self._cache:
            del self._cache[victim]
            self._evictions += 1
    
    def _trigger_prefetch(self):
        """Queue predicted files for prefetch."""
        predictions = self._markov.predict_next(top_k=5)
        time_preds = self._time_model.predict_now(top_k=3)
        
        for path, score in predictions:
            if path not in self._cache:
                self._prefetch_set.add(path)
                self._prefetch_queue.append((score, path))
        
        for path in time_preds:
            if path not in self._cache:
                self._prefetch_set.add(path)
    
    def warm_from_time_model(self, file_loader):
        """Warm cache using time-based predictions."""
        predictions = self._time_model.predict_next_hour(top_k=15)
        for path in predictions:
            if path not in self._cache:
                try:
                    data = file_loader(path)
                    self.put(path, data, prefetch_score=0.7)
                except Exception:
                    pass
    
    def cache_report(self) -> Dict:
        """Generate cache statistics report."""
        total_size = sum(e.stored_size for e in self._cache.values())
        original_size = sum(e.original_size for e in self._cache.values())
        
        total_requests = self._hits + self._misses
        hit_rate = self._hits / max(total_requests, 1) * 100
        prefetch_rate = self._prefetch_hits / max(self._hits, 1) * 100
        
        return {
            'cached_files': len(self._cache),
            'cache_size_mb': total_size / 1e6,
            'max_size_mb': self._max_size / 1e6,
            'utilization_pct': total_size / self._max_size * 100,
            'hit_rate_pct': hit_rate,
            'prefetch_hit_rate_pct': prefetch_rate,
            'evictions': self._evictions,
            'compression_savings_mb': (original_size - total_size) / 1e6,
            'prefetch_queue_depth': len(self._prefetch_queue)
        }
