import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC

# Create dataset matching the image
# Red balls (class 0): bottom-left and top-right corners
red_balls = np.array([
    [1.5, 1.5], [2, 1], [1, 1.5], [2, 2],  # bottom-left cluster
    [5, 5], [5.5, 5], [5, 5.5], [5.5, 5.5]  # top-right cluster
])

# Green balls (class 1): middle region  
green_balls = np.array([
    [3, 3], [3.5, 3], [3, 3.5], [3.5, 3.5]  # middle cluster
])

# Combine data
X = np.vstack([red_balls, green_balls])
y = np.array([0]*8 + [1]*4)  # 0=red, 1=green

# Create mesh grid for decision boundary visualization
x_min, x_max = 0, 7
y_min, y_max = 0, 7
xx, yy = np.meshgrid(np.linspace(x_min, x_max, 300),
                     np.linspace(y_min, y_max, 300))

# Train different classifiers
classifiers = {
    'Decision Tree': DecisionTreeClassifier(max_depth=4, random_state=42),
    'Neural Network (MLP)': MLPClassifier(hidden_layer_sizes=(8, 8), activation='relu', 
                                           max_iter=2000, random_state=42),
    'SVM (RBF Kernel)': SVC(kernel='rbf', gamma=0.5, C=10, random_state=42)
}

# Create figure with subplots
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for ax, (name, clf) in zip(axes, classifiers.items()):
    # Train classifier
    clf.fit(X, y)
    
    # Predict on mesh grid
    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    
    # Plot decision regions
    ax.contourf(xx, yy, Z, levels=[-0.5, 0.5, 1.5], colors=['#ffcccc', '#ccffcc'], alpha=0.6)
    ax.contour(xx, yy, Z, levels=[0.5], colors=['black'], linewidths=2)
    
    # Plot data points
    ax.scatter(red_balls[:, 0], red_balls[:, 1], c='red', s=150, edgecolors='black', 
               linewidths=2, label='Red (Class 0)', zorder=5)
    ax.scatter(green_balls[:, 0], green_balls[:, 1], c='green', s=150, edgecolors='black',
               linewidths=2, label='Green (Class 1)', zorder=5)
    
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 7)
    ax.set_xlabel('X', fontsize=12)
    ax.set_ylabel('Y', fontsize=12)
    ax.set_title(f'{name}\nAccuracy: {clf.score(X, y)*100:.0f}%', fontsize=12)
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')

plt.suptitle('Decision Boundaries: Green in Middle, Red in Corners\n(NOT an S-shape - it\'s a CLOSED REGION around the green cluster)', 
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('decision_boundary_comparison.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n" + "="*60)
print("ANSWER: Is the decision boundary S-shaped?")
print("="*60)
print("""
NO! The decision boundary is NOT S-shaped for this data pattern.

S-shaped boundary occurs when:
  - One class is in bottom-left, other class in top-right
  - Data is DIAGONALLY separated
  
Your data pattern:
  - Green in the MIDDLE (one compact cluster)
  - Red in TWO CORNERS (bottom-left AND top-right)
  
The decision boundary is:
  - Decision Tree: RECTANGULAR box around green cluster
  - Neural Network: CURVED/OVAL region around green cluster  
  - SVM (RBF): ELLIPTICAL region around green cluster

It's like drawing a FENCE around the green balls in the middle!
""")
