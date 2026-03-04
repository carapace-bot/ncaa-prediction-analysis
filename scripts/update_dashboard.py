#!/usr/bin/env python3
"""
Update GitHub Pages dashboard with latest analysis results
Run this after analysis.py to publish new data to the web dashboard
"""

import json
import os
from datetime import datetime

def update_dashboard(analysis_output_path, dashboard_data_path):
    """
    Read latest analysis output and update docs/data.json for GitHub Pages
    """
    try:
        # Read the latest analysis output
        with open(analysis_output_path, 'r') as f:
            analysis = json.load(f)
        
        # Extract team projections
        teams = []
        for team_name, team_data in analysis.get('projections', {}).items():
            teams.append({
                'name': team_name,
                'probability': team_data.get('championship_probability', 0),
                'rating': team_data.get('rating', 0)
            })
        
        # Sort by probability descending
        teams.sort(key=lambda x: x['probability'], reverse=True)
        
        # Build dashboard data
        dashboard_data = {
            'teams': teams[:50],  # Top 50 teams
            'metadata': {
                'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
                'simulations': 10000,
                'teams_analyzed': len(teams)
            }
        }
        
        # Write to docs/data.json
        os.makedirs(os.path.dirname(dashboard_data_path), exist_ok=True)
        with open(dashboard_data_path, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        
        print(f"✓ Updated dashboard: {dashboard_data_path}")
        print(f"  Teams: {len(teams)}, Top favorite: {teams[0]['name']} at {teams[0]['probability']*100:.2f}%")
        return True
        
    except Exception as e:
        print(f"✗ Error updating dashboard: {e}")
        return False

if __name__ == '__main__':
    import sys
    
    # Default paths
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    analysis_output = os.path.join(repo_root, 'output', 'analysis.json')
    dashboard_data = os.path.join(repo_root, 'docs', 'data.json')
    
    # Allow override via command line
    if len(sys.argv) > 1:
        analysis_output = sys.argv[1]
    if len(sys.argv) > 2:
        dashboard_data = sys.argv[2]
    
    update_dashboard(analysis_output, dashboard_data)
