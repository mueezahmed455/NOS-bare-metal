"""
NeuralOS Kernel Core - Pure NumPy Neural Networks
No PyTorch, No TensorFlow. Just numpy.
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
import zlib


# ============================================================================
# Activation Functions
# ============================================================================

def relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(0, x)

def relu_grad(x: np.ndarray) -> np.ndarray:
    return (x > 0).astype(float)

def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

def sigmoid_grad(x: np.ndarray) -> np.ndarray:
    s = sigmoid(x)
    return s * (1 - s)

def tanh_act(x: np.ndarray) -> np.ndarray:
    return np.tanh(x)

def tanh_grad(x: np.ndarray) -> np.ndarray:
    return 1 - np.tanh(x) ** 2

def softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e / np.sum(e, axis=-1, keepdims=True)

def leaky_relu(x: np.ndarray, alpha: float = 0.01) -> np.ndarray:
    return np.where(x > 0, x, alpha * x)

def leaky_relu_grad(x: np.ndarray, alpha: float = 0.01) -> np.ndarray:
    return np.where(x > 0, 1, alpha)

def gelu(x: np.ndarray) -> np.ndarray:
    return 0.5 * x * (1 + np.tanh(np.sqrt(2 / np.pi) * (x + 0.044715 * x ** 3)))

def gelu_grad(x: np.ndarray) -> np.ndarray:
    return 0.5 * (1 + np.tanh(np.sqrt(2 / np.pi) * (x + 0.044715 * x ** 3))) + \
           0.5 * x * (1 - np.tanh(np.sqrt(2 / np.pi) * (x + 0.044715 * x ** 3)) ** 2) * \
           np.sqrt(2 / np.pi) * (1 + 3 * 0.044715 * x ** 2)


ACTIVATIONS = {
    'relu': (relu, relu_grad),
    'sigmoid': (sigmoid, sigmoid_grad),
    'tanh': (tanh_act, tanh_grad),
    'leaky_relu': (leaky_relu, leaky_relu_grad),
    'gelu': (gelu, gelu_grad),
    'linear': (lambda x: x, lambda x: np.ones_like(x)),
    'softmax': (softmax, lambda x: np.ones_like(x)),
}


# ============================================================================
# Dense Layer
# ============================================================================

class DenseLayer:
    """Fully connected neural network layer with Adam optimizer."""
    
    def __init__(self, input_dim: int, output_dim: int, activation: str = 'relu',
                 learning_rate: float = 1e-3, weight_decay: float = 1e-4,
                 dropout_rate: float = 0.0):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.activation_name = activation
        self.activation_fn, self.activation_grad = ACTIVATIONS.get(
            activation, (relu, relu_grad))
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.dropout_rate = dropout_rate
        self.training = True
        
        # He or Xavier initialization
        if activation in ['relu', 'leaky_relu', 'gelu']:
            std = np.sqrt(2.0 / input_dim)
        else:
            std = np.sqrt(1.0 / input_dim)
        
        self.W = np.random.randn(input_dim, output_dim) * std
        self.b = np.zeros((1, output_dim))
        
        # Adam optimizer state
        self.mW = np.zeros_like(self.W)
        self.vW = np.zeros_like(self.W)
        self.mb = np.zeros_like(self.b)
        self.vb = np.zeros_like(self.b)
        self.t = 0
        
        # Cache for backward pass
        self.cache = {}
    
    def forward(self, x: np.ndarray, mask: Optional[np.ndarray] = None) -> np.ndarray:
        self.cache['x'] = x
        z = x @ self.W + self.b
        self.cache['z'] = z
        a = self.activation_fn(z)
        
        # Dropout
        if self.training and self.dropout_rate > 0:
            self.dropout_mask = (np.random.rand(*a.shape) > self.dropout_rate).astype(float)
            a = a * self.dropout_mask / (1 - self.dropout_rate)  # Inverted dropout
        
        self.cache['a'] = a
        return a
    
    def backward(self, grad: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        x = self.cache['x']
        z = self.cache['z']
        
        # Apply dropout mask if used
        if self.training and self.dropout_rate > 0:
            grad = grad * self.dropout_mask / (1 - self.dropout_rate)
        
        grad = grad * self.activation_grad(z)
        
        grad_x = grad @ self.W.T
        grad_W = x.T @ grad + self.weight_decay * self.W
        grad_b = np.sum(grad, axis=0, keepdims=True)
        
        self.cache['grad_W'] = grad_W
        self.cache['grad_b'] = grad_b
        
        return grad_x, grad_W, grad_b
    
    def update_adam(self, beta1: float = 0.9, beta2: float = 0.999, eps: float = 1e-8):
        grad_W = self.cache.get('grad_W', np.zeros_like(self.W))
        grad_b = self.cache.get('grad_b', np.zeros_like(self.b))
        
        self.t += 1
        
        self.mW = beta1 * self.mW + (1 - beta1) * grad_W
        self.vW = beta2 * self.vW + (1 - beta2) * (grad_W ** 2)
        self.mb = beta1 * self.mb + (1 - beta1) * grad_b
        self.vb = beta2 * self.vb + (1 - beta2) * (grad_b ** 2)
        
        mW_hat = self.mW / (1 - beta1 ** self.t)
        vW_hat = self.vW / (1 - beta2 ** self.t)
        mb_hat = self.mb / (1 - beta1 ** self.t)
        vb_hat = self.vb / (1 - beta2 ** self.t)
        
        self.W -= self.learning_rate * mW_hat / (np.sqrt(vW_hat) + eps)
        self.b -= self.learning_rate * mb_hat / (np.sqrt(vb_hat) + eps)
    
    def get_params(self) -> Dict[str, np.ndarray]:
        return {'W': self.W.copy(), 'b': self.b.copy()}
    
    def set_params(self, params: Dict[str, np.ndarray]):
        self.W = params['W'].copy()
        self.b = params['b'].copy()
    
    def param_count(self) -> int:
        return self.W.size + self.b.size


# ============================================================================
# Embedding Layer
# ============================================================================

class EmbeddingLayer:
    """Simple embedding lookup layer."""
    
    def __init__(self, vocab_size: int, embed_dim: int):
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.E = np.random.randn(vocab_size, embed_dim) * 0.1
    
    def forward(self, indices: np.ndarray) -> np.ndarray:
        return self.E[indices]
    
    def backward(self, grad: np.ndarray, indices: np.ndarray, lr: float = 1e-3):
        np.add.at(self.E, indices, -lr * grad)
    
    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))
    
    def nearest(self, query: np.ndarray, top_k: int = 5) -> List[int]:
        scores = self.E @ query / (np.linalg.norm(self.E, axis=1) * np.linalg.norm(query) + 1e-8)
        return list(np.argsort(scores)[-top_k:][::-1])


# ============================================================================
# Attention Layer
# ============================================================================

class AttentionLayer:
    """Single-head attention layer."""
    
    def __init__(self, embed_dim: int, head_dim: int = 64):
        self.embed_dim = embed_dim
        self.head_dim = head_dim
        
        scale = 0.1
        self.Wq = np.random.randn(embed_dim, head_dim) * scale
        self.Wk = np.random.randn(embed_dim, head_dim) * scale
        self.Wv = np.random.randn(embed_dim, head_dim) * scale
        self.Wo = np.random.randn(head_dim, embed_dim) * scale
    
    def forward(self, x: np.ndarray, mask: Optional[np.ndarray] = None) -> np.ndarray:
        q = x @ self.Wq
        k = x @ self.Wk
        v = x @ self.Wv
        
        scale = np.sqrt(self.head_dim)
        scores = (q @ k.T) / scale
        
        if mask is not None:
            scores = scores + mask * -1e9
        
        attn = softmax(scores)
        out = attn @ v
        return out @ self.Wo


# ============================================================================
# MLP (Multi-Layer Perceptron)
# ============================================================================

class MLP:
    """Stack of dense layers."""
    
    def __init__(self, layer_dims: List[int], activations: Optional[List[str]] = None,
                 learning_rate: float = 1e-3, weight_decay: float = 1e-4,
                 dropout_rate: float = 0.0):
        self.layers: List[DenseLayer] = []
        self.learning_rate = learning_rate
        
        if activations is None:
            activations = ['relu'] * (len(layer_dims) - 2) + ['linear']
        
        for i in range(len(layer_dims) - 1):
            act = activations[i] if i < len(activations) else 'linear'
            self.layers.append(DenseLayer(
                layer_dims[i], layer_dims[i + 1], act,
                learning_rate, weight_decay, dropout_rate
            ))
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        for layer in self.layers:
            x = layer.forward(x)
        return x
    
    def train_step(self, x: np.ndarray, y: np.ndarray, 
                   task: str = 'regression') -> float:
        for layer in self.layers:
            layer.training = True
        
        pred = self.forward(x)
        
        if task == 'classification':
            loss = cross_entropy_loss(pred, y)
        else:
            loss = mse_loss(pred, y)
        
        grad = pred - y if task == 'regression' else softmax(pred) - y
        
        for layer in reversed(self.layers):
            grad, _, _ = layer.backward(grad)
            layer.update_adam()
        
        return float(loss)
    
    def predict(self, x: np.ndarray) -> np.ndarray:
        for layer in self.layers:
            layer.training = False
        return self.forward(x)
    
    def get_all_params(self) -> List[Dict[str, np.ndarray]]:
        return [layer.get_params() for layer in self.layers]
    
    def set_all_params(self, params: List[Dict[str, np.ndarray]]):
        for layer, p in zip(self.layers, params):
            layer.set_params(p)
    
    def param_count(self) -> int:
        return sum(layer.param_count() for layer in self.layers)
    
    def save(self, path: str):
        params = {f'layer_{i}_{k}': v 
                  for i, p in enumerate(self.get_all_params()) 
                  for k, v in p.items()}
        np.savez_compressed(path, **params)
    
    def load(self, path: str) -> bool:
        try:
            data = np.load(path)
            params = []
            i = 0
            while f'layer_{i}_W' in data:
                params.append({'W': data[f'layer_{i}_W'], 'b': data[f'layer_{i}_b']})
                i += 1
            self.set_all_params(params)
            return True
        except Exception:
            return False


# ============================================================================
# Autoencoder
# ============================================================================

class Autoencoder:
    """Autoencoder for anomaly detection."""
    
    def __init__(self, input_dim: int, bottleneck: int = 4, 
                 hidden: Optional[int] = None, lr: float = 1e-3):
        if hidden is None:
            hidden = max(input_dim // 2, bottleneck * 2)
        
        self.encoder = MLP([input_dim, hidden, bottleneck], ['relu', 'tanh'], lr)
        self.decoder = MLP([bottleneck, hidden, input_dim], ['relu', 'linear'], lr)
    
    def encode(self, x: np.ndarray) -> np.ndarray:
        return self.encoder.predict(x)
    
    def decode(self, z: np.ndarray) -> np.ndarray:
        return self.decoder.predict(z)
    
    def reconstruction_error(self, x: np.ndarray) -> np.ndarray:
        z = self.encode(x)
        recon = self.decode(z)
        return np.mean((x - recon) ** 2, axis=-1)
    
    def train_step(self, x: np.ndarray) -> float:
        z = self.encoder.forward(x)
        recon = self.decoder.forward(z)
        loss = mse_loss(recon, x)
        
        grad = recon - x
        for layer in reversed(self.decoder.layers):
            grad, _, _ = layer.backward(grad)
            layer.update_adam()
        
        grad, _, _ = self.encoder.layers[-1].backward(grad @ self.decoder.layers[0].W.T)
        for layer in reversed(self.encoder.layers[:-1]):
            grad, _, _ = layer.backward(grad)
            layer.update_adam()
        
        return float(loss)


# ============================================================================
# Model Compressor
# ============================================================================

class ModelCompressor:
    """Quantization and compression for model weights."""
    
    @staticmethod
    def quantize_weights(W: np.ndarray, bits: int = 8) -> Tuple[bytes, float, float]:
        w_min, w_max = W.min(), W.max()
        scale = (w_max - w_min) / (2 ** bits - 1) if w_max > w_min else 1.0
        quantized = np.round((W - w_min) / scale).astype(np.uint8)
        return quantized.tobytes(), w_min, scale
    
    @staticmethod
    def dequantize_weights(data: bytes, shape: Tuple, w_min: float, scale: float) -> np.ndarray:
        quantized = np.frombuffer(data, dtype=np.uint8).reshape(shape)
        return quantized.astype(np.float64) * scale + w_min
    
    @staticmethod
    def prune_weights(W: np.ndarray, sparsity: float = 0.3) -> np.ndarray:
        threshold = np.percentile(np.abs(W), sparsity * 100)
        W_pruned = W.copy()
        W_pruned[np.abs(W) < threshold] = 0
        return W_pruned
    
    @staticmethod
    def compress_model(mlp: MLP) -> bytes:
        compressed_layers = []
        for layer in mlp.layers:
            w_bytes, w_min, scale = ModelCompressor.quantize_weights(layer.W)
            b_bytes, b_min, b_scale = ModelCompressor.quantize_weights(layer.b)
            compressed_layers.append(
                f"{layer.W.shape}|{w_min}|{scale}|{b_min}|{b_scale}".encode() +
                zlib.compress(w_bytes) + b'|' + zlib.compress(b_bytes)
            )
        return b'|'.join(compressed_layers)
    
    @staticmethod
    def compressed_size_kb(mlp: MLP) -> float:
        return len(ModelCompressor.compress_model(mlp)) / 1024
    
    @staticmethod
    def float32_size_kb(mlp: MLP) -> float:
        return mlp.param_count() * 4 / 1024


# ============================================================================
# Loss Functions
# ============================================================================

def mse_loss(pred: np.ndarray, target: np.ndarray) -> np.ndarray:
    return np.mean((pred - target) ** 2)

def cross_entropy_loss(pred: np.ndarray, target: np.ndarray) -> np.ndarray:
    pred = softmax(pred)
    return -np.sum(target * np.log(pred + 1e-10)) / len(pred)
