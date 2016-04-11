__author__ = 'Avik'

import sys
import json
import pprint

class HiddenMarkovModel:
    def __init__(self, transitions=None, word_tag=None, tag_count=None):
        self.transitions = transitions if transitions != None else {}
        self.emissions = {}
        self.word_tag = word_tag if word_tag != None else {}
        self.tag_count = tag_count if tag_count != None else {'start':0}
        self.tag_nextTag = {}
        self.eos_tag = {}

    def updateTagNextTag(self,line):
        for i in range(len(line)-1):
            tag = line[i][-2:]
            nextTag = line[i+1][-2:]
            if i == 0:
                if 'start' in self.tag_nextTag:
                    if tag in self.tag_nextTag['start']:
                        self.tag_nextTag['start'][tag] += 1
                    else:
                        self.tag_nextTag['start'][tag] = 1
                else:
                    self.tag_nextTag['start'] = {}
                    self.tag_nextTag['start'][tag] = 1

            if tag in self.tag_nextTag:
                if nextTag in self.tag_nextTag[tag]:
                    self.tag_nextTag[tag][nextTag] += 1
                else:
                    self.tag_nextTag[tag][nextTag] = 1
            else:
                self.tag_nextTag[tag] = {}
                self.tag_nextTag[tag][nextTag] = 1


    def updateTagCount(self,line):
        self.tag_count['start'] += 1
        for index,item in enumerate(line):
            tag = item[-2:]

            if tag in self.tag_count:
                self.tag_count[tag] += 1
            else:
                self.tag_count[tag] = 1

            if index == (len(line) - 1):
                if tag in self.eos_tag:
                    self.eos_tag[tag] += 1
                else:
                    self.eos_tag[tag] = 1

    def updateWordTag(self,line):
        for item in line:
            tag = item[-2:]
            word = item[:-3]

            if word in self.word_tag:
                if tag in self.word_tag[word]:
                    self.word_tag[word][tag] += 1
                else:
                    self.word_tag[word][tag] = 1
            else:
                self.word_tag[word] = {tag:1}

    def setTransitions(self):
        #self.display()
        for prev_tag in self.tag_nextTag.keys():
            self.transitions[prev_tag] = {}
            for tag in self.tag_nextTag[prev_tag].keys():
                #print prev_tag, tag, self.tag_nextTag[prev_tag][tag], self.tag_count[prev_tag], self.eos_tag.get(prev_tag,0)
                self.transitions[prev_tag][tag] = float(self.tag_nextTag[prev_tag][tag])/float(self.tag_count[prev_tag] - self.eos_tag.get(prev_tag,0))

        #print self.transitions


    def setEmissions(self,line):
        for word in line:
            #print "word:",word
            #raw_input()
            if word in self.word_tag:
                self.emissions[word] = {}
                for tag in self.word_tag[word]:
                    self.emissions[word][tag] = float(self.word_tag[word][tag])/float(self.tag_count[tag])
        #print self.emissions
        #pp = pprint.PrettyPrinter(indent=2)
        #pp.pprint(self.emissions)

    def display(self):
        pp = pprint.PrettyPrinter(indent=2)
        #pp.pprint(self.tag_nextTag)
        pp.pprint(self.transitions)
        raw_input()

def readData(filename,model):
    with open(filename,'r') as fp:
        count = 0
        for line in fp:
            line = line.strip().split(' ')
            model.updateTagNextTag(line)
            model.updateTagCount(line)
            model.updateWordTag(line)
            #print model.tag_nextTag,'\n'
            #print model.tag_count
            #print model.eos_tag
            #print model.word_tag
            count += 1
            print count
        #print model.tag_nextTag,'\n'
        #print model.eos_tag
        #print model.tag_count

    model.setTransitions()

def writeParameters(model):
    with open('hmmmodel.txt','w') as fp:
        json.dump(model.transitions,fp)
        fp.write('\n')
        json.dump(model.word_tag,fp)
        fp.write('\n')
        json.dump(model.tag_count,fp)

def main():
    HMM = HiddenMarkovModel()
    readData(sys.argv[1],HMM)
    writeParameters(HMM)

if __name__ == '__main__':
    main()
