__author__ = 'Avik'

import sys
import json
from hmmlearn import HiddenMarkovModel
import pprint

def readModel():
    with open('hmmmodel.txt','r') as jsonFile:
        data = []
        for line in jsonFile:
            data.append(json.loads(line))

    return data

def readTestData(filename,model):
    with open(filename,'r') as fp:
        count = 0
        for line in fp:
            line = line.strip().split(' ')
            model.setEmissions(line)
            viterbiDecoder(line,model)
            count += 1
            print count


def viterbiDecoder(line,model):
    probability = {}
    pp = pprint.PrettyPrinter(indent=2)

    for tag in model.transitions.keys():
        probability[tag] = {}
    probability.pop('start')

    pp.pprint(model.emissions)
    print '\n'
    pp.pprint(model.transitions)
    print '\n'
    #pp.pprint(probability)
    #raw_input()



    for index,word in enumerate(line):
        if index == 0:
            for tag in probability:
                #print tag
                #print model.transitions['start'][tag]
                try:
                    #probability[tag][word] = model.transitions['start'].get(tag,0) * model.emissions[word].get(tag,0)
                    probability[tag][word] = model.transitions['start'][tag] * model.emissions[word][tag]
                except:
                    probability[tag][word] = 0.0

            pp.pprint(probability)
            raw_input()
            continue

        for tag in probability:
            #probList = []
            #tagList = []
            max_prob = -sys.maxint
            sel_tag = None
            for prev_tag in probability:
                #print word
                try:
                    #prob = probability[prev_tag][line[index-1]] * model.transitions[prev_tag].get(tag,0) * model.emissions[word].get(tag,0)
                    prob = probability[prev_tag][line[index-1]] * model.transitions[prev_tag][tag] * model.emissions[word][tag]
                except:
                    prob = 0.0
                if max_prob < prob:
                    max_prob = prob
                    sel_tag = prev_tag
                #probList.append(probability[prev_tag][line[index-1]] * model.transitions[prev_tag].get(tag,0) * model.emissions[word].get(tag,0))
                #tagList.append(prev_tag)
            #print max_prob
            #print sel_tag
            #raw_input()
            probability[tag][word] = max_prob


        #print "probability:"
        #pp.pprint(probability)
        #raw_input()


def main():
    transitions,word_tag,tag_count = readModel()
    model = HiddenMarkovModel(transitions,word_tag,tag_count)

    #pp = pprint.PrettyPrinter(indent=2)
    #pp.pprint(model.transitions)
    #raw_input()

    readTestData(sys.argv[1],model)

if __name__ == '__main__':
    main()
