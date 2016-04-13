__author__ = 'Avik'

import sys
import json
from hmmlearn import HiddenMarkovModel
import pprint
import time
from collections import Counter

topStates = set()

def readModel():
    with open('hmmmodel.txt','r') as jsonFile:
        data = []
        count = 0
        for line in jsonFile:
            count += 1
            #if count <= 3:
            data.append(json.loads(line))
            #else:
            #    data.append(line)

    return data

def readTestData(filename,model,f):
    with open(filename,'r') as fp:
        count = 0
        for line in fp:
            count += 1
            line = line.strip().split(' ')
            model.setEmissions(line)
            setAllTags(model)
            #printDict(model.emissions)
            #raw_input()
            #viterbiDecoder(line,model)
            viterbi(line,model,f)
            #print count


def printDict(d):
    for key in d.keys():
        print key,":",d[key],'\n'


def setAllTags(model):
    for tag in model.tag_count:
        model.num_states.add(tag)
    model.num_states.add('start')

def setTopStates(model):
    global topStates
    d = dict(Counter(model.tag_count).most_common(10))
    for key in d.keys():
        topStates.add(key)


def viterbi(line,model,f):
    global topStates

    probability = {}
    backpointer = {}
    finalStates = {}
    prevStates = set()

    for index,word in enumerate(line):
        backpointer[index+1] = {}
        word = word.decode('utf-8')

        if index == 0:
            for tag in model.transitions['start']:
                try:
                    model.emissions[word]
                    try:
                        if model.emissions[word][tag] != 0:
                            prevStates.add(tag)
                            probability[tag] = { 1: (model.transitions['start'][tag] * model.emissions[word][tag]) }
                            backpointer[index+1][tag] = 'start'
                    except:
                        {}
                except:
                    prevStates.add(tag)
                    probability[tag] = { 1: model.transitions['start'][tag] }
                    backpointer[index+1][tag] = 'start'

            #print "probability:"
            #printDict(probability)
            #print "prevStates:"
            #print prevStates
            #raw_input()

        else:
            for prev_tag in prevStates:
                currStates = set()
                for tag in model.transitions[prev_tag]:
                    try:
                        model.emissions[word]
                        try:
                            if model.emissions[word][tag] > 0:
                                currStates.add(tag)
                        except:
                            {}
                            #print currStates
                    except:
                        #currStates = model.num_states.copy()
                        currStates = topStates.copy()
                        #print "All:",model.num_states
                        #currStates.remove('start')
                        break

            #print "currStates:"
            #print currStates
            #print model.num_states
            if len(currStates) == 0:
                #currStates = model.num_states.copy()
                #currStates.remove('start')
                currStates = topStates.copy()

            for tag in currStates:
                max_prob = -sys.maxint
                max_back = -sys.maxint
                sel_tag = None

                for prev_tag in prevStates:
                    try:
                        model.emissions[word]
                        prob = probability[prev_tag][index] * model.transitions[prev_tag].get(tag,0) * model.emissions[word][tag]
                        back = probability[prev_tag][index] * model.transitions[prev_tag].get(tag,0)
                    except:
                        prob = probability[prev_tag][index] * model.transitions[prev_tag].get(tag,0)
                        back = probability[prev_tag][index] * model.transitions[prev_tag].get(tag,0)

                    if max_prob < prob:
                        max_prob = prob

                    if max_back < back:
                        max_back = back
                        sel_tag = prev_tag

                backpointer[index+1][tag] = sel_tag
                if tag in probability:
                    probability[tag][index+1] = max_prob
                else:
                    probability[tag] = {}
                    probability[tag][index+1] = max_prob

                if index+1 == len(line):
                    finalStates[max_prob] = tag

            #print currStates

            #print word
            #printDict(probability)
            #printDict(backpointer)
            #print "probability:"
            #print "prevStates:",prevStates
            #print "currStates:",currStates
            prevStates = currStates.copy()

    #print finalStates
    #printDict(probability)
    #raw_input()
    max_prob= max(finalStates.keys(),key=float)
    finalState = finalStates[max_prob]
    #print finalState

    finalTagging = [finalState]
    for index in range( (len(line)-1),0,-1 ):
        finalState = backpointer[index+1][finalState]
        finalTagging.insert(0,finalState)

    writePredTags(line,finalTagging,f)

    #print finalTagging
    #print line
    #raw_input()

def writePredTags(line,finalTagging,fp):
    #with open('hmmoutput.txt','a+') as fp:
    s = ''
    for index,word in enumerate(line):
        s += word.decode('utf-8') + '/' + finalTagging[index].decode('utf-8') + ' '

    fp.write(s.encode('utf-8'))
    fp.write('\n')


def main():
    startTime = time.time()
    transitions,word_tag,tag_count= readModel()
    model = HiddenMarkovModel(transitions,word_tag,tag_count)
    setTopStates(model)
    #pp = pprint.PrettyPrinter(indent=2)
    #pp.pprint(model.transitions)
    #raw_input()
    fp = open('hmmoutput.txt','w')
    readTestData(sys.argv[1],model,fp)
    print "TIME:",time.time()-startTime
    fp.close()

if __name__ == '__main__':
    main()
