"""
Neural Package Manager
AI-driven package installation with collaborative filtering.
"""

import time
from dataclasses import dataclass
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict, Counter
from enum import Enum
import re


class PkgStatus(Enum):
    AVAILABLE = 'available'
    INSTALLED = 'installed'
    CONFLICT = 'conflict'
    BROKEN = 'broken'


@dataclass
class Package:
    name: str
    version: str
    description: str
    categories: List[str]
    depends: List[str]
    conflicts: List[str]
    size_kb: int
    install_count: int
    last_updated_days: float
    has_cve: bool
    cve_count: int
    status: PkgStatus = PkgStatus.AVAILABLE
    install_ts: float = 0.0
    use_count: int = 0
    
    def feature_vector(self) -> List[float]:
        """8-dim feature vector for ML."""
        return [
            min(1.0, self.size_kb / 100000),  # Normalized size
            min(1.0, self.install_count / 1e7),  # Popularity
            max(0, 1 - self.last_updated_days / 365),  # Freshness
            0.0 if self.has_cve else 1.0,  # Security
            min(1.0, self.cve_count / 10),  # CVE severity
            len(self.categories) / 5,  # Category diversity
            len(self.depends) / 20,  # Dependency count
            self.use_count / 100,  # Usage
        ]


# Default package database (30 packages)
DEFAULT_PACKAGES: List[Package] = [
    # Development (10)
    Package('python3', '3.11.0', 'Python programming language', 
            ['dev', 'language'], ['glibc'], [], 50000, 5e8, 30, False, 0),
    Package('gcc', '13.2.0', 'GNU Compiler Collection',
            ['dev', 'compiler'], ['glibc', 'binutils'], [], 80000, 1e8, 60, False, 0),
    Package('git', '2.42.0', 'Distributed version control',
            ['dev', 'vcs'], ['openssl', 'curl'], [], 30000, 2e8, 15, False, 0),
    Package('vim', '9.0.1000', 'Text editor',
            ['dev', 'editor'], ['glibc'], [], 5000, 5e7, 45, False, 0),
    Package('neovim', '0.9.0', 'Modern Vim fork',
            ['dev', 'editor'], ['lua', 'glibc'], [], 8000, 2e7, 20, False, 0),
    Package('nodejs', '20.0.0', 'JavaScript runtime',
            ['dev', 'language'], ['glibc'], [], 40000, 1e8, 10, False, 0),
    Package('rust', '1.72.0', 'Rust programming language',
            ['dev', 'language'], ['glibc'], [], 100000, 5e7, 25, False, 0),
    Package('docker', '24.0.0', 'Container runtime',
            ['dev', 'container'], ['glibc', 'iptables'], [], 90000, 8e7, 5, False, 0),
    Package('make', '4.4.0', 'Build automation',
            ['dev', 'build'], [], [], 2000, 1e8, 120, False, 0),
    Package('cmake', '3.27.0', 'Cross-platform build system',
            ['dev', 'build'], ['glibc'], [], 15000, 5e7, 30, False, 0),
    
    # Data Science (6)
    Package('jupyter', '1.0.0', 'Interactive computing',
            ['data', 'python'], ['python3', 'numpy'], [], 30000, 3e7, 20, False, 0),
    Package('pandas', '2.0.0', 'Data analysis library',
            ['data', 'python'], ['python3', 'numpy'], [], 15000, 5e7, 15, False, 0),
    Package('numpy', '1.25.0', 'Numerical computing',
            ['data', 'python'], ['python3'], [], 20000, 8e7, 20, False, 0),
    Package('matplotlib', '3.7.0', 'Plotting library',
            ['data', 'python'], ['python3', 'numpy'], [], 10000, 4e7, 30, False, 0),
    Package('tensorflow', '2.13.0', 'ML framework',
            ['data', 'ml'], ['python3', 'numpy', 'cuda'], [], 500000, 2e7, 40, False, 0),
    Package('pytorch', '2.0.0', 'Deep learning framework',
            ['data', 'ml'], ['python3', 'numpy', 'cuda'], [], 400000, 3e7, 25, False, 0),
    
    # System (6)
    Package('htop', '3.2.0', 'Interactive process viewer',
            ['system', 'monitor'], ['glibc'], [], 500, 3e7, 90, False, 0),
    Package('curl', '8.2.0', 'HTTP client',
            ['system', 'network'], ['openssl'], [], 1000, 1e9, 30, False, 0),
    Package('wget', '1.21.0', 'File downloader',
            ['system', 'network'], ['openssl'], [], 800, 5e8, 180, False, 0),
    Package('openssh', '9.3.0', 'SSH server and client',
            ['system', 'security'], ['openssl'], [], 3000, 5e8, 60, False, 0),
    Package('ufw', '0.36.0', 'Uncomplicated Firewall',
            ['system', 'security'], ['iptables'], [], 500, 2e7, 200, False, 0),
    Package('fail2ban', '1.0.0', 'Intrusion prevention',
            ['system', 'security'], ['python3', 'iptables'], [], 1000, 1e7, 150, False, 0),
    
    # Media (3)
    Package('ffmpeg', '6.0.0', 'Video/audio processing',
            ['media', 'codec'], ['glibc'], [], 50000, 5e7, 45, False, 0),
    Package('vlc', '3.0.18', 'Media player',
            ['media', 'player'], ['glibc', 'ffmpeg'], [], 40000, 8e7, 90, False, 0),
    Package('gimp', '2.10.34', 'Image editor',
            ['media', 'graphics'], ['glibc', 'gtk'], [], 60000, 3e7, 60, False, 0),
    
    # Communication (2)
    Package('thunderbird', '115.0', 'Email client',
            ['comm', 'email'], ['glibc', 'gtk'], [], 100000, 2e7, 30, False, 0),
    Package('signal-cli', '0.11.0', 'Signal messenger CLI',
            ['comm', 'messaging'], ['java'], [], 20000, 5e6, 20, False, 0),
    
    # Utility (5)
    Package('zstd', '1.5.5', 'Zstandard compression',
            ['utility', 'compression'], [], [], 1000, 5e7, 60, False, 0),
    Package('ripgrep', '13.0.0', 'Fast grep alternative',
            ['utility', 'search'], [], [], 3000, 4e7, 30, False, 0),
    Package('fzf', '0.42.0', 'Fuzzy finder',
            ['utility', 'search'], [], [], 2000, 3e7, 45, False, 0),
    Package('tmux', '3.3a', 'Terminal multiplexer',
            ['utility', 'terminal'], ['glibc'], [], 1500, 4e7, 90, False, 0),
    Package('containerd', '1.7.0', 'Container daemon',
            ['utility', 'container'], ['glibc'], [], 30000, 3e7, 20, False, 0),
]


class DependencyResolver:
    """BFS-based dependency resolution."""
    
    def __init__(self, package_db: Dict[str, Package], 
                 installed: Set[str] = None):
        self.db = package_db
        self.installed = installed or set()
    
    def resolve(self, name: str, check_conflicts: bool = True) -> Dict:
        """Resolve dependencies for a package."""
        if name not in self.db:
            return {'ok': False, 'error': f'Package {name} not found'}
        
        pkg = self.db[name]
        
        # Check conflicts
        conflicts = []
        if check_conflicts:
            for conflict in pkg.conflicts:
                if conflict in self.installed:
                    conflicts.append(conflict)
        
        # BFS for dependencies
        to_install = []
        visited = set()
        queue = [name]
        missing = []
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            if current not in self.db:
                if current not in self.installed:
                    missing.append(current)
                continue
            
            if current not in self.installed:
                to_install.append(current)
            
            for dep in self.db[current].depends:
                if dep not in visited:
                    queue.append(dep)
        
        # Topological sort
        sorted_list = self._topological_sort(to_install)
        
        total_size = sum(self.db[p].size_kb for p in sorted_list if p in self.db)
        
        return {
            'ok': len(conflicts) == 0 and len(missing) == 0,
            'install_order': sorted_list,
            'count': len(sorted_list),
            'total_size_mb': total_size / 1024,
            'conflicts': conflicts,
            'missing': missing
        }
    
    def _topological_sort(self, names: List[str]) -> List[str]:
        """DFS post-order for correct install sequence."""
        result = []
        visited = set()
        
        def visit(name: str):
            if name in visited:
                return
            visited.add(name)
            
            if name in self.db:
                for dep in self.db[name].depends:
                    if dep in names:
                        visit(dep)
            
            result.append(name)
        
        for name in names:
            visit(name)
        
        return result


class PackageHealthScorer:
    """Scores package health for recommendations."""
    
    def __init__(self):
        self.weights = {
            'freshness': 0.30,
            'security': 0.35,
            'popularity': 0.20,
            'size': 0.15
        }
    
    def score(self, pkg: Package) -> Dict:
        """Calculate health score for a package."""
        freshness = max(0, 100 - pkg.last_updated_days * 0.3)
        security = 100 if not pkg.has_cve else max(0, 70 - pkg.cve_count * 20)
        popularity = min(100, 100 * (pkg.install_count / 1e7) ** 0.3)
        size_score = max(0, 100 - pkg.size_kb / 10000)
        
        overall = (
            freshness * self.weights['freshness'] +
            security * self.weights['security'] +
            popularity * self.weights['popularity'] +
            size_score * self.weights['size']
        )
        
        grade = 'A' if overall >= 85 else 'B' if overall >= 70 else 'C' if overall >= 55 else 'D'
        
        return {
            'freshness': freshness,
            'security': security,
            'popularity': popularity,
            'size': size_score,
            'overall': overall,
            'grade': grade
        }


class InstallPatternLearner:
    """Collaborative filtering for package recommendations."""
    
    def __init__(self):
        self._co_occur: defaultdict = defaultdict(Counter)
        self._seed_synthetic_sessions()
    
    def _seed_synthetic_sessions(self):
        """Seed with synthetic install patterns."""
        sessions = [
            {'python3', 'numpy', 'pandas', 'jupyter', 'matplotlib'},  # Data science
            {'gcc', 'make', 'git', 'vim', 'gdb'},  # Dev tools
            {'docker', 'containerd', 'kubectl', 'helm'},  # DevOps
            {'openssh', 'ufw', 'fail2ban', 'snort'},  # Security
            {'ffmpeg', 'vlc', 'gimp', 'blender'},  # Media
        ]
        
        for session in sessions:
            self.record_session(session)
    
    def record_install(self, pkg: str, categories: List[str],
                       currently_installed: Set[str]):
        """Record a package install for pattern learning."""
        for other in currently_installed:
            if other != pkg:
                self._co_occur[pkg][other] += 1
                self._co_occur[other][pkg] += 1
    
    def record_session(self, installed_set: Set[str]):
        """Bulk update from install session."""
        items = list(installed_set)
        for i, pkg1 in enumerate(items):
            for pkg2 in items[i+1:]:
                self._co_occur[pkg1][pkg2] += 1
                self._co_occur[pkg2][pkg1] += 1
    
    def recommend_from_installed(self, installed: Set[str], 
                                  db: Dict[str, Package],
                                  top_k: int = 10) -> List[Tuple[str, float]]:
        """Recommend packages based on co-occurrence."""
        scores: Counter = Counter()
        
        for pkg in installed:
            if pkg in self._co_occur:
                for candidate, count in self._co_occur[pkg].items():
                    if candidate not in installed and candidate in db:
                        scores[candidate] += count
        
        return scores.most_common(top_k)


class NeuralPkgManager:
    """AI-driven package manager."""
    
    def __init__(self):
        self.db: Dict[str, Package] = {p.name: p for p in DEFAULT_PACKAGES}
        self.installed: Set[str] = set()
        self.install_history: List[Dict] = []
        self.context_mode = 'general'
        
        self.resolver = DependencyResolver(self.db, self.installed)
        self.scorer = PackageHealthScorer()
        self.learner = InstallPatternLearner()
    
    def install(self, name: str, dry_run: bool = False) -> Dict:
        """Install a package with dependency resolution."""
        if name in self.installed:
            return {'ok': False, 'error': 'Already installed'}
        
        result = self.resolver.resolve(name)
        if not result['ok']:
            return result
        
        if dry_run:
            return {**result, 'dry_run': True}
        
        # Install in order
        for pkg_name in result['install_order']:
            if pkg_name in self.db:
                pkg = self.db[pkg_name]
                pkg.status = PkgStatus.INSTALLED
                pkg.install_ts = time.time()
                self.installed.add(pkg_name)
                
                self.learner.record_install(
                    pkg_name, pkg.categories, 
                    self.installed - {pkg_name}
                )
        
        self.install_history.append({
            'action': 'install',
            'package': name,
            'timestamp': time.time(),
            'deps': result['install_order']
        })
        
        health = self.scorer.score(self.db[name])
        return {
            'ok': True,
            'installed': result['install_order'],
            'health_score': health
        }
    
    def remove(self, name: str) -> Dict:
        """Remove a package (check reverse deps)."""
        if name not in self.installed:
            return {'ok': False, 'error': 'Not installed'}
        
        # Check reverse dependencies
        reverse_deps = []
        for pkg_name in self.installed:
            if pkg_name != name and name in self.db.get(pkg_name, Package('', '', '', [], [], [], 0, 0, 0, False, 0)).depends:
                reverse_deps.append(pkg_name)
        
        if reverse_deps:
            return {
                'ok': False, 
                'error': f'Required by: {", ".join(reverse_deps)}'
            }
        
        self.installed.discard(name)
        self.install_history.append({
            'action': 'remove',
            'package': name,
            'timestamp': time.time()
        })
        
        return {'ok': True, 'removed': name}
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Search packages by word overlap."""
        query_words = set(query.lower().split())
        
        scores = []
        for name, pkg in self.db.items():
            text = f"{name} {pkg.description} {' '.join(pkg.categories)}".lower()
            pkg_words = set(text.split())
            
            overlap = len(query_words & pkg_words)
            if overlap > 0:
                scores.append((name, overlap))
        
        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]
    
    def recommend(self, context_mode: str = 'general', 
                  top_k: int = 10) -> List[Tuple[str, float]]:
        """Recommend packages based on context and patterns."""
        self.context_mode = context_mode
        
        # Collaborative filtering (0.5 weight)
        collab_scores = self.learner.recommend_from_installed(
            self.installed, self.db, top_k * 2
        )
        
        # Health scores (0.3 weight)
        health_scores = [
            (name, self.scorer.score(pkg)['overall'] / 100)
            for name, pkg in self.db.items()
            if name not in self.installed
        ]
        health_scores.sort(key=lambda x: -x[1])
        
        # Context boost (0.2 weight)
        context_keywords = {
            'coding': ['dev', 'editor', 'language'],
            'data_analysis': ['data', 'ml', 'python'],
            'sysadmin': ['system', 'security', 'network'],
            'media': ['media', 'graphics', 'codec'],
        }
        
        keywords = context_keywords.get(context_mode, [])
        context_scores = []
        for name, pkg in self.db.items():
            if name not in self.installed:
                match = any(kw in pkg.categories for kw in keywords)
                context_scores.append((name, 0.3 if match else 0.0))
        
        # Merge scores
        merged: Dict[str, float] = {}
        for name, score in collab_scores:
            merged[name] = merged.get(name, 0) + score * 0.5
        for name, score in health_scores[:top_k]:
            merged[name] = merged.get(name, 0) + score * 30
        for name, score in context_scores:
            merged[name] = merged.get(name, 0) + score * 20
        
        sorted_recs = sorted(merged.items(), key=lambda x: -x[1])
        return sorted_recs[:top_k]
    
    def audit(self) -> Dict:
        """Audit installed packages for health issues."""
        issues = []
        recommendations = []
        
        for name in self.installed:
            pkg = self.db.get(name)
            if not pkg:
                continue
            
            health = self.scorer.score(pkg)
            if health['overall'] < 70:
                issues.append({
                    'package': name,
                    'grade': health['grade'],
                    'reason': 'Low health score'
                })
            
            if pkg.has_cve:
                issues.append({
                    'package': name,
                    'grade': 'F',
                    'reason': f'{pkg.cve_count} CVEs'
                })
        
        # Get recommendations
        recs = self.recommend(self.context_mode, top_k=5)
        for name, score in recs:
            recommendations.append({
                'package': name,
                'score': score,
                'reason': 'Frequently installed together'
            })
        
        return {
            'installed_count': len(self.installed),
            'issues': issues,
            'recommendations': recommendations
        }
    
    def stats(self) -> Dict:
        """Package manager statistics."""
        return {
            'installed': list(self.installed),
            'installed_count': len(self.installed),
            'available': len(self.db) - len(self.installed),
            'install_history': self.install_history[-10:],
            'context_mode': self.context_mode
        }
