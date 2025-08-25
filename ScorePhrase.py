
class PhraseTableElement: 
    def __init__(self, src_lang, tgt_lang, aligned_to_src, aligned_to_tgt, frequency, lexical_weight): 
        self.src_lang= src_lang
        self.tgt_lang= tgt_lang
        self.aligned_to_src = aligned_to_src
        self.aligned_to_tgt= aligned_to_tgt
        self.frequency = frequency
        self.lexical_weight = lexical_weight
        self.trans_prob = 0
    

#This is just for packaging convinience, easier to pass bunch of values to other methods
class PhraseAlignment: 
    def __init__(self):
        self.frequency=0
        self.tgt_lang=[]
        self.src_lang=[]
        self.src_alignment_info=[]
        self.tgt_alignment_info=[]
        self.lexical_weight =0
        

    def create(self,line): 
        parsed_line = line.strip().split(' ')
        split_pos=0
        initialize_flage=True
        for i in range(len(parsed_line)): 
            if parsed_line[i]=='|||':
                split_pos+=1
                i+=1
            
            if split_pos==0:
                self.src_lang.append(parsed_line[i])
            elif split_pos==1:
                self.tgt_lang.append(parsed_line[i])
            else:
                if initialize_flage: 
                    self.src_alignment_info = [[] for _ in range(len(self.src_lang))]
                    self.tgt_alignment_info = [[] for _ in range(len(self.tgt_lang))]
                    initialize_flage= False

                print(parsed_line[i])
                src_idx, tgt_idx = map(int,parsed_line[i].split('-'))
                print(src_idx, tgt_idx)
                self.src_alignment_info[src_idx].append(tgt_idx)
                self.tgt_alignment_info[tgt_idx].append(src_idx)

        
class ScorePhrase: 
    def __init__(self, phrase_table_file, lex_file, output_file):
        self.output_file_path = output_file
        self.phrase_table_file = phrase_table_file
        self.phrase_table_file_sorted=""
        self.lex_file = lex_file
        self.lex_table = {}  # stores the source->target = probability (word-word prob)
        self.phrase_table = [] #stores the PhraseTableElement which represents a src, tgt and their alignment in both direction
        self.merged_phrase_table = {} # stores the merged alignment for a given (source_phrase, target_phrase)
        self.src_phrase_count=1  #this stores the occurence of a source phrase 
        

    def loadLexicalTable(self):
        try:
            with open(self.lex_file, 'r', encoding='utf-8') as lex_file:
                lines = lex_file.readlines()
                if not lines:
                    raise ValueError("Lexical table file is empty!")
                for line in lines:
                    try:
                        tgt, src, prob = line.strip().split(' ')
                        try:
                            prob = float(prob)
                            if self.lex_table.get(src)==None: 
                                self.lex_table[src]={}
                            self.lex_table[src][tgt]=prob
                        except ValueError:
                            print(f"[WARN] prob is not a number in line: {line.strip()}, skipping...")
                            continue
             
                     
                    except ValueError:

                        print(f"[WARN] invalid line format: {line.strip()}, skipping...")
                        continue
                
                print(self.lex_table)

        except FileNotFoundError:
            print(f"[ERROR] File not found: {self.lex_file}")
            raise
        except PermissionError:
            print(f"[ERROR] No permission to read file: {self.lex_file}")
            raise
        except Exception as e:
            print(f"[ERROR] Unexpected error while reading {self.lex_file}: {e}")
            raise
    
    def sortPhraseTable(self):
        try: 
            with open(self.phrase_table_file,'r',encoding='utf-8') as phrase_table_file: 
                lines= phrase_table_file.readlines()
            
            lines.sort()

            with open(self.phrase_table_file + '.sorted','w',encoding='utf-8') as f: 
                f.writelines(lines)

            self.phrase_table_file_sorted = self.phrase_table_file + ".sorted"
        except FileNotFoundError: 
            raise

        return
    


    def generatePhraseTable(self,pa, last_line): 
        if last_line: 
            #this is to process the last phrase_table sitting in the memory which never gets the change to get processed
            for pt in self.phrase_table: 
                pt.trans_prob= pt.frequency/self.src_phrase_count
            self.saveToFile()
            return 
        else: 
            tmp_src_lang= " ".join(pa.src_lang)
            tmp_tgt_lang = " ".join(pa.tgt_lang)
            tmp_aligned_to_tgt = ""
            tmp_aligned_to_src = ""

            tmp_aligned_to_tgt = "".join("(" + ",".join(str(val) for val in e) + ") " for e in pa.tgt_alignment_info)
            tmp_aligned_to_src = "".join("(" + ",".join(str(val) for val in e) + ") " for e in pa.src_alignment_info)

            print(tmp_aligned_to_src)
            print(tmp_aligned_to_tgt)

            if(len(self.phrase_table)==0):
                self.src_phrase_count = 1
                self.phrase_table.append(PhraseTableElement(tmp_src_lang,tmp_tgt_lang, tmp_aligned_to_src, tmp_aligned_to_tgt, frequency=1, lexical_weight=pa.lexical_weight))
            else: 
                if self.phrase_table[-1].src_lang==tmp_src_lang and self.phrase_table[-1].tgt_lang==tmp_tgt_lang and self.phrase_table[-1].aligned_to_src==tmp_aligned_to_src and self.phrase_table[-1].aligned_to_tgt==tmp_aligned_to_tgt: 
                    self.phrase_table[-1].frequency +=1
                    self.src_phrase_count +=1
                elif self.phrase_table[-1].src_lang==tmp_src_lang: 
                    self.src_phrase_count+=1
                    self.phrase_table.append(PhraseTableElement(tmp_src_lang,tmp_tgt_lang, tmp_aligned_to_src, tmp_aligned_to_tgt, frequency=1, lexical_weight=pa.lexical_weight))
                else: 
                    #new source phrase

                    #calculate the translation Probability P(t_phrase | s_phrase) = count(s,t) / count(s)
                    for pt in self.phrase_table: 
                        pt.trans_prob= pt.frequency/self.src_phrase_count
                    
                    self.saveToFile()
                    self.phrase_table=[]
                    self.src_phrase_count=1
                    self.phrase_table.append(PhraseTableElement(tmp_src_lang,tmp_tgt_lang, tmp_aligned_to_src, tmp_aligned_to_tgt, frequency=1, lexical_weight=pa.lexical_weight))
        
        return
    
    def mergeAlignedInfo(aligned_str1, aligned_str2):
        """
        Merge two alignment strings by combining numbers in corresponding parentheses groups.
        
        Example:
            aligned_str1 = "(0,1) (2)"
            aligned_str2 = "(2,3) (2,4)" 
            Result: "(0,1,2,3) (2,4)"
        """
        print("merge called")
        if aligned_str1 == aligned_str2:
            return aligned_str2
        
        firstStart = 0
        secondStart = 0
        aligned_info_list = []

        while True:
            # Find opening parentheses
            firstStart = aligned_str1.find("(", firstStart)
            secondStart = aligned_str2.find("(", secondStart)
            
            if firstStart == -1 or secondStart == -1:
                break
                
            # Find closing parentheses AFTER the opening ones
            firstEnd = aligned_str1.find(")", firstStart)  # Start search from firstStart, not firstEnd!
            secondEnd = aligned_str2.find(")", secondStart)  # Start search from secondStart, not secondEnd!
            
            if firstEnd == -1 or secondEnd == -1:
                break

            # Extract content between parentheses
            tmp_first_aligned_info = aligned_str1[firstStart + 1:firstEnd]
            tmp_second_aligned_info = aligned_str2[secondStart + 1:secondEnd]
            
            unique_tokens = set()
            
            # Handle empty groups gracefully
            if tmp_first_aligned_info.strip():
                unique_tokens.update(map(int, tmp_first_aligned_info.split(',')))
            if tmp_second_aligned_info.strip():
                unique_tokens.update(map(int, tmp_second_aligned_info.split(',')))

            aligned_info_list.append(unique_tokens)

            # Move to next positions
            firstStart = firstEnd + 1
            secondStart = secondEnd + 1

        return " ".join("(" + ",".join(map(str, sorted(a))) + ")" for a in aligned_info_list)

      

    def saveToFile(self): 
        for pt in self.phrase_table: 
            if (pt.src_lang, pt.tgt_lang) not in self.merged_phrase_table: 
                self.merged_phrase_table[(pt.src_lang, pt.tgt_lang)] = pt
            else: 
                pt_other = self.merged_phrase_table[(pt.src_lang, pt.tgt_lang)]
                pt_other.frequency += pt.frequency

                if pt.trans_prob > pt_other.trans_prob:
                    pt_other.trans_prob = pt.trans_prob
                    pt_other.lexical_weight = pt.lexical_weight
                
                pt_other.aligned_to_src= self.mergeAlignedInfo(pt_other.aligned_to_src, pt.aligned_to_src)   
                pt_other.aligned_to_tgt = self.mergeAlignedInfo(pt_other.aligned_to_tgt, pt.aligned_to_tgt)

        with open(self.output_file_path, 'a', encoding='utf-8') as o_file: 
            for key, val in self.merged_phrase_table.items():
                o_file.write(f"{val.src_lang} ||| {val.tgt_lang} ||| {val.aligned_to_src} ||| {val.aligned_to_tgt} ||| {val.trans_prob} ||| {val.lexical_weight}\n")

        return


    def readPhraseFile(self):
        try: 
            with open(self.phrase_table_file_sorted, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines: 
                    pa=PhraseAlignment()
                    pa.create(line)
                    self.calculateLexicalWeight(pa)
                    self.generatePhraseTable(pa, False)
                #this is just for a placeholder
                pa= PhraseAlignment()
                #process the last orphaned line
                self.generatePhraseTable(pa, True)

        except FileNotFoundError: 
            raise
        except PermissionError: 
            raise 

    def calculateLexicalWeight(self, pa):

        # p(tgt_phrase|src_phrase) = product( sum( p_word(t|s) ) / count(s | s aligned with t) )

        lexical_weight = 1

        tgt_idx=0
        tgt_aligned_len= 1
        for a in pa.tgt_alignment_info: 
            weight = 0
            if len(a)==0: 
                #TODO ADD NULL EDGE-CASE HANDLING
                continue
            else:
                tgt_aligned_len = len(a)
                for src_idx in a: 
                    src_word= pa.src_lang[src_idx]
                    tgt_word= pa.tgt_lang[tgt_idx]
                    if src_word in self.lex_table and tgt_word in self.lex_table[src_word]:
                        weight += self.lex_table[src_word][tgt_word]
            
            weight /= tgt_aligned_len

            lexical_weight*=weight
            
            tgt_idx+=1
        
        pa.lexical_weight= lexical_weight
        return 
                


    def run(self):
        try:
            self.sortPhraseTable()
            self.loadLexicalTable()
            self.readPhraseFile()
        
        except Exception as e:
            print(f"[FATAL] Error → {e}")
