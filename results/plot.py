import plotly.graph_objects as go

PLOTLY_AVAILABLE = True
try:
    import plotly.graph_objects as go
except ImportError:
    PLOTLY_AVAILABLE = False


def plot_interactive_student_scores(all_results):
    """
    Create an interactive visualization showing final scores with component breakdown.
    Hover over any student to see their individual component scores.
    
    Args:
        all_results: {student_id: {scores: {component: score}, ...}}
    """
    if not PLOTLY_AVAILABLE:
        print(" Plotly not installed. Install with: pip install plotly")
        return
    
    # Prepare data
    students = []
    final_scores = []
    structure_scores = []
    syntax_scores = []
    test_scores = []
    originality_scores = []
    colors = []
    
    for student_id, result in all_results.items():
        if "scores" in result:
            students.append(student_id)
            final_scores.append(result["final_score"])
            structure_scores.append(result["scores"].get("structure", 0))
            syntax_scores.append(result["scores"].get("syntax", 0))
            test_scores.append(result["scores"].get("test_cases", 0))
            originality_scores.append(result["scores"].get("originality", 0))
            
            # Color coding
            if result["final_score"] >= 75:
                colors.append("green")
            elif result["final_score"] >= 50:
                colors.append("orange")
            else:
                colors.append("red")
    
    # Sort by final score
    sorted_indices = sorted(range(len(final_scores)), key=lambda i: final_scores[i], reverse=True)
    students = [students[i] for i in sorted_indices]
    final_scores = [final_scores[i] for i in sorted_indices]
    structure_scores = [structure_scores[i] for i in sorted_indices]
    syntax_scores = [syntax_scores[i] for i in sorted_indices]
    test_scores = [test_scores[i] for i in sorted_indices]
    originality_scores = [originality_scores[i] for i in sorted_indices]
    colors = [colors[i] for i in sorted_indices]
    
    # Create custom hover text with component breakdown
    hover_text = []
    for i in range(len(students)):
        text = (f"<b>{students[i]}</b><br><br>"
                f"<b>Component Scores:</b><br>"
                f"Structure: {structure_scores[i]:.2f}%<br>"
                f"Syntax: {syntax_scores[i]:.2f}%<br>"
                f"Test Cases: {test_scores[i]:.2f}%<br>"
                f"Originality: {originality_scores[i]:.2f}%<br><br>"
                f"<b>Final Score: {final_scores[i]:.2f}%</b>")
        hover_text.append(text)
    
    # Create main figure with final scores
    fig = go.Figure()
    
    # Add bars for final scores
    fig.add_trace(go.Bar(
        x=students,
        y=final_scores,
        marker=dict(
            color=colors,
            line=dict(color="black", width=1)
        ),
        text=[f"{score:.1f}%" for score in final_scores],
        textposition="auto",
        hovertext=hover_text,
        hoverinfo="text",
        name="Final Score",
        showlegend=False
    ))
    
    # Add threshold lines
    fig.add_hline(y=75, line_dash="dash", line_color="green", 
                  annotation_text="Good (75%)", annotation_position="right")
    fig.add_hline(y=50, line_dash="dash", line_color="orange",
                  annotation_text="Average (50%)", annotation_position="right")
    
    # Update layout
    fig.update_layout(
        title={
            'text': " Final Scores - All Students (Hover for Component Breakdown)",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title="Student ID",
        yaxis_title="Score (%)",
        height=600,
        width=1400,
        hovermode="closest",
        plot_bgcolor="rgba(240,240,240,0.5)",
        paper_bgcolor="white",
        font=dict(size=11),
        margin=dict(b=150)
    )
    
    fig.update_xaxes(tickangle=-45)
    fig.update_yaxes(range=[0, 105])
    
    # Show the figure
    fig.show()
    
    # Save as HTML with proper structure
    html_content = fig.to_html()
    html_doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Assessment Results - Final Scores</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Student Assessment Results - Final Scores</h1>
        {html_content}
    </div>
</body>
</html>'''
    
    with open("results/final_scores_interactive.html", "w", encoding="utf-8") as f:
        f.write(html_doc)
    
    print(" Interactive visualization saved to: results/final_scores_interactive.html")
