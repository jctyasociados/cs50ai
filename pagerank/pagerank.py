import os
import random
import re
import sys
from math import isclose

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    probability_dist = {}

    if corpus[page]:
        for link in corpus:
            probability_dist[link] = (1-damping_factor) / len(corpus)
            if link in corpus[page]:
                probability_dist[link] += damping_factor / len(corpus[page])
    else:
        # If there is no links from the page we chose one at random
        for link in corpus:
            probability_dist[link] = 1 / len(corpus)

    return probability_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    # Dictionary to store pagerank
    pagerank = {}

    # Choosing page at random
    sample = random.choice(list(corpus))

    # Iterate over the samples
    for i in range(n - 1):
        # Create a New Transition Model with it's probabilities
        model = transition_model(corpus, sample, damping_factor)
        population, weights = zip(*model.items())
        # Chose a random page given the probabilities of the Transition Model Created Before
        sample = random.choices(population, weights=weights, k=1)[0]

        # If the sample is surfed increment pagerank else add one to pagerank
        if sample in pagerank:
            pagerank[sample] += 1
        else:
            pagerank[sample] = 1

    # Number of times the surfer is on a page over the samples
    for page in pagerank:
        pagerank[page] = pagerank[page] / n

    return pagerank

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = {}
    new_pagerank = {}

    # Assign initial values for pagerank
    for page in corpus:
        pagerank[page] = 1 / len(corpus)

    repeat = True

    while repeat:
        # Calculate new rank values based on all of the current rank values
        for page in pagerank:
            total = float(0)

            for possible_page in corpus:
                # Show the pages that link to current page
                if page in corpus[possible_page]:
                    total += pagerank[possible_page] / len(corpus[possible_page])
                # If a page has no links we supose has links from all pages
                if not corpus[possible_page]:
                    total += pagerank[possible_page] / len(corpus)

            new_pagerank[page] = (1 - damping_factor) / len(corpus) + damping_factor * total

        repeat = False

        # if the value of pagerank is far from threshold repeat the process
        for page in pagerank:
            if not isclose(new_pagerank[page], pagerank[page], rel_tol = 1e-09, abs_tol = 0.001):
                repeat = True
            # Assign new values to current values
            pagerank[page] = new_pagerank[page]

    return pagerank


if __name__ == "__main__":
    main()
