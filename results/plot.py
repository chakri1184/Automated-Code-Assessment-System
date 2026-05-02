import matplotlib.pyplot as plt

def plot_scores(scores_dict):
    names = list(scores_dict.keys())
    values = list(scores_dict.values())

    plt.figure()
    plt.bar(names, values)
    plt.title("Score Distribution")
    plt.xlabel("Metrics")
    plt.ylabel("Score")
    plt.show()


def plot_multiple_students(student_scores):
    names = list(student_scores.keys())
    scores = list(student_scores.values())

    plt.figure()
    plt.bar(names, scores)
    plt.title("Final Scores of Students")
    plt.xlabel("Students")
    plt.ylabel("Final Score")
    plt.xticks(rotation=45)
    plt.show()