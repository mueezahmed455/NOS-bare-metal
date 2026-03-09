#ifndef NEURAL_CORE_H
#define NEURAL_CORE_H

#include <cstdint>
#include <cstddef>
#include "kernel.h"

// Neural network constants
#define MAX_LAYERS 16
#define MAX_NEURONS_PER_LAYER 1024
#define LEARNING_RATE 0.01f

// Activation functions
enum class ActivationFunction {
    SIGMOID,
    RELU,
    TANH,
    SOFTMAX
};

// Neuron structure
struct Neuron {
    float* weights;
    float bias;
    float output;
    float delta;
    size_t num_inputs;
};

// Layer structure
struct Layer {
    Neuron* neurons;
    size_t num_neurons;
    ActivationFunction activation;
};

// Neural network structure
struct NeuralNetwork {
    Layer* layers;
    size_t num_layers;
    float learning_rate;
};

// Neural core class
class NeuralCore {
public:
    static void initialize();
    static NeuralNetwork* create_network(size_t num_layers, size_t* layer_sizes, ActivationFunction* activations);
    static void destroy_network(NeuralNetwork* network);
    static void forward_pass(NeuralNetwork* network, float* inputs);
    static void backward_pass(NeuralNetwork* network, float* targets);
    static void update_weights(NeuralNetwork* network);
    static float train(NeuralNetwork* network, float* inputs, float* targets, size_t epochs);
    static void predict(NeuralNetwork* network, float* inputs, float* outputs);

private:
    static float sigmoid(float x);
    static float sigmoid_derivative(float x);
    static float relu(float x);
    static float relu_derivative(float x);
    static float tanh_activation(float x);
    static float tanh_derivative(float x);
    static void softmax_layer(Layer* layer);
    static void softmax(float* inputs, size_t size);
};

// Federated learning coordinator
class FederatedCoordinator {
public:
    static void initialize();
    static void add_node(u32 node_id);
    static void remove_node(u32 node_id);
    static void aggregate_models();
    static void distribute_global_model();
    static bool should_update_global_model();

private:
    static u32* node_ids;
    static size_t num_nodes;
    static NeuralNetwork* global_model;
    static u32 rounds_since_last_update;
};

// Consensus engine
class ConsensusEngine {
public:
    static void initialize();
    static bool validate_proof(const void* proof, size_t proof_size);
    static void* generate_proof(const NeuralNetwork* model);
    static bool reach_consensus(const void* proofs[], size_t num_proofs);
    static float calculate_learning_proof(const NeuralNetwork* model);

private:
    static u32 difficulty_target;
    static u64 total_computation;
};

#endif // NEURAL_CORE_H