import sys
from collections import defaultdict
import math
import random
import os
import os.path
"""
COMS W4705 - Natural Language Processing
Homework 1 - Programming Component: Trigram Language Models
Yassine Benajiba
"""

def corpus_reader(corpusfile, lexicon=None): 
    with open(corpusfile,'r') as corpus:
        for line in corpus:
            if line.strip():
                sequence = line.lower().strip().split()
                if lexicon:
                    yield [word if word in lexicon else "UNK" for word in sequence]
                else:
                    yield sequence

def get_lexicon(corpus):
    word_counts = defaultdict(int)
    for sentence in corpus:
        for word in sentence: 
            word_counts[word] += 1
    return set(word for word in word_counts if word_counts[word] > 1)  



def get_ngrams(sequence, n):
    a,b=['START']*(n-1) if n!=1 else ['START'],['STOP']
    sequence = a + sequence + b
    list = []
    for i in range(len(sequence) - n + 1):
        curr, words = 0, []
        while curr < n:
            if i + curr >= len(sequence):
                break
            words.append(sequence[i + curr])
            curr += 1
        list.append(tuple(words))
    return list


class TrigramModel(object):
    
    def __init__(self, corpusfile):
    
        # Iterate through the corpus once to build a lexicon 
        generator = corpus_reader(corpusfile)
        self.lexicon = get_lexicon(generator)
        self.lexicon.add("UNK")
        self.lexicon.add("START")
        self.lexicon.add("STOP")
    
        # Now iterate through the corpus again and count ngrams
        generator = corpus_reader(corpusfile, self.lexicon)
        self.count_ngrams(generator)
        self.total=sum(self.unigramcounts.values())

    def count_ngrams(self, corpus):
        self.unigramcounts = defaultdict(int)
        self.bigramcounts = defaultdict(int)
        self.trigramcounts = defaultdict(int)
        for sentence in corpus:
            for item in get_ngrams(sentence,1):
                    self.unigramcounts[item]+=1
            for item in get_ngrams(sentence,2):
                    self.bigramcounts[item]+=1
            for item in get_ngrams(sentence,3):
                    self.trigramcounts[item]+=1
        return

    def raw_trigram_probability(self,trigram):
        """
        COMPLETE THIS METHOD (PART 3)
        Returns the raw (unsmoothed) trigram probability
        """
        if self.bigramcounts[trigram[:2]]==0:
            return 0
        else:
            return self.trigramcounts[trigram] / self.bigramcounts[trigram[:2]]

    def raw_bigram_probability(self, bigram):
        """
        COMPLETE THIS METHOD (PART 3)
        Returns the raw (unsmoothed) bigram probability
        """
        if self.unigramcounts[bigram[:1]]==0:
            return 0
        else:
            return self.bigramcounts[bigram] / self.unigramcounts[bigram[:1]]


    
    def raw_unigram_probability(self, unigram):

        #hint: recomputing the denominator every time the method is called
        # can be slow! You might want to compute the total number of words once, 
        # store in the TrigramModel instance, and then re-use it.  
        return self.unigramcounts[unigram]/self.total

    def generate_sentence(self,t=20): 
        """
        COMPLETE THIS METHOD (OPTIONAL)
        Generate a random sentence from the trigram model. t specifies the
        max length, but the sentence may be shorter if STOP is reached.
        """
        return result            

    def smoothed_trigram_probability(self, trigram):
        """
        COMPLETE THIS METHOD (PART 4)
        Returns the smoothed trigram probability (using linear interpolation). 
        """
        lambda1 = 1/3.0
        lambda2 = 1/3.0
        lambda3 = 1/3.0
        result=lambda1*self.raw_trigram_probability(trigram)+lambda2*self.raw_bigram_probability(trigram[1:])+\
               lambda3*self.raw_unigram_probability(trigram[2:])
        if result<0:
            return 0
        else:
            return result
        
    def sentence_logprob(self, sentence):
        """
        COMPLETE THIS METHOD (PART 5)
        Returns the log probability of an entire sequence.
        """
        result=0.0
        for item in get_ngrams(sentence,3):
            if self.smoothed_trigram_probability(item)>0:
                result+=math.log2(self.smoothed_trigram_probability(item))
        return result

    def perplexity(self, corpus):
        M = 0.0
        result=0
        for sentence in corpus:
            M+=len(sentence)+3
            result+=self.sentence_logprob(sentence)
        l=result / M
        return 2**(-l)


def essay_scoring_experiment(training_file1, training_file2, testdir1, testdir2):

        model1 = TrigramModel(training_file1)
        model2 = TrigramModel(training_file2)

        total = 0
        correct = 0       
 
        for f in os.listdir(testdir1):
            pp = model1.perplexity(corpus_reader(os.path.join(testdir1, f), model1.lexicon))
            p_train=model2.perplexity(corpus_reader(os.path.join(testdir1,f),model2.lexicon))
            if p_train>pp:
                correct+=1
            total+=1

        for f in os.listdir(testdir2):
            pp = model1.perplexity(corpus_reader(os.path.join(testdir2, f), model1.lexicon))
            p_train=model2.perplexity(corpus_reader(os.path.join(testdir2,f),model2.lexicon))
            if p_train<pp:
                correct+=1
            total+=1
        
        return correct/total

if __name__ == "__main__":
    model=TrigramModel("hw1_data/brown_train.txt")
    generator = corpus_reader("hw1_data/brown_train.txt",model.lexicon)
    print(model.bigramcounts[('START', 'the')])
    print(model.trigramcounts[('START','START','the')])
    print(model.unigramcounts[('the',)])
    dev_corpus = corpus_reader("hw1_data/brown_train.txt", model.lexicon)
    pp = model.perplexity(dev_corpus)
    print(pp)
    dev_corpus = corpus_reader("hw1_data/brown_test.txt", model.lexicon)
    pp = model.perplexity(dev_corpus)
    print(pp)
    # Essay scoring experiment:
    acc = essay_scoring_experiment('hw1_data/ets_toefl_data/train_high.txt', 'hw1_data/ets_toefl_data/train_low.txt', "hw1_data/ets_toefl_data/test_high", "hw1_data/ets_toefl_data/test_low")
    print(acc)




