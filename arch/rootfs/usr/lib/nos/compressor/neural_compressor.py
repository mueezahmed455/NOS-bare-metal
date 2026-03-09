"""
Neural Memory Compressor
Delta encoding, neural pattern prediction, tiered memory management.
"""

import numpy as np
import zlib
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


@dataclass
class MemoryRegion:
    pid: int
    region_id: str
    base_address: int
    size_bytes: int
    data: bytes
    is_compressed: bool = False
    compressed_data: bytes = b''
    compression_ratio: float = 1.0
    last_accessed: float = 0.0
    access_count: int = 0
    dirty: bool = False
    region_type: str = 'anonymous'


@dataclass
class CompressionStats:
    original_bytes: int = 0
    compressed_bytes: int = 0
    regions_compressed: int = 0
    regions_decompressed: int = 0
    compress_time_ms: float = 0.0
    decompress_time_ms: float = 0.0
    delta_hits: int = 0
    neural_assists: int = 0
    
    @property
    def ratio(self) -> float:
        if self.original_bytes == 0:
            return 1.0
        return self.original_bytes / (self.compressed_bytes + 1e-8)
    
    @property
    def savings_mb(self) -> float:
        return (self.original_bytes - self.compressed_bytes) / 1e6


class DeltaEncoder:
    """Delta encoding for similar memory regions."""
    
    def __init__(self):
        self._enc: Dict[str, bytes] = {}  # Encoder baselines
        self._dec: Dict[str, bytes] = {}  # Decoder baselines
    
    def encode(self, region_id: str, data: bytes) -> bytes:
        """Encode data with delta if baseline exists."""
        if region_id in self._enc:
            baseline = self._enc[region_id]
            if len(baseline) == len(data):
                # XOR delta
                delta = bytes(a ^ b for a, b in zip(data, baseline))
                # Check if delta is sparse enough
                changed = sum(1 for b in delta if b != 0) / len(delta)
                if changed < 0.4:
                    self._enc[region_id] = data
                    return b'\x01' + delta  # Delta marker
        
        # Keyframe
        self._enc[region_id] = data
        return b'\x00' + data
    
    def decode(self, region_id: str, encoded: bytes) -> bytes:
        """Decode delta or keyframe."""
        marker = encoded[0]
        payload = encoded[1:]
        
        if marker == 0x00:
            # Keyframe
            self._dec[region_id] = payload
            return payload
        else:
            # Delta
            if region_id not in self._dec:
                return payload
            baseline = self._dec[region_id]
            decoded = bytes(a ^ b for a, b in zip(baseline, payload))
            self._dec[region_id] = decoded
            return decoded
    
    def forget(self, region_id: str):
        """Clear baseline for region."""
        self._enc.pop(region_id, None)
        self._dec.pop(region_id, None)


class NeuralPatternPredictor:
    """N-gram pattern prediction for compression assist."""
    
    def __init__(self, n: int = 4, codebook_size: int = 512):
        self.n = n
        self.codebook_size = codebook_size
        self._ngrams: defaultdict = defaultdict(int)
        self._codebook: Dict[bytes, int] = {}
        self._trained_bytes = 0
    
    def learn(self, data: bytes):
        """Learn patterns from data."""
        self._trained_bytes += len(data)
        
        for i in range(len(data) - self.n + 1):
            pattern = data[i:i+self.n]
            self._ngrams[pattern] += 1
        
        # Rebuild codebook every 64KB
        if self._trained_bytes >= 65536:
            self._rebuild_codebook()
            self._trained_bytes = 0
    
    def _rebuild_codebook(self):
        """Build codebook from top patterns."""
        sorted_patterns = sorted(
            self._ngrams.items(), 
            key=lambda x: -x[1]
        )[:self.codebook_size]
        
        self._codebook = {
            pattern: idx for idx, (pattern, _) in enumerate(sorted_patterns)
        }
    
    def encode_assist(self, data: bytes) -> bytes:
        """Substitute known patterns with 2-byte codes."""
        if not self._codebook:
            return data
        
        result = bytearray()
        i = 0
        while i < len(data):
            substituted = False
            for n_size in range(self.n, 2, -1):
                pattern = data[i:i+n_size]
                if pattern in self._codebook:
                    result.extend(b'\xFF\xFE')
                    result.extend(self._codebook[pattern].to_bytes(2, 'big'))
                    i += n_size
                    substituted = True
                    break
            
            if not substituted:
                result.append(data[i])
                i += 1
        
        return bytes(result)
    
    def decode_assist(self, data: bytes) -> bytes:
        """Reverse pattern substitution."""
        if not self._codebook:
            return data
        
        reverse_codebook = {v: k for k, v in self._codebook.items()}
        result = bytearray()
        i = 0
        
        while i < len(data):
            if i < len(data) - 2 and data[i:i+2] == b'\xFF\xFE':
                code = int.from_bytes(data[i+2:i+4], 'big')
                if code in reverse_codebook:
                    result.extend(reverse_codebook[code])
                    i += 4
                    continue
            
            result.append(data[i])
            i += 1
        
        return bytes(result)


class TieredMemoryManager:
    """Three-tier memory management with neural compression."""
    
    def __init__(self, hot_limit_mb: int = 512, warm_limit_mb: int = 1024):
        self._hot: Dict[str, MemoryRegion] = {}  # Raw bytes
        self._warm: Dict[str, MemoryRegion] = {}  # Compressed
        self._cold: Dict[str, MemoryRegion] = {}  # Cold compressed
        
        self._hot_limit = hot_limit_mb * 1024 * 1024
        self._warm_limit = warm_limit_mb * 1024 * 1024
        
        self._delta_encoder = DeltaEncoder()
        self._pattern_predictor = NeuralPatternPredictor()
        self._stats = CompressionStats()
    
    def store(self, pid: int, region_id: str, data: bytes, 
              region_type: str = 'anonymous') -> str:
        """Store memory region in appropriate tier."""
        # Learn patterns
        self._pattern_predictor.learn(data[:4096])
        
        region = MemoryRegion(
            pid=pid,
            region_id=region_id,
            base_address=0,
            size_bytes=len(data),
            data=data,
            last_accessed=time.time(),
            region_type=region_type
        )
        
        self._stats.original_bytes += len(data)
        
        # Try hot tier first
        hot_usage = sum(r.size_bytes for r in self._hot.values())
        if hot_usage + len(data) <= self._hot_limit:
            self._hot[region_id] = region
            return 'hot'
        
        # Compress to warm
        self._compress_to_warm(region_id, region)
        return 'warm'
    
    def access(self, pid: int, region_id: str) -> Optional[bytes]:
        """Access memory region, promoting tiers as needed."""
        # Check hot tier
        if region_id in self._hot:
            region = self._hot[region_id]
            region.access_count += 1
            region.last_accessed = time.time()
            return region.data
        
        # Check warm tier
        if region_id in self._warm:
            region = self._warm[region_id]
            data = self._decompress_warm(region)
            self._stats.decompressed_bytes += region.size_bytes
            
            # Remove from warm
            del self._warm[region_id]
            
            # Promote to hot if frequently accessed
            region.access_count += 1
            if region.access_count > 3:
                self._hot[region_id] = region
            else:
                self._hot[region_id] = region
            
            return data
        
        # Check cold tier
        if region_id in self._cold:
            region = self._cold[region_id]
            data = self._decompress_cold(region)
            del self._cold[region_id]
            self._hot[region_id] = region
            return data
        
        return None
    
    def _compress_to_warm(self, region_id: str, region: MemoryRegion):
        """Compress region to warm tier."""
        start = time.time()
        
        # Delta encode
        delta = self._delta_encoder.encode(region_id, region.data)
        if delta[0] == 1:
            self._stats.delta_hits += 1
        
        # zlib compress
        compressed = zlib.compress(delta, level=3)
        
        region.compressed_data = compressed
        region.is_compressed = True
        region.compression_ratio = len(region.data) / (len(compressed) + 1e-8)
        
        self._stats.compressed_bytes += len(compressed)
        self._stats.regions_compressed += 1
        self._stats.compress_time_ms += (time.time() - start) * 1000
        
        # Check warm tier limit
        warm_usage = sum(len(r.compressed_data) for r in self._warm.values())
        if warm_usage + len(compressed) > self._warm_limit:
            self._compress_to_cold(region_id, region, region.data)
        else:
            self._warm[region_id] = region
    
    def _compress_to_cold(self, region_id: str, region: MemoryRegion, data: bytes):
        """Compress region to cold tier with pattern assist."""
        start = time.time()
        
        # Pattern-assisted compression
        assisted = self._pattern_predictor.encode_assist(data)
        if len(assisted) < len(data):
            self._stats.neural_assists += 1
        
        compressed = zlib.compress(assisted, level=9)
        region.compressed_data = compressed
        region.is_compressed = True
        region.compression_ratio = len(data) / (len(compressed) + 1e-8)
        
        self._stats.compressed_bytes += len(compressed)
        self._stats.compress_time_ms += (time.time() - start) * 1000
        
        self._cold[region_id] = region
    
    def _decompress_warm(self, region: MemoryRegion) -> bytes:
        """Decompress warm tier region."""
        start = time.time()
        
        delta = zlib.decompress(region.compressed_data)
        data = self._delta_encoder.decode(region.region_id, delta)
        
        region.data = data
        region.is_compressed = False
        region.last_accessed = time.time()
        
        self._stats.decompress_time_ms += (time.time() - start) * 1000
        return data
    
    def _decompress_cold(self, region: MemoryRegion) -> bytes:
        """Decompress cold tier region."""
        start = time.time()
        
        compressed = zlib.decompress(region.compressed_data)
        assisted = self._pattern_predictor.decode_assist(compressed)
        
        region.data = assisted
        region.is_compressed = False
        region.last_accessed = time.time()
        
        self._stats.decompress_time_ms += (time.time() - start) * 1000
        return assisted
    
    def evict_lru(self, target_free_mb: int) -> int:
        """Evict LRU regions to free memory."""
        target = target_free_mb * 1024 * 1024
        freed = 0
        
        # Sort hot by last_accessed
        hot_sorted = sorted(
            self._hot.values(),
            key=lambda r: r.last_accessed
        )
        
        for region in hot_sorted:
            if freed >= target:
                break
            self._compress_to_warm(region.region_id, region)
            freed += region.size_bytes
        
        # If still need more, compress warm to cold
        if freed < target:
            warm_sorted = sorted(
                self._warm.values(),
                key=lambda r: r.last_accessed
            )
            
            for region in warm_sorted:
                if freed >= target:
                    break
                self._compress_to_cold(
                    region.region_id, 
                    region,
                    region.data if region.data else b''
                )
                freed += region.size_bytes
        
        return freed
    
    def memory_report(self) -> Dict:
        """Generate memory usage report."""
        hot_size = sum(r.size_bytes for r in self._hot.values())
        warm_size = sum(len(r.compressed_data) for r in self._warm.values())
        cold_size = sum(len(r.compressed_data) for r in self._cold.values())
        
        return {
            'hot_regions': len(self._hot),
            'warm_regions': len(self._warm),
            'cold_regions': len(self._cold),
            'hot_size_mb': hot_size / 1e6,
            'warm_size_mb': warm_size / 1e6,
            'cold_size_mb': cold_size / 1e6,
            'compression_ratio': self._stats.ratio,
            'savings_mb': self._stats.savings_mb,
            'delta_hits': self._stats.delta_hits,
            'neural_assists': self._stats.neural_assists
        }
