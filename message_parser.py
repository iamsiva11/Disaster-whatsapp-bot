import nltk
import word2number
from word2number import w2n
from nltk.corpus import wordnet
from nltk.corpus import wordnet as wn

def get_integer(str):
  try:
    l = int(str)
    return l
  except:
    l = w2n.word_to_num(str)
    return l
    
def get_message(message_parser):
  message_split =  message_parser.split("|")
  mobile_number = message_split[0]
  need_synonyms = ["require", "want", "motivation", "motive", "ask", "call for", "demand", "involve", "necessitate", "need", "postulate", "take", "indigence", "pauperism", "pauperization", "penury"]
  supply_synonyms = ["issue", "furnish", "provide", "render", "add", "append", "cater", "ply", "provision", "supplying", "afford", "yield", "commit", "consecrate", "dedicate", "devote", "spring", "springiness", "impart", "leave", "pass on", "ease up", "give way", "move over", "render", "feed", "generate", "return", "throw", "chip in", "contribute", "kick in", "grant", "pay", "break", "cave in", "collapse", "fall in", "founder", "hand", "pass", "reach", "turn over", "have", "hold", "make", "establish", "open", "apply", "gift", "present", "sacrifice"]
  tokens = nltk.word_tokenize(message_split[1])
  need = len(set(tokens) & set(need_synonyms)) > 0
  need_json = {"need": True} if need else {"supply": True}
  need_json.update({"number": mobile_number})
  tagged_tokens = nltk.pos_tag(tokens)
  for i in range(len(tagged_tokens)):
    if tagged_tokens[i][1] == 'CD':
      current_count = get_integer(tagged_tokens[i][0])
    elif  tagged_tokens[i][1] == 'DT':
      current_count = 1
    elif  tagged_tokens[i][1] in ['NNS','NN']:
      if tagged_tokens[i][0] in ["cups", "cup", "packets","packet","bottle", "bottles", "bundle","bundles","packages", "package", need_synonyms, supply_synonyms]:
          continue
      current_category = tagged_tokens[i][0]
      c = wn.synsets(current_category)
      food = wn.synset('food.n.01')
      water = wn.synset('water.n.01')
      food = food.wup_similarity(c[0])
      water = water.wup_similarity(c[0])
      current_category = "food" if food > water else "water"
      print current_count
      try :
        current_count = current_count
      except NameError:
        current_count =1 
      if current_count == None:
        current_count =1
      need_json.update({current_category: current_count})
      current_count = None
  return need_json
