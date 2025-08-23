
class PhrasePair: 
    def __init__(self, source_start, source_end, target_start, target_end):
        self.source_start= source_start
        self.source_end = source_end
        self.target_start = target_start
        self.target_end = target_end


class PhraseExtractor:
    def __init__(self,src_file, tgt_file, align_file, output_file):
        self.src_file_path= src_file
        self.tgt_file_path= tgt_file
        self.align_file_path= align_file
        self.output_file_path = output_file
        self.src_lang = [] 
        self.tgt_lang = [] 
        #stores src->tgt word mapping
        self.src_tgt_align_info = [] 
        #stores tgt->src word mapping
        self.tgt_src_align_info = []

        

    def createWordAlignment(self,src_line, tgt_line, align_line):
        self.src_lang = src_line.split(" ")
        self.tgt_lang = tgt_line.split(" ")

        self.src_tgt_align_info = [set() for _ in range(len(self.src_lang))]
        self.tgt_src_align_info = [set() for _ in range(len(self.tgt_lang))]

        align_tokens = align_line.split(" ")
        for align_token in align_tokens:
            try:
                src_word_idx, tgt_word_idx = map(int, align_token.split('-'))
                self.src_tgt_align_info[src_word_idx].add(tgt_word_idx)
                self.tgt_src_align_info[tgt_word_idx].add(src_word_idx)
            except ValueError: 
                print("invalid alignment format")

        return True
    

    def validatePhrase(self, phrase_pair): 
        if phrase_pair.source_start > phrase_pair.source_end: 
            print("invalid_phrase")
            return False 
        for i in range(phrase_pair.source_start, phrase_pair.source_end + 1): 
            for aligned_tgt_idx in self.src_tgt_align_info[i]: 
                if(aligned_tgt_idx < phrase_pair.target_start  or aligned_tgt_idx > phrase_pair.target_end): 
                    print("invaid phrase")
                    return False
        
        #TRY EXPAND THE SOURCE PHRASE ---> NEED AN EXAMPLE TO UNDERSTAND IT COMPLETELY
        return True  
        
    
    def addPhraseToFile(self, phrase_pair): 
        output_file_path_inv= self.output_file_path + ".inv"
        with  open(self.output_file_path, "a", encoding='utf-8') as o_file, open(output_file_path_inv, "a", encoding='utf-8') as o_file_inv: 
 
            temp_tgt_lang = " ".join(self.tgt_lang[phrase_pair.target_start:phrase_pair.target_end + 1])
            temp_src_lang = " ".join(self.src_lang[phrase_pair.source_start:phrase_pair.source_end + 1])

            local_aligned_info = []
            for i in range(phrase_pair.target_start, phrase_pair.target_end + 1): 
                for j in self.tgt_src_align_info[i]: 
                    local_aligned_info.append((i - phrase_pair.target_start, j - phrase_pair.source_start))


            o_file.write(f"{temp_src_lang} ||| {temp_tgt_lang} |||")
            o_file_inv.write(f"{temp_tgt_lang} ||| {temp_src_lang} |||")
            for tgt, src in local_aligned_info: 
                o_file.write(f" {src}-{tgt}")
                o_file_inv.write(f" {tgt}-{src}")
            
            o_file.write("\n")
            o_file_inv.write("\n")

            

    def extractPhrasePair(self):
        #sliding window
        tgt_lang_size = len(self.tgt_lang)
        for phrase_len in range(1, tgt_lang_size + 1):
            for start in range(0, tgt_lang_size - phrase_len + 1): 
                end = start + phrase_len-1

                source_start = len(self.src_lang)
                source_end = 0
                #iterate over a phrase of the target language
                for i in range(start,end+1): 
                    for aligned_src_idx in self.tgt_src_align_info[i]:
                        source_start = aligned_src_idx if aligned_src_idx < source_start else source_start
                        source_end = aligned_src_idx if aligned_src_idx > source_end else source_end

                pair= PhrasePair(source_start, source_end, target_start=start, target_end=end)
                is_valid_phrase_pair= self.validatePhrase(pair)
                if is_valid_phrase_pair: 
                    self.addPhraseToFile(pair)
    
    def run(self):
        with open(self.src_file_path,"r", encoding='utf-8') as i_src_file, open(self.tgt_file_path,"r", encoding='utf-8') as i_tgt_file, open(self.align_file_path, encoding='utf-8') as i_align_file :
            for src_line, tgt_line, align_line in zip(i_src_file, i_tgt_file, i_align_file):
                src_line = src_line.strip()
                tgt_line = tgt_line.strip()
                align_line = align_line.strip()
                if self.createWordAlignment(src_line,tgt_line, align_line):
                    self.extractPhrasePair()
                else: 
                    print("extraction failed")


        