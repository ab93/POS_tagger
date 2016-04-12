__author__ = 'Avik'

import sys
import json
from hmmlearn import HiddenMarkovModel
import pprint
import time

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

def readTestData(filename,model):
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
            viterbi(line,model)
            #print count


def printDict(d):
    for key in d.keys():
        print key,":",d[key],'\n'


def setAllTags(model):
    for tag in model.tag_count:
        model.num_states.add(tag)
    model.num_states.add('start')

def viterbi(line,model):
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
                        currStates = model.num_states.copy()
                        #print "All:",model.num_states
                        currStates.remove('start')
                        break

            #print "currStates:"
            #print currStates
            #print model.num_states
            if len(currStates) == 0:
                currStates = model.num_states.copy()
                currStates.remove('start')

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

    writePredTags(line,finalTagging)

    #print finalTagging
    #print line
    #raw_input()

def writePredTags(line,finalTagging):
    with open('hmmoutput.txt','a+') as fp:
        s = ''
        for index,word in enumerate(line):
            s += word.decode('utf-8') + '/' + finalTagging[index].decode('utf-8') + ' '

        fp.write(s.encode('utf-8'))
        fp.write('\n')



def viterbiDecoder(line,model):
    probability = {}
    backpointer = {}
    finalStates = {}
    pp = pprint.PrettyPrinter(indent=2)

    for tag in model.transitions.keys():
        probability[tag] = {}
    probability.pop('start')

    '''
    pp.pprint(model.emissions)
    print '\n'
    pp.pprint(model.transitions)
    print '\n'
    pp.pprint(probability)
    raw_input()
    '''
    printDict(model.emissions)
    #raw_input()

    tagSet = set()
    for index,word in enumerate(line):
        backpointer[index+1] = {}
        word = word.decode('utf-8')
        if index == 0:
            #for tag in probability:

            for tag in model.transitions['start']:
                #print tag
                #print model.transitions['start'][tag]
                tagSet.add(tag)
                backpointer[1][tag] = 'start'
                try:
                    #probability[tag][word] = model.transitions['start'].get(tag,0) * model.emissions[word].get(tag,0)
                    probability[tag][index+1] = model.transitions['start'][tag] * model.emissions[word][tag]
                except:
                    probability[tag][index+1] = 0.0

            #pp.pprint(backpointer)
            #raw_input()

            continue

        #raw_input("word ended")
        impTags = tagSet.copy()
        tagSet.clear()
        #maxStateProb = -sys.maxint
        #maxState = None

        for tag in probability:
            #print "\nimpTags:",impTags
            max_prob = -sys.maxint
            max_back = -sys.maxint
            sel_tag = None

            for prev_tag in impTags:
                #print "word,prev_tag,tag:",word,prev_tag,tag
                #raw_input()
                try:
                    #prob = probability[prev_tag][line[index-1]] * model.transitions[prev_tag].get(tag,0) * model.emissions[word].get(tag,0)
                    prob = probability[prev_tag][index] * model.transitions[prev_tag].get(tag,0) * model.emissions[word][tag]
                    tagSet.add(tag)
                    back = model.transitions[prev_tag][tag] * model.emissions[word][tag]
                except:
                    #print word, prev_tag, tag, '\n', model.transitions[prev_tag]
                    #raw_input("except")
                    prob = 0.0
                    back = 0.0
                if max_back < back:
                    max_back = back
                    sel_tag = prev_tag
                if max_prob < prob:
                    max_prob = prob

                #probList.append(probability[prev_tag][line[index-1]] * model.transitions[prev_tag].get(tag,0) * model.emissions[word].get(tag,0))
                #tagList.append(prev_tag)
            #print tagSet
            #raw_input("after each tag")
            #print max_prob
            #print sel_tag
            #raw_input()
            backpointer[index+1][tag] = sel_tag
            probability[tag][index+1] = max_prob

            if index+1 == len(line):
                finalStates[max_prob] = tag


        print "backpointer:"
        printDict(backpointer)
        #pp.pprint(backpointer)
        '''
        print "probability:"
        pp.pprint(probability)
        print finalStates
        raw_input()
        '''

    max_prob= max(finalStates.keys(),key=float)
    finalState = finalStates[max_prob]
    print finalState

    finalTagging = [finalState]
    for index in range( (len(line)-1),0,-1 ):
        finalState = backpointer[index+1][finalState]
        finalTagging.insert(0,finalState)

    print finalTagging
    print line
    raw_input()


def main():
    startTime = time.time()
    transitions,word_tag,tag_count= readModel()
    model = HiddenMarkovModel(transitions,word_tag,tag_count)

    #pp = pprint.PrettyPrinter(indent=2)
    #pp.pprint(model.transitions)
    #raw_input()
    readTestData(sys.argv[1],model)
    print "TIME:",time.time()-startTime

if __name__ == '__main__':
    main()
