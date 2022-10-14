from matplotlib import pyplot as plt

def getTypingScores(filename):
    scores = []
    with open(filename, mode = "r") as read_file:
        lines = read_file.readlines()
        for line in lines:
            line = line.split(",")
            score = int(line[1].split(":")[1])
            scores.append(score)
        read_file.close()
    return scores


def graphTypingScores(filename):
    scores = getTypingScores(filename)
    x_vals = [i for i in range(1,len(scores)+1)]

    plt.title("Typing Scores Over Time")
    plt.ylabel("Typing Score")
    
    plt.plot(x_vals,scores)
    plt.show()

    plt.scatter(x_vals,scores)
    plt.show()

filename = "scores.txt"

if __name__ == "__main__":
    graphTypingScores(filename)
