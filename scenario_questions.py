"""Scenario-based and trick questions for ML interviews."""

from typing import List, Dict

# Scenario-based questions in MCQ format
SCENARIO_QUESTIONS: List[Dict] = [
    # Q1 — Tokenization / Domain Adaptation
    {
        "id": 1,
        "topic": "Tokenization / Domain Adaptation",
        "category": "LLM & NLP",
        "scenario": """A medical-domain startup is building an LLM assistant for radiology reports. 
Their dataset contains heavy use of complex, compound medical terms (e.g., "hyperdenseextra-axialhemorrhage").

Consider the tradeoffs for: vocabulary fragmentation, model perplexity, downstream fine-tuning stability, and rare word generalization.""",
        "question": "Which tokenization strategy should they choose?",
        "options": [
            "Train a tokenizer from scratch on their domain corpus",
            "Use the tokenizer from a general-purpose LLM (e.g., GPT-style)",
            "Use a hybrid approach (retain base tokenizer + add domain-specific merges)",
            "Use character-level tokenization for maximum flexibility"
        ],
        "correct_answer": 2,
        "explanation": """The hybrid approach (C) is optimal because:

• Vocabulary Fragmentation: Base tokenizer fragments medical terms ("hyperdense" → "hyper", "dense"), but adding domain merges reduces this
• Model Perplexity: Retains pretrained knowledge while improving on domain text
• Fine-tuning Stability: Keeps most embeddings frozen/pretrained, avoiding training from scratch
• Rare Word Generalization: Benefits from transfer learning + domain-specific handling

Option A loses pretrained knowledge. Option B causes severe fragmentation. Option D is computationally expensive and loses semantic chunking."""
    },
    
    # Q2 — Classical ML / XOR-Type Structure (Part A)
    {
        "id": 2,
        "topic": "Classical ML / XOR-Type Structure",
        "category": "Classical ML",
        "scenario": """You are given a dataset where the positive class appears in two disconnected regions (corners), 
while negative samples form a band between them - similar to an XOR pattern.""",
        "question": "Why does logistic regression fail on this configuration?",
        "options": [
            "Logistic regression requires normalized features",
            "Logistic regression creates a single linear decision boundary and cannot separate disconnected regions",
            "Logistic regression cannot handle binary classification",
            "Logistic regression fails when classes are imbalanced"
        ],
        "correct_answer": 1,
        "explanation": """Logistic regression fails because it can only create a SINGLE linear decision boundary (a hyperplane).

For XOR-like data, positive samples exist in TWO disconnected regions. No single straight line can separate:
• Bottom-left positives
• Top-right positives
• From middle negatives

You need at least TWO boundaries, which requires either:
• Polynomial features (transforms space)
• Non-linear models (trees, neural networks, kernelized SVM)"""
    },
    
    # Q2 — Classical ML / XOR-Type Structure (Part B)
    {
        "id": 3,
        "topic": "Classical ML / XOR-Type Structure",
        "category": "Classical ML",
        "scenario": """Same XOR-type dataset: positive class in two disconnected corner regions, negatives in the middle band.""",
        "question": "Can a decision tree learn this pattern? Why?",
        "options": [
            "No, decision trees can only create linear boundaries",
            "Yes, because trees use axis-aligned splits that can create multiple rectangular regions",
            "No, decision trees require continuous features only",
            "Yes, but only with boosting applied"
        ],
        "correct_answer": 1,
        "explanation": """Decision trees CAN learn XOR patterns because:

• Trees create AXIS-ALIGNED splits (vertical and horizontal cuts)
• Each split adds a new boundary
• The tree can learn: "if (x < 2.5 OR x > 4.5) → positive"
• Multiple splits create multiple rectangular decision regions

A tree with depth 2-3 can perfectly separate the disconnected positive regions from the negative band.
No feature transformation or ensemble needed - a single tree suffices."""
    },
    
    # Q2 — Classical ML / XOR-Type Structure (Part C)
    {
        "id": 4,
        "topic": "Classical ML / XOR-Type Structure",
        "category": "Neural Networks",
        "scenario": """XOR-type dataset with positive class in two disconnected regions.""",
        "question": "What is the MINIMAL neural network architecture to achieve 0 training error?",
        "options": [
            "Single layer perceptron (no hidden layers)",
            "One hidden layer with 1 neuron and ReLU activation",
            "One hidden layer with 2-3 neurons and non-linear activation (ReLU/tanh)",
            "At least 3 hidden layers with 10+ neurons each"
        ],
        "correct_answer": 2,
        "explanation": """The minimal architecture is: Input → Hidden(2-3 neurons, non-linear) → Output

• 2 hidden neurons minimum: Each can learn one decision boundary
• Non-linear activation ESSENTIAL: Without it, network collapses to linear model
• One hidden layer sufficient: Universal approximation theorem guarantees this

Architecture: Input(2) → Dense(2-3, ReLU) → Dense(1, sigmoid)

A single perceptron (A) fails (linear). One neuron (B) is insufficient. Three layers (D) is overkill."""
    },
    
    # Q2 — Classical ML / XOR-Type Structure (Part D)
    {
        "id": 5,
        "topic": "Classical ML / XOR-Type Structure",
        "category": "Classical ML",
        "scenario": """You're using SVM with RBF kernel on the XOR-type dataset.""",
        "question": "What failure mode would SVM with RBF kernel exhibit if γ (gamma) is too large?",
        "options": [
            "Underfitting - the decision boundary becomes too simple",
            "The model refuses to converge",
            "Severe overfitting - each training point becomes its own isolated 'island'",
            "The kernel becomes equivalent to a linear kernel"
        ],
        "correct_answer": 2,
        "explanation": """Large γ in RBF kernel causes SEVERE OVERFITTING:

• RBF kernel: K(x,y) = exp(-γ||x-y||²)
• Large γ → very narrow Gaussian peaks
• Each training point becomes its own "island" of influence
• Decision boundary becomes extremely jagged
• Model memorizes training data instead of learning patterns
• Fails to generalize to test data

The model achieves 100% training accuracy but near-random test performance."""
    },
    
    # Q3 — Decision Boundaries / Neural Networks
    {
        "id": 6,
        "topic": "Decision Boundaries / Neural Networks",
        "category": "Neural Networks",
        "scenario": """A dataset has two circle clusters (positive class) in opposite corners, separated by a band of crosses (negative class).
The positive regions are disjoint manifolds.""",
        "question": "Can a neural network produce 0 training error on this dataset? Select the best explanation.",
        "options": [
            "No, neural networks cannot separate disjoint positive regions",
            "Yes, because the Universal Approximation Theorem guarantees a single hidden layer with sufficient neurons can approximate any decision boundary",
            "Only with at least 5 hidden layers",
            "Only if the data is first transformed using PCA"
        ],
        "correct_answer": 1,
        "explanation": """Yes, a neural network CAN achieve 0 training error.

Universal Approximation Theorem: A single hidden layer with enough neurons can approximate ANY continuous function, including complex decision boundaries.

How it works:
• MLP hidden layers construct piecewise-linear partitions (with ReLU)
• Multiple neurons create multiple "folds" in decision space
• The network learns to "wrap around" the middle negative region
• Class topology (two disjoint manifolds) is learnable

ReLU creates sharp polygonal boundaries; tanh creates smoother curves. Both work."""
    },
    
    # Q3 — Activation Functions
    {
        "id": 7,
        "topic": "Decision Boundaries / Activation Functions",
        "category": "Neural Networks",
        "scenario": """You're training an MLP to separate two disjoint positive clusters from a negative band between them.""",
        "question": "Which activation function (ReLU vs tanh) is more likely to find a clean separating region?",
        "options": [
            "ReLU, because it's computationally faster",
            "Tanh, because it produces smoother decision boundaries that better capture curved class regions",
            "They are mathematically equivalent for classification",
            "Neither works; you must use sigmoid"
        ],
        "correct_answer": 1,
        "explanation": """Tanh often produces SMOOTHER decision boundaries:

• ReLU: Creates piecewise-LINEAR partitions → sharp, polygonal boundaries
• Tanh: Creates smooth, curved boundaries → better for curved class regions

For circular/elliptical class regions:
• Tanh naturally models curves with fewer neurons
• ReLU needs more neurons to approximate smooth curves with many linear segments

However, both can achieve 0 training error. ReLU trains faster but may need more neurons for smooth boundaries."""
    },
    
    # Q4 — Overfitting / Bias-Variance
    {
        "id": 8,
        "topic": "Overfitting / Bias-Variance",
        "category": "Model Evaluation",
        "scenario": """You train a binary classifier with:
• Training accuracy: 100%
• Validation accuracy: fluctuates between 45–60%
• ROC curve on held-out set is almost diagonal
• SHAP values show unstable feature importance between runs""",
        "question": "What is happening?",
        "options": [
            "Underfitting - the model is too simple",
            "Severe overfitting - the model memorized training data and performs like random guessing on validation",
            "Data leakage from training to validation set",
            "The loss function is incorrectly configured"
        ],
        "correct_answer": 1,
        "explanation": """This is SEVERE OVERFITTING:

Evidence:
• 100% training / ~50% validation = memorization, not learning
• Diagonal ROC = performance equivalent to random guessing
• Fluctuating SHAP values = model learns different spurious patterns each run

The model has perfectly memorized the training set (100% accuracy) but learned NO generalizable patterns. On unseen data, it performs no better than flipping a coin (45-60% on binary = random).

The unstable SHAP values indicate the model is in a flat/noisy loss landscape, finding different arbitrary solutions each run."""
    },
    
    # Q4 — Overfitting Fix
    {
        "id": 9,
        "topic": "Overfitting / Bias-Variance",
        "category": "Model Evaluation",
        "scenario": """Same situation: 100% train accuracy, ~50% validation accuracy, diagonal ROC, unstable SHAP values.""",
        "question": "What minimal ONE change would you apply first?",
        "options": [
            "Increase model complexity (add more layers)",
            "Add regularization (L2/Dropout)",
            "Increase the learning rate",
            "Add more training epochs"
        ],
        "correct_answer": 1,
        "explanation": """Regularization is the BEST first fix for overfitting:

Priority ranking:
1. Regularization (L2/Dropout) - Directly penalizes complexity, prevents memorization
2. Early Stopping - Stops before overfitting, but needs validation monitoring
3. Reduce Model Complexity - Fewer parameters = less capacity to memorize
4. Data Augmentation - Helps but slower to implement

Adding layers (A) worsens overfitting. Higher LR (C) causes instability. More epochs (D) increases overfitting.

Regularization is fast to implement (one parameter change) and directly addresses the core problem."""
    },
    
    # Q4 — SHAP Instability
    {
        "id": 10,
        "topic": "Overfitting / SHAP Interpretation",
        "category": "Model Evaluation",
        "scenario": """Your overfitting model shows unstable SHAP feature importance values across different training runs.""",
        "question": "Why do SHAP values fluctuate between runs?",
        "options": [
            "SHAP is a stochastic algorithm with inherent randomness",
            "The model finds different local minima each run, learning different spurious correlations",
            "The training data changes between runs",
            "SHAP values are only stable for linear models"
        ],
        "correct_answer": 1,
        "explanation": """SHAP values fluctuate because the MODEL differs between runs:

• The model is in a flat/noisy loss landscape
• Different random seeds → different local minima
• Each run learns different spurious correlations (memorized patterns)
• Feature importance reflects these arbitrary patterns, not true signal

If the model learned TRUE patterns:
• Same features would be important across runs
• SHAP values would be stable

Unstable SHAP = model is memorizing noise, not learning signal."""
    },
    
    # Q5 — Distribution Shift Detection
    {
        "id": 11,
        "topic": "Inference-Time Failure / Distribution Shift",
        "category": "MLOps",
        "scenario": """A segmentation model works perfectly on validation but fails on real-world data showing:
• Lower resolution
• Motion blur  
• Different lighting
• New background patterns""",
        "question": "What experiment would you run to CONFIRM distribution shift?",
        "options": [
            "Retrain the model with more epochs",
            "Train a classifier to distinguish validation images from real-world images - high accuracy confirms shift",
            "Check if the model architecture supports variable input sizes",
            "Compute training loss on real-world images"
        ],
        "correct_answer": 1,
        "explanation": """The Domain Classifier Test confirms distribution shift:

Method:
1. Label validation images as class 0
2. Label real-world images as class 1  
3. Train a classifier to distinguish them
4. High accuracy (>60%) = significant distribution shift

Alternative methods:
• Compute embedding statistics (mean, variance) for both sets
• Run 2-sample tests (KS test, MMD) on feature distributions
• Visualize embeddings with t-SNE/UMAP - distinct clusters = shift

If a simple classifier can easily distinguish the datasets, they come from different distributions."""
    },
    
    # Q5 — Distribution Shift Mitigation
    {
        "id": 12,
        "topic": "Inference-Time Failure / Distribution Shift",
        "category": "MLOps",
        "scenario": """Confirmed distribution shift between validation and real-world deployment images.""",
        "question": "What is the FASTEST mitigation without retraining?",
        "options": [
            "Collect more training data",
            "Test-Time Augmentation (TTA) - average predictions over augmented versions of input",
            "Fine-tune on real-world data",
            "Switch to a different model architecture"
        ],
        "correct_answer": 1,
        "explanation": """Test-Time Augmentation (TTA) is the fastest fix:

How TTA works:
1. Apply multiple augmentations to each test image (flip, rotate, scale)
2. Run inference on all augmented versions
3. Average the predictions

Why it helps:
• Some augmentations may match training distribution better
• Averaging reduces prediction variance
• No model changes or retraining needed

Other fast fixes:
• Histogram matching/normalization
• Input preprocessing to match training statistics

Retraining options (slower but more effective):
• Domain adaptation, data augmentation during training, domain randomization"""
    },
    
    # Q6 — LLM Strategy
    {
        "id": 13,
        "topic": "LLM Prompting vs Fine-Tuning vs RAG",
        "category": "LLM & NLP",
        "scenario": """A genomics company must classify gene-mutation descriptions (highly specialized text).
Options available:
1. Prompting a base LLM
2. RAG using an internal knowledge base
3. Fine-tuning a domain LLM
4. Training a domain tokenizer""",
        "question": "Which combination gives BEST long-term performance and cost efficiency?",
        "options": [
            "Prompting only - it's cheapest and requires no training",
            "RAG only - retrieval handles domain knowledge",
            "Fine-tuning + RAG - domain understanding plus dynamic knowledge retrieval",
            "Domain tokenizer + prompting - handles vocabulary best"
        ],
        "correct_answer": 2,
        "explanation": """Fine-tuning + RAG is optimal for specialized domains:

Fine-tuning provides:
• Deep domain understanding
• Learns genomics patterns, terminology
• Better base performance

RAG provides:
• Dynamic knowledge retrieval
• Up-to-date mutation databases
• Knowledge updates without retraining

Combined benefits:
• One-time fine-tuning cost amortized over many queries
• RAG allows knowledge updates without retraining
• Smaller fine-tuned model + RAG can outperform larger prompted model

Prompting alone lacks domain depth. RAG alone has retrieval errors. Domain tokenizer is optional (useful if vocabulary fragmentation is severe)."""
    },
    
    # Q7 — Optimization Instability
    {
        "id": 14,
        "topic": "Loss Landscape / Optimization",
        "category": "Training & Optimization",
        "scenario": """Your model trains normally for 10 epochs, then suddenly the loss spikes and remains unstable.
You check:
• Gradient norms → exploding
• Weight norms → growing
• Learning rate scheduler → constant LR
• Batch size → small (8)""",
        "question": "What is the root cause most likely?",
        "options": [
            "The model architecture is fundamentally flawed",
            "Exploding gradients due to high constant LR + small batch causing gradient variance",
            "The dataset contains corrupted samples",
            "The loss function is incorrectly implemented"
        ],
        "correct_answer": 1,
        "explanation": """Root cause: Exploding Gradients from LR + Batch Size interaction

The model reached a region of the loss landscape where:
• Gradients are naturally large
• Small batch (8) = high gradient variance
• Constant LR doesn't adapt → overshoots optimal region
• Overshooting increases weights → larger gradients → positive feedback loop

Evidence:
• "Normally for 10 epochs" = stable initially, then hit bad region
• Exploding gradients + growing weights = classic instability pattern
• Small batch + constant LR = no adaptive mechanism to handle it"""
    },
    
    # Q7 — Optimization Fix
    {
        "id": 15,
        "topic": "Loss Landscape / Optimization",
        "category": "Training & Optimization",
        "scenario": """Loss spiked at epoch 10. Gradients exploding. Need to fix without retraining from scratch.""",
        "question": "How would you patch this without retraining from scratch?",
        "options": [
            "Delete the model and start over with a new architecture",
            "Load checkpoint from epoch 8-9, add gradient clipping, reduce learning rate",
            "Increase batch size to 512 and continue from current state",
            "Switch to a different optimizer (Adam → SGD)"
        ],
        "correct_answer": 1,
        "explanation": """Best patch strategy:

1. Load checkpoint from epoch 8-9 (last stable state)
2. Add gradient clipping: torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
3. Reduce learning rate by 10x
4. Resume training

Why this works:
• Checkpoint restores stable weights
• Gradient clipping prevents explosion
• Lower LR reduces overshoot risk

Optional additions:
• Learning rate warmup from checkpoint
• Increase batch size if memory allows (reduces gradient variance)
• Add learning rate scheduler (cosine, reduce-on-plateau)"""
    },
    
    # Q8 — Imbalanced Data Accuracy
    {
        "id": 16,
        "topic": "Evaluation / Imbalanced Data",
        "category": "Model Evaluation",
        "scenario": """Dataset: 0.5% fraud, 99.5% legitimate.
A candidate reports: "Model accuracy = 99.4%, so performance is excellent."

Additional evaluation:
• AUROC = 0.62
• AUPRC = 0.04
• FPR at threshold = 18%""",
        "question": "Why is the 99.4% accuracy claim meaningless?",
        "options": [
            "Accuracy should be reported as a decimal, not percentage",
            "A model predicting 'always legitimate' achieves 99.5% accuracy - the reported model is actually WORSE",
            "99.4% accuracy is actually quite good for fraud detection",
            "The dataset is too small for meaningful accuracy calculation"
        ],
        "correct_answer": 1,
        "explanation": """99.4% accuracy is MEANINGLESS (actually worse than baseline):

Baseline model: Always predict "legitimate"
• Accuracy = 99.5% (correctly labels all 99.5% legitimate cases)
• The reported 99.4% is WORSE than this trivial baseline!

What the metrics reveal:
• AUROC = 0.62 → barely better than random (0.5)
• AUPRC = 0.04 → catches almost no fraud
• FPR = 18% → flags 18% of legitimate as fraud (huge false alarms)

For imbalanced data:
• Accuracy is dominated by majority class
• Model appears good while failing on the actual task (detecting fraud)"""
    },
    
    # Q8 — Best Metric for Imbalanced
    {
        "id": 17,
        "topic": "Evaluation / Imbalanced Data",
        "category": "Model Evaluation",
        "scenario": """Same fraud detection scenario with 0.5% fraud rate.""",
        "question": "Which single metric BEST captures real-world performance?",
        "options": [
            "Accuracy",
            "AUROC (Area Under ROC Curve)",
            "AUPRC (Area Under Precision-Recall Curve)",
            "F1 Score at default threshold"
        ],
        "correct_answer": 2,
        "explanation": """AUPRC is best for imbalanced data:

Why AUPRC > AUROC > Accuracy:

AUPRC:
• Focuses on the MINORITY class (fraud)
• Not inflated by true negatives (correctly identifying legitimate)
• Baseline is class proportion (0.5%), not 50%
• Directly measures what matters: finding fraud

AUROC:
• Can be misleadingly high with class imbalance
• A random classifier still gets 0.5 AUROC
• Inflated by large number of true negatives

Accuracy:
• Completely meaningless for imbalanced data
• Dominated by majority class

For 0.5% fraud: AUPRC of 0.04 vs baseline 0.005 = ~8x improvement, but still terrible."""
    },
    
    # Q9 — Multi-Modal Failure
    {
        "id": 18,
        "topic": "Multi-Modal Failure Case",
        "category": "Deep Learning",
        "scenario": """A dermatologist assistant uses:
• Image embedding branch (CNN)
• Text branch (BERT)
• Fused MLP classifier

Model performs poorly on "rare skin conditions" despite perfect training accuracy.""",
        "question": "What is the MOST likely bottleneck?",
        "options": [
            "The CNN architecture is too shallow",
            "Data imbalance (rare classes underrepresented) + modality collapse (one branch dominates)",
            "BERT is not suitable for medical text",
            "The fusion MLP has too few layers"
        ],
        "correct_answer": 1,
        "explanation": """Most likely bottlenecks:

1. Data Imbalance:
• Rare conditions have few training examples
• Model ignores minority classes (perfect accuracy on common = high overall accuracy)

2. Modality Collapse:
• One branch (likely text/BERT) dominates learning
• Image features may be ignored entirely
• Easy to achieve high accuracy using only text descriptions

Evidence:
• "Perfect training accuracy" + "poor on rare" = overfitting to majority classes
• Multi-modal models often learn to rely on the "easier" modality

The model memorizes common conditions and ignores rare ones."""
    },
    
    # Q9 — Multi-Modal Fix
    {
        "id": 19,
        "topic": "Multi-Modal Failure Case",
        "category": "Deep Learning",
        "scenario": """Same dermatology assistant with data imbalance and potential modality collapse.""",
        "question": "What architecture modification or training strategy fixes this?",
        "options": [
            "Use a deeper CNN backbone",
            "Weighted loss for rare classes + modality dropout + cross-attention fusion",
            "Switch from BERT to GPT",
            "Increase the MLP fusion layer size"
        ],
        "correct_answer": 1,
        "explanation": """Combined fix strategy:

1. Weighted Loss / Oversampling:
• Give rare conditions higher loss weight
• Or oversample rare examples during training

2. Modality Dropout:
• Randomly drop one modality during training (zero out one branch)
• Forces BOTH branches to learn useful representations
• Prevents over-reliance on single modality

3. Cross-Attention Fusion:
• Replace MLP fusion with cross-attention between modalities
• Allows dynamic weighting of image vs text features
• Better captures complementary information

Additional options:
• Few-shot learning head for rare classes
• Contrastive learning to align image-text embeddings"""
    },
    
    # Q10 — Curse of Dimensionality
    {
        "id": 20,
        "topic": "Curse of Dimensionality",
        "category": "Classical ML",
        "scenario": """You run k-NN on a dataset with 50k samples and 800 sparse features. Performance is terrible.""",
        "question": "Why do nearest neighbors break down in high-dimensional sparse spaces? (Intuitive explanation)",
        "options": [
            "k-NN requires continuous features, not sparse ones",
            "In high dimensions, all points become roughly equidistant - 'nearest' neighbor is barely closer than 'farthest'",
            "k-NN cannot handle more than 100 features",
            "Sparse features always contain missing values that break distance calculations"
        ],
        "correct_answer": 1,
        "explanation": """Intuitive explanation of the curse:

Imagine finding your "nearest neighbor":
• In 2D (small room): Easy to tell who's closest
• In 800D (massive warehouse with 800 hallways): Everyone seems roughly the same distance away

Why this happens:
1. Distance Concentration: Difference between nearest and farthest point becomes negligible
2. Sparse Data: Points are scattered so thinly that "neighborhoods" are essentially empty
3. Irrelevant Dimensions: Many of 800 features are noise, polluting distance calculations

With 50k samples in 800D:
• Each point has ~no meaningful neighbors
• k-NN essentially picks randomly from equally-distant points"""
    },
    
    # Q10 — Dimensionality Reduction Fix
    {
        "id": 21,
        "topic": "Curse of Dimensionality",
        "category": "Classical ML",
        "scenario": """k-NN failing on 800 sparse features. Need to rescue performance.""",
        "question": "What specific transformation could rescue performance?",
        "options": [
            "Increase k to consider more neighbors",
            "Dimensionality reduction: Autoencoder or Truncated SVD → then k-NN on reduced dimensions",
            "Switch to weighted k-NN with inverse distance weighting",
            "Normalize all features to unit variance"
        ],
        "correct_answer": 1,
        "explanation": """Dimensionality reduction is essential:

Recommended transformations:
• Truncated SVD / PCA: Fast, works well for sparse data
• Autoencoders: Learns compressed representation preserving structure
• UMAP: Creates low-dimensional manifold where neighbors are meaningful

Pipeline:
1. Reduce 800D → 50-100D using SVD/Autoencoder
2. Run k-NN on reduced dimensions
3. Distances become meaningful again

Why other options fail:
• Increasing k: Still using meaningless distances
• Inverse weighting: Weights are arbitrary when all distances similar
• Normalization: Doesn't fix the fundamental dimensionality problem

For sparse data specifically: TruncatedSVD (sparse-aware) > PCA"""
    }
]


def get_scenario_questions() -> List[Dict]:
    """Return all scenario-based questions."""
    return SCENARIO_QUESTIONS.copy()


def get_scenario_questions_by_category(category: str) -> List[Dict]:
    """Return scenario questions filtered by category."""
    return [q for q in SCENARIO_QUESTIONS if q["category"] == category]


def get_scenario_categories() -> List[str]:
    """Return list of unique categories."""
    return list(set(q["category"] for q in SCENARIO_QUESTIONS))


def get_scenario_question_count() -> int:
    """Return total number of scenario questions."""
    return len(SCENARIO_QUESTIONS)
