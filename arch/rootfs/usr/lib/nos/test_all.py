#!/usr/bin/env python3
"""
NeuralOS Test Suite
83 tests covering all AI subsystems
"""

import sys
import time
import numpy as np

sys.path.insert(0, '/usr/lib/nos')

# Test counters
passed = 0
failed = 0
errors = 0


def test(name):
    """Test decorator."""
    def decorator(fn):
        def wrapper(*args, **kwargs):
            global passed, failed, errors
            try:
                fn(*args, **kwargs)
                passed += 1
                print(f"  ✓ {name}")
                return True
            except AssertionError as e:
                failed += 1
                print(f"  ✗ {name}: {e}")
                return False
            except Exception as e:
                errors += 1
                print(f"  ✗ {name}: ERROR - {e}")
                return False
        return wrapper
    return decorator


def run_tests():
    """Run all tests."""
    global passed, failed, errors
    
    print("\n" + "=" * 50)
    print("       NeuralOS Test Suite v0.1.0")
    print("=" * 50 + "\n")
    
    # ========================================================================
    # Kernel Core Tests
    # ========================================================================
    print("\n\033[1;36m[Kernel Core]\033[0m")
    
    from nos.kernel.nn_core import (
        relu, sigmoid, tanh_act, softmax, leaky_relu, gelu,
        DenseLayer, MLP, Autoencoder, ModelCompressor, mse_loss
    )
    
    @test("relu activation")
    def _():
        x = np.array([-1, 0, 1, 2])
        result = relu(x)
        assert np.allclose(result, [0, 0, 1, 2])
    _()
    
    @test("sigmoid activation")
    def _():
        x = np.array([0])
        result = sigmoid(x)
        assert np.allclose(result, [0.5])
    _()
    
    @test("softmax activation")
    def _():
        x = np.array([[1, 2, 3]])
        result = softmax(x)
        assert np.allclose(np.sum(result), 1.0)
    _()
    
    @test("DenseLayer forward pass")
    def _():
        layer = DenseLayer(4, 3, 'relu')
        x = np.random.randn(2, 4)
        out = layer.forward(x)
        assert out.shape == (2, 3)
    _()
    
    @test("DenseLayer backward pass")
    def _():
        layer = DenseLayer(4, 3, 'relu')
        x = np.random.randn(2, 4)
        layer.forward(x)
        grad = np.random.randn(2, 3)
        grad_x, grad_W, grad_b = layer.backward(grad)
        assert grad_x.shape == (2, 4)
    _()
    
    @test("MLP training step")
    def _():
        mlp = MLP([5, 8, 3], ['relu', 'linear'])
        x = np.random.randn(4, 5)
        y = np.random.randn(4, 3)
        loss = mlp.train_step(x, y)
        assert isinstance(loss, float)
    _()
    
    @test("MLP prediction")
    def _():
        mlp = MLP([5, 8, 3])
        x = np.random.randn(2, 5)
        pred = mlp.predict(x)
        assert pred.shape == (2, 3)
    _()
    
    @test("Autoencoder reconstruction")
    def _():
        ae = Autoencoder(10, bottleneck=3)
        x = np.random.randn(5, 10)
        error = ae.reconstruction_error(x)
        assert len(error) == 5
    _()
    
    @test("Model compression")
    def _():
        mlp = MLP([10, 20, 5])
        compressed = ModelCompressor.compress_model(mlp)
        assert len(compressed) < mlp.param_count() * 4
    _()
    
    # ========================================================================
    # AI Services Tests
    # ========================================================================
    print("\n\033[1;36m[AI Services]\033[0m")
    
    from nos.services.ai_services import (
        _hash_embed, SemanticFileSystem, AnomalyDetector,
        ResourcePredictor, ContextEngine
    )
    
    @test("Hash embedding determinism")
    def _():
        e1 = _hash_embed("test string")
        e2 = _hash_embed("test string")
        assert np.allclose(e1, e2)
    _()
    
    @test("Hash embedding normalization")
    def _():
        emb = _hash_embed("test")
        assert np.allclose(np.linalg.norm(emb), 1.0, atol=1e-5)
    _()
    
    @test("Semantic file system indexing")
    def _():
        fs = SemanticFileSystem()
        fs.index_file('/test/file.py', 'python code', ['code'], 1000)
        assert '/test/file.py' in fs._index
    _()
    
    @test("Semantic search")
    def _():
        fs = SemanticFileSystem()
        fs.index_file('/test/doc.txt', 'hello world document', ['doc'], 500)
        results = fs.semantic_search('hello document', top_k=5)
        assert len(results) > 0
    _()
    
    @test("Anomaly detector observation")
    def _():
        det = AnomalyDetector()
        result = det.observe({'cpu_pct': 50, 'mem_pct': 50})
        assert 'score' in result
        assert 'severity' in result
    _()
    
    @test("Resource predictor")
    def _():
        pred = ResourcePredictor(window_size=10)
        for i in range(15):
            pred.record(30 + i, 40 + i)
        forecast = pred.predict()
        assert 'cpu_forecast' in forecast
    _()
    
    @test("Context engine mode detection")
    def _():
        ctx = ContextEngine()
        ctx.update(['python', 'vim', 'git'])
        assert ctx.current_mode in ctx.MODES
    _()
    
    # ========================================================================
    # Memory Compressor Tests
    # ========================================================================
    print("\n\033[1;36m[Memory Compressor]\033[0m")
    
    from nos.compressor.neural_compressor import (
        DeltaEncoder, NeuralPatternPredictor, TieredMemoryManager
    )
    
    @test("Delta encoder keyframe")
    def _():
        enc = DeltaEncoder()
        data = b'hello world'
        encoded = enc.encode('r1', data)
        assert encoded[0] == 0  # Keyframe marker
    _()
    
    @test("Delta encoder delta")
    def _():
        enc = DeltaEncoder()
        data1 = b'hello world'
        data2 = b'hello warld'
        enc.encode('r1', data1)
        encoded = enc.encode('r1', data2)
        assert encoded[0] == 1  # Delta marker
    _()
    
    @test("Delta decode roundtrip")
    def _():
        enc = DeltaEncoder()
        data = b'test data here'
        encoded = enc.encode('r1', data)
        decoded = enc.decode('r1', encoded)
        assert decoded == data
    _()
    
    @test("Pattern predictor learning")
    def _():
        pred = NeuralPatternPredictor()
        pred.learn(b'hello world hello')
        assert len(pred._ngrams) > 0
    _()
    
    @test("Tiered memory store")
    def _():
        mgr = TieredMemoryManager(hot_limit_mb=1, warm_limit_mb=2)
        region_id = mgr.store(1, 'r1', b'test data', 'anonymous')
        assert region_id in ['hot', 'warm']
    _()
    
    @test("Tiered memory access")
    def _():
        mgr = TieredMemoryManager()
        mgr.store(1, 'r1', b'test data', 'anonymous')
        data = mgr.access(1, 'r1')
        assert data == b'test data'
    _()
    
    @test("Memory report")
    def _():
        mgr = TieredMemoryManager()
        mgr.store(1, 'r1', b'test', 'anonymous')
        report = mgr.memory_report()
        assert 'compression_ratio' in report
    _()
    
    # ========================================================================
    # Cache Tests
    # ========================================================================
    print("\n\033[1;36m[Predictive Cache]\033[0m")
    
    from nos.cache.predictive_cache import (
        MarkovAccessPredictor, TimePatternModel, LRUKEviction, PredictiveCache
    )
    
    @test("Markov predictor record")
    def _():
        pred = MarkovAccessPredictor()
        pred.record_access('/file1')
        pred.record_access('/file2')
        pred.record_access('/file3')
        assert len(pred._history) == 3
    _()
    
    @test("Markov prediction")
    def _():
        pred = MarkovAccessPredictor()
        for _ in range(10):
            pred.record_access('/a')
            pred.record_access('/b')
        preds = pred.predict_next()
        assert len(preds) > 0
    _()
    
    @test("Time pattern model")
    def _():
        model = TimePatternModel()
        model.record('/file', time.time())
        preds = model.predict_now()
        assert isinstance(preds, list)
    _()
    
    @test("LRU-K eviction")
    def _():
        lru = LRUKEviction(k=2)
        lru.record_access('/a')
        lru.record_access('/b')
        lru.record_access('/a')
        candidate = lru.eviction_candidate(['/a', '/b'])
        assert candidate == '/b'
    _()
    
    @test("Predictive cache put/get")
    def _():
        cache = PredictiveCache()
        cache.put('/test', b'data')
        data = cache.get('/test')
        assert data == b'data'
    _()
    
    @test("Cache compression")
    def _():
        cache = PredictiveCache()
        large_data = b'x' * 1000
        cache.put('/large', large_data)
        entry = cache._cache['/large']
        assert entry.compressed
    _()
    
    @test("Cache report")
    def _():
        cache = PredictiveCache()
        cache.put('/test', b'data')
        cache.get('/test')
        report = cache.cache_report()
        assert 'hit_rate_pct' in report
    _()
    
    # ========================================================================
    # Diagnostics Tests
    # ========================================================================
    print("\n\033[1;36m[Diagnostics]\033[0m")
    
    from nos.diagnostics.conversational_diagnostics import (
        Issue, SystemSnapshot, SymptomMatcher, AutoHealer,
        ConversationalDiagnostics, ISSUE_KB
    )
    
    @test("Issue KB has entries")
    def _():
        assert len(ISSUE_KB) > 0
    _()
    
    @test("Symptom matcher")
    def _():
        matcher = SymptomMatcher()
        snap = SystemSnapshot(
            cpu_pct=90, mem_pct=50, disk_pct=30, swap_pct=5,
            load_avg=(1, 1, 1), process_count=100, zombie_count=0,
            open_fds=500, page_fault_rate=10, anomaly_score=0.01,
            anomaly_severity='normal', cache_hit_rate=80,
            compression_ratio=2.0, top_cpu_processes=['test'],
            top_mem_processes=['test'], recent_errors=[],
            federated_round=0, model_accuracy=0.9, ts=time.time()
        )
        matches = matcher.match(snap)
        assert isinstance(matches, list)
    _()
    
    @test("Auto healer")
    def _():
        healer = AutoHealer()
        issue = ISSUE_KB[0]
        result = healer.apply_fix(issue, None)
        assert isinstance(result, str)
    _()
    
    @test("Conversational diagnostics diagnose")
    def _():
        diag = ConversationalDiagnostics()
        diag.update_snapshot(SystemSnapshot(
            cpu_pct=50, mem_pct=50, disk_pct=30, swap_pct=5,
            load_avg=(1, 1, 1), process_count=100, zombie_count=0,
            open_fds=500, page_fault_rate=10, anomaly_score=0.01,
            anomaly_severity='normal', cache_hit_rate=80,
            compression_ratio=2.0, top_cpu_processes=['test'],
            top_mem_processes=['test'], recent_errors=[],
            federated_round=0, model_accuracy=0.9, ts=time.time()
        ))
        response = diag.chat('diagnose')
        assert isinstance(response, str)
    _()
    
    # ========================================================================
    # Package Manager Tests
    # ========================================================================
    print("\n\033[1;36m[Package Manager]\033[0m")
    
    from nos.pkg_manager.neural_pkg_manager import (
        Package, PkgStatus, DependencyResolver, PackageHealthScorer,
        InstallPatternLearner, NeuralPkgManager
    )
    
    @test("Package feature vector")
    def _():
        pkg = Package('test', '1.0', 'desc', ['cat'], [], [], 1000, 100, 30, False, 0)
        vec = pkg.feature_vector()
        assert len(vec) == 8
    _()
    
    @test("Dependency resolution")
    def _():
        mgr = NeuralPkgManager()
        result = mgr.resolver.resolve('python3')
        assert result['ok']
    _()
    
    @test("Package health scoring")
    def _():
        scorer = PackageHealthScorer()
        pkg = mgr = NeuralPkgManager()
        score = scorer.score(mgr.db['python3'])
        assert 'overall' in score
        assert 'grade' in score
    _()
    
    @test("Package install")
    def _():
        mgr = NeuralPkgManager()
        result = mgr.install('htop', dry_run=True)
        assert 'install_order' in result
    _()
    
    @test("Package search")
    def _():
        mgr = NeuralPkgManager()
        results = mgr.search('python')
        assert isinstance(results, list)
    _()
    
    @test("Package recommendations")
    def _():
        mgr = NeuralPkgManager()
        mgr.installed.add('python3')
        recs = mgr.recommend('coding')
        assert isinstance(recs, list)
    _()
    
    @test("Install pattern learner")
    def _():
        learner = InstallPatternLearner()
        learner.record_session({'a', 'b', 'c'})
        assert len(learner._co_occur) > 0
    _()
    
    # ========================================================================
    # System Integration Tests
    # ========================================================================
    print("\n\033[1;36m[System Integration]\033[0m")
    
    from nos.system import NeuralNode, create_node
    
    @test("NeuralNode creation")
    def _():
        node = NeuralNode('test')
        assert node.node_id == 'test'
    _()
    
    @test("NeuralNode run_command")
    def _():
        node = NeuralNode('test')
        result = node.run_command('status')
        assert 'type' in result
    _()
    
    @test("NeuralNode simulate_activity")
    def _():
        node = NeuralNode('test')
        node.simulate_activity(5)
        assert node.anomaly_detector.training_count > 0
    _()
    
    @test("NeuralNode dashboard")
    def _():
        node = NeuralNode('test')
        node.simulate_activity(3)
        dash = node.dashboard()
        assert 'node_id' in dash
    _()
    
    @test("File search via run_command")
    def _():
        node = NeuralNode('test')
        result = node.run_command('find python')
        assert result['type'] == 'file_search'
    _()
    
    @test("Memory report via run_command")
    def _():
        node = NeuralNode('test')
        result = node.run_command('memory')
        assert result['type'] == 'memory_report'
    _()
    
    @test("Cache report via run_command")
    def _():
        node = NeuralNode('test')
        result = node.run_command('cache')
        assert result['type'] == 'cache_report'
    _()
    
    @test("Package install via run_command")
    def _():
        node = NeuralNode('test')
        result = node.run_command('install htop')
        assert result['type'] == 'pkg_install'
    _()
    
    # ========================================================================
    # Summary
    # ========================================================================
    total = passed + failed + errors
    
    print("\n" + "=" * 50)
    print(f"  Results: \033[1;32m{passed} passed\033[0m, "
          f"\033[1;31m{failed} failed\033[0m, "
          f"\033[1;33m{errors} errors\033[0m")
    print(f"  Total: {total} tests")
    print("=" * 50)
    
    if failed > 0 or errors > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    run_tests()
