import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon, Rectangle
import numpy as np
from collections import defaultdict
import time

class AlphaBetaAnimator:
    def __init__(self):
        # Tree structure: node_id -> (parent, children, value, node_type)
        self.tree = {
            0: (None, [1, 2, 3], None, 'max'),     # Root (Max)
            1: (0, [4, 5, 6], None, 'min'),       # Left Min node
            2: (0, [7, 8, 9], None, 'min'),       # Middle Min node  
            3: (0, [10, 11, 12], None, 'min'),    # Right Min node
            4: (1, [], 5, 'leaf'),                # Leaf values
            5: (1, [], 2, 'leaf'),
            6: (1, [], 3, 'leaf'),
            7: (2, [], 1, 'leaf'),
            8: (2, [], 2, 'leaf'),
            9: (2, [], 3, 'leaf'),
            10: (3, [], 4, 'leaf'),
            11: (3, [], 0, 'leaf'),
            12: (3, [], 5, 'leaf')
        }
        
        # Node positions for visualization
        self.pos = {
            0: (0, 2),      # Root
            1: (-2.5, 1),   # Left Min
            2: (0, 1),      # Middle Min
            3: (2.5, 1),    # Right Min
            4: (-3.5, 0),   # Left leaves
            5: (-2.5, 0),
            6: (-1.5, 0),
            7: (-0.5, 0),   # Middle leaves
            8: (0, 0),
            9: (0.5, 0),
            10: (1.5, 0),   # Right leaves
            11: (2.5, 0),
            12: (3.5, 0)
        }
        
        # Animation states - each state represents one frame
        self.animation_states = []
        self.current_frame = 0
        
        # Algorithm tracking
        self.step_descriptions = []
        
        # Initialize matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        self.fig.patch.set_facecolor('white')
        
    def generate_animation_states(self, use_pruning=True):
        """Generate all animation states by running the algorithm"""
        self.animation_states = []
        self.step_descriptions = []
        
        # Initial state
        initial_state = {
            'visited_nodes': set(),
            'current_node': None,
            'alpha_beta_values': {},
            'node_values': {},
            'pruned_edges': set(),
            'step_count': 0,
            'description': 'Initial Tree State'
        }
        self.animation_states.append(initial_state.copy())
        
        # Run algorithm to generate states
        self._run_algorithm_with_states(0, float('-inf'), float('inf'), True, use_pruning)
        
        # Final state
        final_state = self.animation_states[-1].copy()
        final_state['current_node'] = None
        final_state['description'] = f"Algorithm Complete - Result: {final_state.get('result', 'N/A')}"
        self.animation_states.append(final_state)
        
    def _run_algorithm_with_states(self, node_id, alpha, beta, maximizing_player, use_pruning=True):
        """Run algorithm and capture states for animation"""
        if not self.animation_states:
            current_state = {
                'visited_nodes': set(),
                'current_node': None,
                'alpha_beta_values': {},
                'node_values': {},
                'pruned_edges': set(),
                'step_count': 0
            }
        else:
            current_state = self.animation_states[-1].copy()
            # Deep copy sets and dicts
            current_state['visited_nodes'] = current_state['visited_nodes'].copy()
            current_state['alpha_beta_values'] = current_state['alpha_beta_values'].copy()
            current_state['node_values'] = current_state['node_values'].copy()
            current_state['pruned_edges'] = current_state['pruned_edges'].copy()
        
        # Update state for current node visit
        current_state['step_count'] += 1
        current_state['current_node'] = node_id
        current_state['visited_nodes'].add(node_id)
        
        # Update alpha-beta values for internal nodes
        if self.tree[node_id][3] != 'leaf':
            current_state['alpha_beta_values'][node_id] = (alpha, beta)
        
        current_state['description'] = f'Step {current_state["step_count"]}: Visiting Node {node_id}'
        self.animation_states.append(current_state.copy())
        
        # Base case: leaf node
        if self.tree[node_id][3] == 'leaf':
            value = self.tree[node_id][2]
            current_state['node_values'][node_id] = value
            current_state['description'] = f'Step {current_state["step_count"]}: Leaf Node {node_id} = {value}'
            self.animation_states.append(current_state.copy())
            return value
        
        children = self.tree[node_id][1]
        
        if maximizing_player:
            max_eval = float('-inf')
            for i, child in enumerate(children):
                if use_pruning and (node_id, child) in current_state['pruned_edges']:
                    continue
                
                eval_score = self._run_algorithm_with_states(child, alpha, beta, False, use_pruning)
                max_eval = max(max_eval, eval_score)
                old_alpha = alpha
                alpha = max(alpha, eval_score)
                
                # Update current state after child evaluation
                if self.animation_states:
                    current_state = self.animation_states[-1].copy()
                    current_state['visited_nodes'] = current_state['visited_nodes'].copy()
                    current_state['alpha_beta_values'] = current_state['alpha_beta_values'].copy()
                    current_state['node_values'] = current_state['node_values'].copy()
                    current_state['pruned_edges'] = current_state['pruned_edges'].copy()
                
                current_state['alpha_beta_values'][node_id] = (alpha, beta)
                current_state['current_node'] = node_id
                
                if old_alpha != alpha:
                    current_state['description'] = f'Step {current_state["step_count"]}: Updated α={alpha} at Node {node_id}'
                    self.animation_states.append(current_state.copy())
                
                # Alpha-beta pruning check
                if use_pruning and beta <= alpha:
                    # Prune remaining children
                    remaining_children = children[i + 1:]
                    for remaining_child in remaining_children:
                        current_state['pruned_edges'].add((node_id, remaining_child))
                    
                    if remaining_children:
                        current_state['description'] = f'Step {current_state["step_count"]}: Pruning at Node {node_id} (β≤α: {beta}≤{alpha})'
                        self.animation_states.append(current_state.copy())
                    break
            
            current_state['node_values'][node_id] = max_eval
            current_state['result'] = max_eval
            return max_eval
            
        else:  # minimizing player
            min_eval = float('inf')
            for i, child in enumerate(children):
                if use_pruning and (node_id, child) in current_state['pruned_edges']:
                    continue
                
                eval_score = self._run_algorithm_with_states(child, alpha, beta, True, use_pruning)
                min_eval = min(min_eval, eval_score)
                old_beta = beta
                beta = min(beta, eval_score)
                
                # Update current state after child evaluation
                if self.animation_states:
                    current_state = self.animation_states[-1].copy()
                    current_state['visited_nodes'] = current_state['visited_nodes'].copy()
                    current_state['alpha_beta_values'] = current_state['alpha_beta_values'].copy()
                    current_state['node_values'] = current_state['node_values'].copy()
                    current_state['pruned_edges'] = current_state['pruned_edges'].copy()
                
                current_state['alpha_beta_values'][node_id] = (alpha, beta)
                current_state['current_node'] = node_id
                
                if old_beta != beta:
                    current_state['description'] = f'Step {current_state["step_count"]}: Updated β={beta} at Node {node_id}'
                    self.animation_states.append(current_state.copy())
                
                # Alpha-beta pruning check
                if use_pruning and beta <= alpha:
                    # Prune remaining children
                    remaining_children = children[i + 1:]
                    for remaining_child in remaining_children:
                        current_state['pruned_edges'].add((node_id, remaining_child))
                    
                    if remaining_children:
                        current_state['description'] = f'Step {current_state["step_count"]}: Pruning at Node {node_id} (β≤α: {beta}≤{alpha})'
                        self.animation_states.append(current_state.copy())
                    break
            
            current_state['node_values'][node_id] = min_eval
            return min_eval
    
    def draw_frame(self, frame_idx):
        """Draw a single frame of the animation"""
        self.ax.clear()
        
        if frame_idx >= len(self.animation_states):
            frame_idx = len(self.animation_states) - 1
            
        state = self.animation_states[frame_idx]
        
        # Set up the plot
        self.ax.set_xlim(-5, 5)
        self.ax.set_ylim(-0.5, 2.8)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        # Title with step description
        title = f"Alpha-Beta Pruning Visualization\n{state['description']}"
        self.ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Draw edges first
        for node_id, (parent, children, value, node_type) in self.tree.items():
            if parent is not None:
                is_pruned = (parent, node_id) in state['pruned_edges']
                edge_color = 'red' if is_pruned else 'black'
                edge_style = '--' if is_pruned else '-'
                line_width = 2 if not is_pruned else 3
                alpha_val = 0.7 if not is_pruned else 0.9
                
                self.ax.plot([self.pos[parent][0], self.pos[node_id][0]], 
                           [self.pos[parent][1], self.pos[node_id][1]], 
                           color=edge_color, linestyle=edge_style, 
                           linewidth=line_width, alpha=alpha_val)
                
                # Draw X for pruned edges
                if is_pruned:
                    mid_x = (self.pos[parent][0] + self.pos[node_id][0]) / 2
                    mid_y = (self.pos[parent][1] + self.pos[node_id][1]) / 2
                    self.ax.plot([mid_x-0.15, mid_x+0.15], [mid_y-0.15, mid_y+0.15], 'r', linewidth=4)
                    self.ax.plot([mid_x-0.15, mid_x+0.15], [mid_y+0.15, mid_y-0.15], 'r', linewidth=4)
        
        # Draw nodes
        for node_id, (parent, children, value, node_type) in self.tree.items():
            x, y = self.pos[node_id]
            
            # Determine node color with animation effects
            if node_id == state['current_node']:
                color = 'gold'  # Current node - bright gold
                edge_color = 'orange'
                edge_width = 3
            elif node_id in state['visited_nodes']:
                color = 'lightgreen'  # Visited nodes
                edge_color = 'darkgreen'
                edge_width = 2
            else:
                color = 'lightblue' if node_type != 'leaf' else 'lightcoral'
                edge_color = 'black'
                edge_width = 2
            
            # Draw node shapes with enhanced visuals
            if node_type == 'max':
                # Upward triangle
                triangle = Polygon([(x, y+0.25), (x-0.2, y-0.15), (x+0.2, y-0.15)], 
                                 closed=True, facecolor=color, edgecolor=edge_color, 
                                 linewidth=edge_width)
                self.ax.add_patch(triangle)
            elif node_type == 'min':
                # Downward triangle  
                triangle = Polygon([(x, y-0.25), (x-0.2, y+0.15), (x+0.2, y+0.15)], 
                                 closed=True, facecolor=color, edgecolor=edge_color, 
                                 linewidth=edge_width)
                self.ax.add_patch(triangle)
            else:  # leaf
                # Square
                square = Rectangle((x-0.2, y-0.2), 0.4, 0.4, 
                                 facecolor=color, edgecolor=edge_color, 
                                 linewidth=edge_width)
                self.ax.add_patch(square)
            
            # Add node labels
            if node_type == 'leaf':
                self.ax.text(x, y, str(value), ha='center', va='center', 
                           fontsize=14, fontweight='bold', color='darkred')
            else:
                # Show computed value if available
                if node_id in state['node_values']:
                    self.ax.text(x, y, str(state['node_values'][node_id]), 
                               ha='center', va='center', fontsize=14, fontweight='bold', color='darkblue')
                
                # Show alpha-beta values
                if node_id in state['alpha_beta_values']:
                    alpha, beta = state['alpha_beta_values'][node_id]
                    alpha_str = str(alpha) if alpha != float('-inf') else '-∞'
                    beta_str = str(beta) if beta != float('inf') else '+∞'
                    
                    # Alpha value (left side)
                    self.ax.text(x-0.4, y+0.4, f'α={alpha_str}', ha='center', va='center', 
                               fontsize=11, fontweight='bold',
                               bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcyan', 
                                        edgecolor='blue', alpha=0.9))
                    
                    # Beta value (right side)
                    self.ax.text(x+0.4, y+0.4, f'β={beta_str}', ha='center', va='center', 
                               fontsize=11, fontweight='bold',
                               bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow', 
                                        edgecolor='red', alpha=0.9))
        
        # Add enhanced legend
        legend_elements = [
            plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='lightblue', 
                      markersize=12, markeredgecolor='black', markeredgewidth=2, label='Max Node'),
            plt.Line2D([0], [0], marker='v', color='w', markerfacecolor='lightblue', 
                      markersize=12, markeredgecolor='black', markeredgewidth=2, label='Min Node'),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='lightcoral', 
                      markersize=12, markeredgecolor='black', markeredgewidth=2, label='Leaf Node'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gold', 
                      markersize=12, markeredgecolor='orange', markeredgewidth=2, label='Current Node'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgreen', 
                      markersize=12, markeredgecolor='darkgreen', markeredgewidth=2, label='Visited Node'),
            plt.Line2D([0], [0], color='red', linestyle='--', linewidth=3, label='Pruned Branch')
        ]
        
        self.ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1), 
                      fontsize=10, framealpha=0.9)
        
        # Add step counter
        step_text = f"Frame: {frame_idx + 1}/{len(self.animation_states)}"
        self.ax.text(0.02, 0.02, step_text, transform=self.ax.transAxes, 
                    fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    def animate_function(self, frame):
        """Animation function called by matplotlib animator"""
        self.draw_frame(frame)
        return []
    
    def create_animation(self, use_pruning=True, interval=2000, save_gif=False, filename='alpha_beta_animation.gif'):
        """Create and display the animation"""
        print(f"Generating animation states for {'Alpha-Beta Pruning' if use_pruning else 'Plain Minimax'}...")
        self.generate_animation_states(use_pruning)
        print(f"Generated {len(self.animation_states)} animation frames")
        
        # Create animation
        anim = animation.FuncAnimation(
            self.fig, 
            self.animate_function, 
            frames=len(self.animation_states),
            interval=interval,  # milliseconds between frames
            blit=False,
            repeat=True
        )
        
        if save_gif:
            print(f"Saving animation to {filename}...")
            writer = animation.PillowWriter(fps=1)
            anim.save(filename, writer=writer)
            print(f"Animation saved as {filename}")
        
        plt.tight_layout()
        plt.show()
        
        return anim
    
    def step_by_step_visualization(self, use_pruning=True):
        """Interactive step-by-step visualization"""
        self.generate_animation_states(use_pruning)
        current_frame = 0
        
        plt.ion()  # Interactive mode
        
        while True:
            self.draw_frame(current_frame)
            plt.draw()
            plt.pause(0.1)
            
            print(f"\nFrame {current_frame + 1}/{len(self.animation_states)}")
            print(f"Description: {self.animation_states[current_frame]['description']}")
            print("\nControls:")
            print("  n/Enter: Next frame")
            print("  p: Previous frame")
            print("  g: Go to specific frame")
            print("  a: Auto-play remaining frames")
            print("  q: Quit")
            
            user_input = input("Your choice: ").strip().lower()
            
            if user_input in ['n', '']:
                current_frame = min(current_frame + 1, len(self.animation_states) - 1)
            elif user_input == 'p':
                current_frame = max(current_frame - 1, 0)
            elif user_input == 'g':
                try:
                    target_frame = int(input(f"Enter frame number (1-{len(self.animation_states)}): ")) - 1
                    current_frame = max(0, min(target_frame, len(self.animation_states) - 1))
                except ValueError:
                    print("Invalid frame number")
            elif user_input == 'a':
                for i in range(current_frame, len(self.animation_states)):
                    self.draw_frame(i)
                    plt.draw()
                    plt.pause(2)
                break
            elif user_input == 'q':
                break
        
        plt.ioff()

def main():
    """Main function with enhanced options"""
    print("🎬 Alpha-Beta Pruning Animation Visualizer")
    print("=" * 50)
    
    animator = AlphaBetaAnimator()
    
    while True:
        print("\n🎯 Animation Options:")
        print("1. 🎭 Auto-play Animation (Alpha-Beta Pruning)")
        print("2. 🎪 Auto-play Animation (Plain Minimax)")
        print("3. 👆 Step-by-Step Interactive (Alpha-Beta)")
        print("4. 👆 Step-by-Step Interactive (Plain Minimax)")
        print("5. 💾 Save Animation as GIF (Alpha-Beta)")
        print("6. 💾 Save Animation as GIF (Plain Minimax)")
        print("7. 🚪 Exit")
        
        try:
            choice = input("\n🎮 Enter your choice (1-7): ").strip()
            
            if choice == '1':
                print("\n🎬 Starting Alpha-Beta Pruning Animation...")
                anim = animator.create_animation(use_pruning=True, interval=2500)
                input("\nPress Enter to continue...")
                
            elif choice == '2':
                print("\n🎬 Starting Plain Minimax Animation...")
                anim = animator.create_animation(use_pruning=False, interval=2500)
                input("\nPress Enter to continue...")
                
            elif choice == '3':
                print("\n👆 Starting Interactive Alpha-Beta Visualization...")
                animator.step_by_step_visualization(use_pruning=True)
                
            elif choice == '4':
                print("\n👆 Starting Interactive Plain Minimax Visualization...")
                animator.step_by_step_visualization(use_pruning=False)
                
            elif choice == '5':
                filename = input("Enter filename for GIF (default: alpha_beta.gif): ").strip()
                if not filename:
                    filename = "alpha_beta.gif"
                if not filename.endswith('.gif'):
                    filename += '.gif'
                animator.create_animation(use_pruning=True, interval=2500, save_gif=True, filename=filename)
                input("\nPress Enter to continue...")
                
            elif choice == '6':
                filename = input("Enter filename for GIF (default: plain_minimax.gif): ").strip()
                if not filename:
                    filename = "plain_minimax.gif"
                if not filename.endswith('.gif'):
                    filename += '.gif'
                animator.create_animation(use_pruning=False, interval=2500, save_gif=True, filename=filename)
                input("\nPress Enter to continue...")
                
            elif choice == '7':
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-7.")
                
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            import traceback
            traceback.print_exc()
    
    plt.close('all')
    print("🎬 Animation complete! Thank you for using the visualizer!")

if __name__ == "__main__":
    main()