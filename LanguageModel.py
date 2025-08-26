import numpy as np


class LanguageModel:
    def __init__(self, n, input_file, smoothing_k=1.0):
        self.vocab = set()
        self.counts = {}
        self.input_file = input_file
        if n < 1: 
            raise ValueError("n must be at least 1")
        self.n = n
        self.smoothing_k = smoothing_k


    def get_ngrams(self, tokens): 
        padded_tokens = ['<s>'] * (self.n - 1) + tokens + ['</s>']
        for i in range(len(padded_tokens) - self.n + 1):
            yield tuple(padded_tokens[i:i + self.n])

    def score(self, sentence): 
        tokens = sentence.split(' ')
        tokens = [token if token in self.vocab else '<unk>' for token in tokens]
        total_log_prob = 0.0
        for n_gram in self.get_ngrams(tokens): 
            n_gram_count = self.counts['ngrams'].get(n_gram, 0)
            context = n_gram[:-1]
            context_count = self.counts['contexts'].get(context, 0)
            vocab_size = len(self.vocab)
            prob = (n_gram_count + self.smoothing_k) / (context_count + self.smoothing_k * vocab_size)
            total_log_prob += np.log(prob)
        return total_log_prob

    def fit(self): 
        try: 
            with open(self.input_file, 'r', encoding='utf-8') as f:
                corpus = f.readlines()
                for sentence in corpus: 
                    tokens = sentence.split()
                    #add start, end, and unknown tokens to vocab
                    self.vocab.add('<s>')
                    self.vocab.add('</s>')
                    self.vocab.add('<unk>')
                    
                    n_gram_counts = {}
                    context_counts = {}
                    for n_gram in self.get_ngrams(tokens): 
                        n_gram_counts[n_gram] = n_gram_counts.get(n_gram, 0) + 1 
                        context = n_gram[:-1]
                        context_counts[context] = context_counts.get(context, 0) + 1
                    
                    self.counts['ngrams'] = n_gram_counts
                    self.counts['contexts'] = context_counts
        except Exception as e:
            print(f"Error occurred while fitting model: {e}")



